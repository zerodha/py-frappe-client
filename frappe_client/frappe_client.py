import json
import atexit

import requests

from .frappe_exceptions import GeneralException, MissingConfigException


class FrappeRequest(object):
    """Class representation of FrappeRequest object

    Attributes:
            url: URL of Frappe site.
            usr (str): Username to Frappe Login.
            pwd (str): Password to Frappe Login.
            session_data (dict): dict of session object cookie data.
            api_key(str): Api key for token based auth.
            api_secret(str): Api secret for token based auth.
            frappe_session (<requests.Session()>): Object representation
            callback (func): Callback function to handle session data
    """

    def __init__(self,
        url, username=None, password=None, session_data=None, api_key=None, api_secret=None, callback=None, headers=None):
        """

        Returns:
                - <FrappeRequest> object initialized
        """
        self.frappe_session = requests.Session()
        atexit.register(self.frappe_session.close)

        self.url = url
        self.usr = username
        self.pwd = password
        self.session_data = None
        self.callback = callback
        self.headers = headers

        # If user provides `session_data` don't login again,
        # instead set the cookie data in requests.Session() object
        if session_data:
            # Make sure user:pass exists for 403 relogins
            if not all([self.usr, self.pwd]):
                raise MissingConfigException("Missing user, password for session based auth.")

            self.session_data = session_data
            self.set_session_token(session_data)
        elif self.usr and self.pwd:
            login_response = self._login()
            self.session_data = self._get_cookie_data(login_response)
        elif api_key and api_secret:
            self.frappe_session.headers.update({"Authorization": "token {api_key}:{api_secret}".format(
                api_key=api_key,
                api_secret=api_secret
            )})

    @property
    def is_legacy_auth(self):
        if (self.usr and self.pwd) or self.session_data:
            return True
        return False

    def _get_cookie_data(self, response):
        return response.cookies.get_dict()

    def _process_response(self, response):
        try:
            rjson = response.json()
        except ValueError:
            raise GeneralException("Unable to process non JSON response")
        return rjson

    def _login(self):
        """
        Internal call to POST login data to Frappe.

        Returns:
            login_response: <Requests> object
        """
        login_response = self.frappe_session.post(
            self.url, data={'cmd': 'login', 'usr': self.usr, 'pwd': self.pwd}, headers=self.headers)

        if login_response.status_code == 403:
            raise GeneralException("Invalid Session")
        if login_response.status_code != 200:
            raise GeneralException("An error with frappe response occurred")
        # If user provides a callback function, call the function with the
        # session data
        if self.callback:
            session_data = self._get_cookie_data(login_response)
            self.callback(session_data)
        return login_response

    def set_session_token(self, session_data):
        """
        Creates a <ResponseCookieJar> object from a dict
        and updates the session object with the newly created
        cookie object.

        Args:
            session_data (dict): Dict of session cookie data
        """
        if session_data:
            cookiejar = requests.utils.cookiejar_from_dict(session_data)
        # Set the cookies for future requests made by `self.frappe_session` object
        self.frappe_session.cookies = cookiejar

    def get(self, method, params=None, headers=None):
        """
        Wrapper around GET API requests. Handles the 1st 403 response
        internally

        Args:
            method (str): Endpoint to call
            params (dict): Dict representation of additional data to call

        Returns:
            response (<requests.Response>): Response object received from the Frappe server

        """
        if headers:
            headers.update(self.headers)
        else:
            headers = self.headers

        response = self.frappe_session.get(self.url + "/api/method/" + method + "/", params=params, headers=headers)
        if response.status_code == 403 and self.is_legacy_auth:
            # For the 1st 403 response try logging again
            login_response = self._login()
            if login_response.status_code == 200:
                response = self.frappe_session.get(self.url + "/api/method/" + method + "/", params=params, headers=headers)

        processed_response = self._process_response(response)
        return processed_response

    def post(self, method, data=None, json=None, headers=None):
        """
        Wrapper around POST API requests. Handles the 1st 403 response
        internally

        Args:
            method (str): Endpoint to call
            data (dict): Dict representation of additional data to send in request
            json (json): Json representation of additional data to send in request

        Returns:
            response (<requests.Response>): Response object received from the Frappe server

        """
        if headers:
            headers.update(self.headers)
        else:
            headers = self.headers

        response = self.frappe_session.post(
            self.url + "/api/method/" + method + "/", data=data, json=json, headers=headers
        )
        if response.status_code == 403 and self.is_legacy_auth:
            # For the 1st 403 response try logging again
            login_response = self._login()
            if login_response.status_code == 200:
                response = self.frappe_session.post(
                    self.url + "/api/method/" + method + "/", data=data, json=json, headers=headers
                )

        processed_response = self._process_response(response)
        return processed_response

    def get_paginated_doc(
            self, doctype, filters=None,
            fields=None, limit_page_length=100, limit_start=None, order_by=None,
            headers=None
    ):
        """
        Wrapper around GET API for fetching doctype data in a paginated fashion.

        Args:
            doctype (str): Doctype name
            filters (dict): Dict containing filters
            fields (list): Fields to return from the doctype
            limit_page_length (int): Interger indicating the page length limit
            limit_start (int): Integer indicating the page start
            order_by (str): String indicating to order results by

        Returns:
            response (<requests.Response>): Response object received from the Frappe server
        """
        if headers:
            headers.update(self.headers)
        else:
            headers = self.headers

        start = limit_start if limit_start else 0
        limit_page_length = 100 if limit_page_length == 0 else limit_page_length
        params = {
            "limit_start": str(start),
            "limit_page_length": str(limit_page_length),
        }
        if filters:
            params["filters"] = json.dumps(filters)
        if fields:
            params["fields"] = json.dumps(fields)
        if order_by:
            params["order_by"] = order_by

        has = True
        pages = 0
        empty_response = {"data": []}
        endpoint = "{url}/api/resource/{doctype}/".format(
            url=self.url,
            doctype=doctype,
        )

        while has:
            response = self.frappe_session.get(endpoint, params=params, headers=headers)

            # Previous iteration was the last page
            if response.status_code == 404:
                has = False
                yield empty_response
                return

            if response.status_code == 403 and self.is_legacy_auth:
                # For the 1st 403 response try logging again
                login_response = self._login()
                if login_response.status_code == 200:
                    response = self.frappe_session.get(endpoint, params=params, headers=headers)

            processed_response = self._process_response(response)
            pages += 1

            # No items.
            if len(processed_response.get("data", [])) == 0:
                yield empty_response
                return
            # List of items fetches has lesser items than the given page size. last page!
            elif len(processed_response.get("data", [])) < limit_page_length:
                yield processed_response
                return

            # Increment the offset.
            if pages > 0:
                start += limit_page_length
                params["limit_start"] = start

            yield processed_response

    def get_doc(
            self, doctype, name="", filters=None,
            fields=None, limit_page_length=None, limit_start=None, order_by=None,
            headers=None, pagination=False
    ):
        """
        Wrapper around GET API for fetching doctype data.

        Args:
            doctype (str): Doctype name
            name (str): Doctype record name identifier
            filters (dict): Dict containing filters
            fields (list): Fields to return from the doctype
            limit_page_length (int): Interger indicating the page length limit
            limit_start (int): Integer indicating the page start
            order_by (str): String indicating to order results by

        Returns:
            response (<requests.Response>): Response object received from the Frappe server
        """
        # Cannot fetch paginated items for a single fetch
        if name != "" and pagination:
            pagination = False

        # Use pagination API
        if pagination:
            return self.get_paginated_doc(doctype,
                filters=filters,
                fields=fields,
                limit_page_length=limit_page_length,
                limit_start=limit_start,
                order_by=order_by,
                headers=headers
            )

        if headers:
            headers.update(self.headers)
        else:
            headers = self.headers

        params = {}
        if filters:
            params["filters"] = json.dumps(filters)
        if fields:
            params["fields"] = json.dumps(fields)
        if limit_start:
            params["limit_start"] = str(limit_start)
        if limit_page_length:
            params["limit_page_length"] = str(limit_page_length)
        if order_by:
            params["order_by"] = order_by

        response = self.frappe_session.get(self.url + "/api/resource/" + doctype + "/" + name, params=params, headers=headers)
        if response.status_code == 403 and self.is_legacy_auth:
            # For the 1st 403 response try logging again
            login_response = self._login()
            if login_response.status_code == 200:
                response = self.frappe_session.get(self.url + "/api/resource/" + doctype + "/" + name, params=params, headers=headers)

        processed_response = self._process_response(response)
        return processed_response
