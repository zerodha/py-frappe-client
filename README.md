# Py-Frappe-Client

## Install

```
pip install py-frappe-client
```

[View on PyPi](https://pypi.org/project/py-frappe-client/)

## Usage

### Token based authentication

```python
>>> from frappe_client import FrappeRequest
>>> client = FrappeRequest(url="http://localhost:8002", api_key="API_KEY", api_secret="API_SECRET")
>>> client.get("method_name")
>>> client.post("method_name")
```

### Session based authentication (Legacy)

#### Initialize

```python
>>> from frappe_client import FrappeRequest
>>> client = FrappeRequest(url="http://localhost:8002", username="user", password="password")

>>> client.__dict__

{
   "frappe_session":<requests.sessions.Session at 0x1073fc978>,
   "url":"http://localhost:8002",
   "usr":"Administrator",
   "pwd":"pass",
   "session_data":{
      "full_name":"Administrator",
      "sid":"6684ed4e173094199b1cc0913d4044fdcec1d87d5d6a74a3728f229b",
      "system_user":"yes",
      "user_id":"Administrator",
      "user_image":""
   },
   "callback": None
}
```

#### Using Callback

The wrapper checks for a HTTP 403 Response from the server for the first time on every API call. If the server
returns 403, the wrapper attempts to login again. During this login, if a `callback` function is passed by the user
the new `session_data` is passed on to this callback parameter.

```python
# Example Callback function
 def store_session_data(data):
    print ("Callback function invoked with arg {}".format(data))

>>> client = FrappeRequest(url="http://localhost:8002", username="Administrator", password="pwd", callback=store_session_data)
Callback function invoked with arg {'full_name': 'Administrator', 'sid': '427f585e17c551b9bf70ff64a22a6998064d0415914aaf91beb981f2', 'system_user': 'yes', 'user_id': 'Administrator', 'user_image': ''}
```

#### Get Session Data

`client.session_data`

```python
# Example Output
>>> client.session_data

>>> {
   "full_name":"Administrator",
   "sid":"427f585e17c551b9bf70ff64a22a6998064d0415914aaf91beb981f2",
   "system_user":"yes",
   "user_id":"Administrator",
   "user_image":""
}
```

#### Storing Session Data

`session_data` is a `dict` object which is returned by `client.session_data` field.
Session Data needs to be stored locally on the client's end (database/redis/file/etc).

On further initializations of the FrappeRequest() class, you should pass `session_data` field
to prevent multiple sessions for the same user.

If `session_data` field is passed, all further API calls will use the same session.


### Invoke GET Endpoint

`client.get(method, params)`

```python
>>> # Example Request
>>> response = client.get(method="acop_process.lead_integration.ping")
>>> response.json()
{'message': 'PONG'}
```


### Invoke POST Endpoint

`client.post(method, data)`

```python
>>> # Example Request
>>> response = client.post(method="acop_process.lead_integration.post_ping", data={'test_param':123})
>>> response.json()
{'message': 'POST PONG success 123'}
```

### Documents API

```python
# Fetch a single resource
>>> response = client.get_doc("Custom Doctype", name="record1")
# Fetch multiple resources
>>> response = client.get_doc("Custom Doctype")
# With filters, fields
>>> response = client.get_doc("Custom Doctype", fields=["field1", "field2"], filters={"field3", ["in", [1, 2, 3]]})
# With page size, fetch 50 records at once
>>> response = client.get_doc("Custom Doctype", limit_page_length=50)
# fetch 50 records starting from offset 50
>>> response = client.get_doc("Custom Doctype", limit_start=50, limit_page_length=50)
# paginated generator
>>> fetch_iter = client.get_doc("Custom Doctype", limit_page_length=10, pagination=True)
>>> for records in fetch_iter:
      print(records["data"])
```

### Pagination API

```python
# Fetch in batches of 10 records from API using a generator
>>> fetch_iter = client.get_paginated_doc("Custom Doctype", limit_page_lenth=10)
>>> for records in fetch_iter:
      print(records["data"])
```


