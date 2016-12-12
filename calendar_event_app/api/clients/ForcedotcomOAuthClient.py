import requests
from django.conf import settings
from ...api.errors import Unauthorized, APIError
from ...api.utils import dict_to_query_params
import json


class ForcedotcomOAuthClient(object):
    def __init__(self):
        self.base_url = settings.SFDC_URL + '/services/oauth2'
        self.app_url = settings.APP_URL
        self.client_id = settings.SFDC_CLIENT_ID
        self.secret = settings.SFDC_SECRET

        if not self.base_url:
            raise ValueError('Invalid base_url')

    def auth_code(self, task_id):
        base = self.base_url + "/authorize"
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.app_url + '/sfdc/oauth/callback',
        }
        params_str = dict_to_query_params(params)
        return base + params_str

    def access_token(self, access_code):
        if not access_code:
            raise ValueError('Invalid access code')

        post_data = {
          "client_id": self.client_id,
          "client_secret": self.secret,
          "grant_type": "authorization_code",
          "code": access_code,
          "redirect_uri": self.app_url + "/sfdc/oauth/callback"
        }
        result = requests.post(self.base_url + "/token", data=post_data)
        status = result.status_code
        if status != 200:
            if status == 401:
                raise Unauthorized()
            else:
                raise APIError(message=result.content, code=status)

        return json.loads(result.content)
