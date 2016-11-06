import json
import inspect


class APIError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Unauthorized(Exception):
    def __init__(self, message=None):
        msg = "Unauthorized"
        if message:
            msg = msg + ": " + message
        self.message = msg

    def __str__(self):
        return self.message
