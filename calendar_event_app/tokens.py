from __future__ import absolute_import
import jwt as jwt_python
from .clients.OidcClient import *
from django.conf import settings


class TokenValidator:
    def __init__(self, keys=[]):
        self.keys = keys

    def call_token_endpoint(self, auth_code):
        token_endpoint = "{}/v1/token".format(settings.ISSUER)

        basic_auth_str = '{0}:{1}'.format(settings.CLIENT_ID, settings.CLIENT_SECRET)
        authorization_header = base64.b64encode(basic_auth_str.encode())
        header = {
            'Authorization': 'Basic: ' + authorization_header.decode("utf-8"),
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'scope': 'openid profile',
            'redirect_uri': '{}/oidc/callback'.format(settings.APP_URL)
        }

        r = requests.post(token_endpoint, headers=header, params=data)
        response = r.json()

        result = {}
        if 'error' not in response:
            if 'access_token' in response:
                result['access_token'] = response['access_token']
            if 'id_token' in response:
                result['id_token'] = response['id_token']

        return result if len(list(result.keys())) > 0 else None

    def validate_id_token(self, token, nonce):
        try:
            decoded_token = jwt_python.decode(token, verify=False)
            # if decoded_token['iss'] != self.config.issuer:
            #     raise ValueError('Issuer does not match')
            #
            # if decoded_token['aud'] != self.config.client_id:
            #     raise ValueError('Audience does not match client_id')
            #
            # if decoded_token['exp'] < int(time.time()):
            #     raise ValueError('Token has expired')

            if nonce is not None:
                if nonce != decoded_token['nonce']:
                    raise ValueError('nonce value does not match Authentication Request nonce')

            oidc_client = OidcClient(settings.ISSUER)
            response = oidc_client.introspect(settings.CLIENT_ID, settings.CLIENT_SECRET, token, "id_token")
            if response.status_code == 200:
                return response.json()
            else:
                raise ValueError('introspection failed')

        except ValueError as err:
            return err
