import requests
from django.conf import settings
from calendar_event_app.errors import Unauthorized, APIError
from calendar_event_app.utils import dict_to_query_params


class CronofyClient(object):
    def __init__(self, token):
        self.base_url = settings.CRONOFY_API_URL
        self.version = '1'
        self.token = token
        self.max_attempts = 5

        if not self.base_url:
            raise ValueError('Invalid base_url')

        if not self.token:
            raise ValueError('Invalid token')

        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }

    def get_calendars(self):
        response = requests.get(self.base_url + '/calendars', headers=self.headers)
        status = int(float(response.status_code))
        if status >= 400:
            if status == 401:
                raise Unauthorized()
            else:
                raise APIError('Import encountered an error.')

        return response.json()

    def get_events(self, params):
        params_str = dict_to_query_params(params)
        response = requests.get(self.base_url + '/events' + params_str, headers=self.headers)
        result = response.json()

        events = []
        next_page_events = []
        if 'pages' in result:
            pages = result['pages']
            if 'next_page' in pages:
                next_page_events = self.__events_next_page(pages['next_page'])
        if 'events' in result:
            events = result['events']

        return events + next_page_events

    def __events_next_page(self, url):
        events = []
        next_page_events = []

        response = requests.get(url, headers=self.headers)
        result = response.json()
        if 'pages' in result:
            pages = result['pages']
            if 'next_page' in pages:
                next_page_events = self.__events_next_page(pages['next_page'])

        if 'events' in result:
            events = result['events']

        return events + next_page_events
