from builtins import bytes
import requests
import base64


class OidcClient:

    def __init__(self, issuer):
        self.issuer = issuer

    def introspect(self, client_id, client_secret, token, hint):

        data = '{0}:{1}'.format(client_id, client_secret)

        basic = base64.b64encode(bytes(data, 'utf-8'))
        headers = {
            'Authorization': 'Basic ' + basic.decode('utf-8')
        }
        introspect = {
            "token": token,
            "token_type_hint": hint
        }
        response = requests.post('{}/v1/introspect'.format(self.issuer),
                                 headers=headers,
                                 data=introspect)
        return response
