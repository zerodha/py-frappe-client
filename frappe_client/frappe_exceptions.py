class FrappeResponseException(Exception):
    """Base exception class representing a Frappe reponse client exception.
    Every specific Frappe reponse client exception is a subclass of this
    and  exposes two instance variables	`.code` (HTTP error code)
    and `.message` (error text)."""

    def __init__(self, message, code=500):
        super(FrappeResponseException, self).__init__(message)
        self.code = code


class GeneralException(FrappeResponseException):
    """An unclassified, general error. Default code is 500"""

    def __init__(self, message):
        super(GeneralException, self).__init__(message, code=500)


class TokenException(FrappeResponseException):
    """Represents all token and authentication related errors."""

    def __init__(self, message):
        super(TokenException, self).__init__(message, code=403)


class MissingConfigException(Exception):
    pass