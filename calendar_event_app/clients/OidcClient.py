import requests
import base64


class OidcClient(object):

    def __init__(self, issuer):
        self.issuer = issuer

    def introspect(self, client_id, client_secret, token, hint):

        basic = base64.b64encode(client_id + ":" + client_secret)
        headers = {
            'Authorization': 'Basic ' + basic
        }
        introspect = {
            "token": token,
            "token_type_hint": hint
        }
        response = requests.post('{}/v1/introspect'.format(self.issuer),
                                 headers=headers,
                                 data=introspect)
        return response
