# Py-Frappe-Client


## Usage

### Initialize
```
from frappe_client import FrappeRequest
client = FrappeRequest(url="http://localhost:8002", username="user", password="password", session_data=None, callback=store_session_data)

# Example Callback function
 def store_session_data(data):
    print ("Data stored is {}".format(data))


>>> client = FrappeRequest(url="http://localhost:8002", username="Administrator", password="pwd", callback=store_session_data)
Data stored is {'full_name': 'Administrator', 'sid': '427f585e17c551b9bf70ff64a22a6998064d0415914aaf91beb981f2', 'system_user': 'yes', 'user_id': 'Administrator', 'user_image': ''}

```

### Using Callback
The wrapper checks for a HTTP 403 Response from the server for the first time on every API call. If the server
returns 403, the wrapper attempts to login again. During this login, if a `callback` function is passed by the user
the new `session_data` is passed on to this callback parameter.  

### Get Session Data
```
client.session_data

# Example Output
# >>> client.session_data

>>> {'full_name': 'Administrator',
# 'sid': '427f585e17c551b9bf70ff64a22a6998064d0415914aaf91beb981f2',
# 'system_user': 'yes',
# 'user_id': 'Administrator',
# 'user_image': ''}
```

### Storing Session Data
```
session_data is a dict which is returned by `client.session_data` field. Session Data needs to be 
stored locally on the client's end (database/redis/file/etc).

On further initializations of the FrappeRequest() class, you should pass `session_data` field.
If `session_data` field is passed, all further API calls will use the same session.

Make sure to store and use `session_data` in order to prevent multiple login calls
```

### Get Endpoint call
```
client.get(method, params)

# Example Request
# In [13]: response = client.get(method="acop_process.lead_integration.ping")
# In [15]: response.json()
# Out[15]: {'message': 'PONG'}
```


### POST Endpoint call
```
client.get(method, params)

# Example Request
# In [20]: response = client.post(method="acop_process.lead_integration.post_ping", params={'test_param':123})
# In [21]: response.json()
Out[21]: {'message': 'POST PONG success 123'}
```

