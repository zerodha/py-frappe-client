import requests
from .frappe_exceptions import GeneralException, TokenException


class FrappeRequest(object):
    """Class representation of FrappeRequest object

    Attributes:
            url: URL of Frappe site.
            usr (str): Username to Frappe Login.
            pwd (str): Password to Frappe Login.
            session_data (dict): dict of session object cookie data.
            frappe_session (<requests.Session()>): Object representation
            callback (func): Callback function to handle session data
    """

    def __init__(self, url, username, password, session_data=None, callback=None):
        """

        Returns:
                - <FrappeRequest> object initialized
        """
        self.frappe_session = requests.Session()
        self.url = url
        self.usr = username
        self.pwd = password
        self.session_data = None
        self.callback = callback

        # If user provides `session_data` don't login again,
        # instead set the cookie data in requests.Session() object
        if session_data:
            self.session_data = session_data
            self.set_session_token(session_data)
        else:
            login_response = self._login()
            self.session_data =  self._get_cookie_data(login_response)


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
            self.url, data={'cmd':'login','usr':self.usr, 'pwd':self.pwd})

        if login_response.status_code == 403:
            raise GeneralException("Invalid Session")
        if login_response.status_code !=200:
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


    def get(self, method, params=None):
        """
        Wrapper around GET API requests. Handles the 1st 403 response
        internally

        Args:
            method (str): Endpoint to call
            params (dict): Dict representation of additional data to call

        Returns:
            response (<requests.Response>): Response object received from the Frappe server

        """
        response = self.frappe_session.get(self.url +"/api/method/" + method + "/", params=params)
        if response.status_code == 403:
            # For the 1st 403 response try logging again
            login_response = self._login()
            if login_response.status_code == 200:
                response = self.frappe_session.get(self.url +"/api/method/" + method + "/", params=params)

        processed_response = self._process_response(response)
        return processed_response

    def post(self, method, data=None):
        """
        Wrapper around POST API requests. Handles the 1st 403 response
        internally

        Args:
            method (str): Endpoint to call
            params (dict): Dict representation of additional data to call

        Returns:
            response (<requests.Response>): Response object received from the Frappe server

        """
        response = self.frappe_session.post(self.url +"/api/method/" + method + "/", data=data)
        if response.status_code == 403:
            # For the 1st 403 response try logging again
            login_response = self._login()
            if login_response.status_code == 200:
                response = self.frappe_session.post(self.url +"/api/method/" + method + "/", data=data)

        processed_response = self._process_response(response)
        return processed_response