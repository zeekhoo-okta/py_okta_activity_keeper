import requests
import six
from django.conf import settings
from ...api.errors import Unauthorized, APIError
import json


class ForcedotcomClient(object):
    def __init__(self, token):
        self.base_url = settings.SFDC_URL
        self.version = settings.SFDC_API_VERSION
        self.token = token

        if not self.base_url:
            raise ValueError('Invalid base_url')

        if not self.token:
            raise ValueError('Invalid token')

        self.headers = {
            # 'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }

    def check_token(self):
        response = requests.get(self.base_url + '/services/data/' + self.version + '/recent/?limit=0',
                                headers=self.headers)
        return response.status_code == 200

    def search_opportunities(self, q):
        response = requests.get(self.base_url + '/services/data/' + self.version + '/parameterizedSearch/?q=' + q +
                                '&sobject=Opportunity&fields=Id,Name,CloseDate,Amount,StageName,Owner.Alias',
                                headers=self.headers)
        status = int(float(response.status_code))
        if status >= 400:
            if status == 401:
                raise Unauthorized()
            else:
                raise APIError(message=response.content, status_code=status)
        opportunities = []
        search_records = response.json()['searchRecords']
        for record in search_records:
            opportunity = {
                'Id': record['Id'],
                'Name': record['Name'],
                'CloseDate': record['CloseDate'],
                'Amount': record['Amount'],
                'Stage': record['StageName'],
                'Owner': record['Owner']['Alias']
            }
            opportunities.append(opportunity)

        return opportunities

    def recent_opportunities(self):
        response = requests.get(self.base_url + '/services/data/' + self.version + '/sobjects/Opportunity/listviews',
                                headers=self.headers)
        status = int(float(response.status_code))
        print(status)
        if status >= 400:
            if status == 401:
                raise Unauthorized()
            else:
                raise APIError(message=response.content, status_code=status)

        recent_opportunities = []
        urls = response.json()['listviews']
        for list in urls:
            if list['developerName'] == 'RecentlyViewedOpportunities':
                results_url = list['resultsUrl']

                results = requests.get(self.base_url + results_url, headers=self.headers)
                results_json = results.json()
                records = results_json['records']
                for record in records:
                    opportunity = {}
                    columns = record['columns']
                    for column in columns:
                        if column['fieldNameOrPath'] == 'Id':
                            opportunity['Id'] = column['value']
                        if column['fieldNameOrPath'] == 'Name':
                            opportunity['Name'] = column['value']
                        if column['fieldNameOrPath'] == 'Amount':
                            val = column['value']
                            if val:
                                amount = float(column['value'])
                            else:
                                amount = 0
                            opportunity['Amount'] = "{:,.0f}".format(amount)
                        if column['fieldNameOrPath'] == 'CloseDate':
                            # Fri Sep 23 21:19:32 GMT 2016
                            str = column['value']
                            date_str = str[4:][:6] + ' ' + str[-4:]
                            opportunity['CloseDate'] = date_str
                        if column['fieldNameOrPath'] == 'StageName':
                            opportunity['Stage'] = column['value']
                        if column['fieldNameOrPath'] == 'Owner.Alias':
                            opportunity['Owner'] = column['value']
                    recent_opportunities.append(opportunity)
        return recent_opportunities

    @staticmethod
    def __dict_to_query_params(d):
        if d is None or len(d) == 0:
            return ''

        param_list = [param + '=' + (str(value).lower() if type(value) == bool else str(value))
                      for param, value in six.iteritems(d) if value is not None]
        return '?' + "&".join(param_list)

    def post_task(self, op, subject, activity_date, time_spent, task_type):
        task = {
            'WhatId': op,
            'Subject': subject,
            'Status': 'Completed',
            'ActivityDate': activity_date,
            'Time_Spent_minutes__c': time_spent
            # "Type__c": task_type
        }
        json_task = json.dumps(task)
        resource = self.base_url + '/services/data/' + self.version + '/sobjects/Task'
        response = requests.post(resource, headers=self.headers, data=json_task)
        status = int(float(response.status_code))
        if status >= 400:
            if status == 401:
                raise Unauthorized()
            else:
                raise APIError(message=response.content, status_code=status)

        return {"status_code":  status, "result": response.json()}