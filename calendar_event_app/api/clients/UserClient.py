import requests
import json
from ...api.errors import Unauthorized, APIError


class UserClient(object):

    def __init__(self, base_url, api_token):
        self.base_url = base_url + '/api/v1/users'
        self.api_token = api_token

        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'SSWS ' + self.api_token
        }

    def users_me(self):
        response = requests.get(self.base_url + '/me', headers=self.headers)
        return response.json()

    def filter_user(self, filter_string):
        query_url = self.base_url + '?filter=' + filter_string
        print(query_url)
        response = requests.get(query_url, headers=self.headers)
        return response.json()

    def create_user(self, email, first_name, last_name):
        user = {
            'profile': {
                'email': email,
                'login': email,
                'firstName': first_name,
                'lastName': last_name
            }
        }
        json_user = json.dumps(user)
        response = requests.post(self.base_url + '?activate=true', headers=self.headers, data=json_user)
        status = int(float(response.status_code))
        if status >= 400:
            if status == 401:
                raise Unauthorized()
            else:
                raise APIError(message=response.content, status_code=status)

        return {"status_code":  status, "result": response.json()}
