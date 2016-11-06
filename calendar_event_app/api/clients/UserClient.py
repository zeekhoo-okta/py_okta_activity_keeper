import requests


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
