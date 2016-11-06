import requests
import six
from django.conf import settings
from ...api.errors import Unauthorized, APIError


class ForcedotcomClient(object):
    def __init__(self, token):
        self.base_url = settings.SFDC_URL
        self.version = 'v38.0'
        self.token = token

        if not self.base_url:
            raise ValueError('Invalid base_url')

        if not self.token:
            raise ValueError('Invalid token')

        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }

    def recent_opportunities(self):
        response = requests.get(self.base_url + '/services/data/' + self.version + '/sobjects/Opportunity/listviews',
                                headers=self.headers)
        status = int(float(response.status_code))
        print('get_recents STATUS: {}'.format(status))
        if status >= 400:
            if status == 401:
                raise Unauthorized()
            else:
                raise APIError(status)

        recent_opportunities = []
        urls = response.json()['listviews']
        for list in urls:
            if list['developerName'] == 'RecentlyViewedOpportunities':
                results_url = list['resultsUrl']

                results = requests.get(self.base_url + results_url, headers=self.headers)
                results_json = results.json()
                records = results_json['records']
                for record in records:
                    Opportunity = {}

                    columns = record['columns']
                    for column in columns:
                        if column['fieldNameOrPath'] == 'Name':
                            Opportunity['Name'] = column['value']

                    recent_opportunities.append(Opportunity)

        return recent_opportunities

    @staticmethod
    def __dict_to_query_params(d):
        if d is None or len(d) == 0:
            return ''

        param_list = [param + '=' + (str(value).lower() if type(value) == bool else str(value))
                      for param, value in six.iteritems(d) if value is not None]
        return '?' + "&".join(param_list)