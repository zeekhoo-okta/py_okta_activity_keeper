import requests
import base64
from ...api.errors import Unauthorized, APIError


class OidcClient(object):

    def __init__(self, base_url):
        self.base_url = base_url + '/oauth2/v1'

    def introspect(self, client_id, client_secret, token, hint):

        basic = base64.b64encode(client_id + ":" + client_secret)
        headers = {
            'Authorization': 'Basic ' + basic
        }
        introspect = {
            "token": token,
            "token_type_hint": hint
        }
        response = requests.post(self.base_url + '/introspect', headers=headers, data=introspect)
        return response
