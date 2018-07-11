class NoSession(Exception):
    def __init__(self, message=None):
        msg = "No Session"
        if message:
            msg = msg + ": " + message
        self.message = msg
        self.status_code = 302

    def __str__(self):
        return self.message


class NoSfdcSession(Exception):
    def __init__(self, message=None):
        msg = "No SFDC Session"
        if message:
            msg = msg + ": " + message
        self.message = msg
        self.status_code = 302

    def __str__(self):
        return self.message


class APIError(Exception):
    def __init__(self, message, status_code=None):
        self.message = message
        self.status_code = 400
        if status_code:
            self.status_code = status_code

    def __str__(self):
        return '(' + self.status_code + ')' + self.message


class Unauthorized(Exception):
    def __init__(self, message=None):
        msg = "Unauthorized"
        if message:
            msg = msg + ": " + message
        self.message = msg
        self.status_code = 401

    def __str__(self):
        return self.message
