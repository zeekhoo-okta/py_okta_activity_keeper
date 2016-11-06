import json
from datetime import date

import requests
import six
from api.clients.CronofyClient import CronofyClient
from api.clients.ForcedotcomClient import ForcedotcomClient
from api.errors import Unauthorized
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.SFDCSerializers import sfdc_login_serializer
from forms import AddTaskForm, ImportTaskForm
from models import Task

OKTA_ORG = ''.join(['https://', settings.OKTA_ORG])
API_TOKEN = settings.OKTA_API_TOKEN
SESSION_COOKIES = ['userId',
                   'user_id',
                   'login',
                   'time_zone',
                   'event_range',
                   'cronofy_access_token',
                   'forcecom_access_token'
                   ]


class STATUS_CODES():
    NO_TOKEN = 'NO_TOKEN'
    NO_CALENDAR = 'NO_CALENDAR'
    SUCCESS = 'SUCCESS'


def home_view(request):
    return render(request, 'index.html')


def task_view(request, p):
    activity_date = ''
    summary = ''
    time_minutes = 0

    if p != 'new':
        task = Task.objects.get(pk=p)
        if task:
            if request.method == 'POST':
                task.status_code = 'C'
                task.save()

                task_form = AddTaskForm(request.POST)
                if task_form.is_valid():
                    return HttpResponseRedirect(reverse('mytasks'))
                else:
                    response = HttpResponse()
                    response.status_code = 200
                    return response

            activity_date = task.start.date().strftime('%m/%d/%Y')
            summary = task.summary
            time = task.end - task.start
            time_minutes = '{0:0g}'.format(time.total_seconds()/60)

    form = AddTaskForm(initial={
        'ActivityDate': activity_date,
        'Subject': summary,
        'TimeSpent': time_minutes
    })
    return render(request, 'task.html', {'form': form, 'id': p})


def logout(request):
    for name in SESSION_COOKIES:
        print('deleting session cookie {}'.format(name))
        if name in request.session:
            del request.session[name]
    return render(request, 'logged_out.html')


def login_session(request):
    response = HttpResponse()
    response.status_code = 200

    if request.method == 'POST':
        user = json.loads(request.body)

        #Set the okta session
        print('user = {}'.format(user))
        print('user id = {}'.format(user['id']))
        print('user profile = {}'.format(user['profile']))

        request.session['user_id'] = user['id']
        profile = user['profile']
        if profile['login']:
            request.session['login'] = profile['login']
        else:
            request.session['login'] = None
        if profile['timeZone']:
            request.session['time_zone'] = profile['timeZone']
        else:
            request.session['time_zone'] = 'America/Los_Angeles'

    else:
        if 'user_id' in request.session:
            user_id = request.session['user_id']
            response.content = {"user_id", user_id}
        else:
            response.content = {"user_id", "None"}

    return HttpResponseRedirect(reverse_lazy('home'))


def _nosession_check(request):
    if 'user_id' in request.session:
        return request.session['user_id']

    return None


def my_tasks_view(request):
    user_id = _nosession_check(request)
    if not user_id:
        return HttpResponseRedirect(reverse_lazy('home'))

    list_of_tasks = Task.objects.filter(okta_user_id=user_id, status_code='N').order_by('start')
    dates = []
    for task in list_of_tasks:
        if task.start_date_local() not in dates:
            dates.append(task.start_date_local())

    c = {'tasks': list_of_tasks, 'dates': dates}
    return render(request, 'tasks.html', c)


def import_options_view(request):
    user_id = _nosession_check(request)
    if not user_id:
        return HttpResponseRedirect(reverse_lazy('home'))

    form = ImportTaskForm()
    return render(request, 'import_options.html', {'form': form})


def import_tasks(request):
    user_id = _nosession_check(request)
    if not user_id:
        return HttpResponseRedirect(reverse_lazy('home'))

    if request.method == 'POST':
        form = ImportTaskForm(request.POST)
        if form.is_valid():
            range = form.cleaned_data['ImportRange']
            print('Import range = {}'.format(range))
            request.session['event_range'] = range

    if 'cronofy_access_token' in request.session:
        if _populate_tasks(request) == STATUS_CODES.NO_TOKEN:
            return HttpResponseRedirect(reverse('import_tasks'))

        return HttpResponseRedirect(reverse('mytasks'))

    base = settings.CRONOFY_AUTH_URL + "/authorize"
    params = {
        'response_type': 'code',
        'client_id': settings.CRONOFY_CLIENT_ID,
        'redirect_uri': settings.APP_URL + '/cronofy/oauth/callback',
        'scope': 'read_events'

    }
    params_str = __dict_to_query_params(params)
    return HttpResponseRedirect(base + params_str)


def __dict_to_query_params(d):
    if d is None or len(d) == 0:
        return ''

    param_list = [param + '=' + (str(value).lower() if type(value) == bool else str(value))
                  for param, value in six.iteritems(d) if value is not None]
    return '?' + "&".join(param_list)


def cronofy_oauth_callback(request):
    user_id = _nosession_check(request)
    if not user_id:
        return HttpResponseRedirect(reverse_lazy('home'))

    return render(request, 'cronofy_oauth_callback.html')


def cronofy_access_token(request):
    user_id = _nosession_check(request)
    if not user_id:
        return HttpResponseRedirect(reverse_lazy('home'))

    if request.method == 'POST':
        client_id = settings.CRONOFY_CLIENT_ID
        client_secret = settings.CRONOFY_CLIENT_SECRET
        received_json_data = json.loads(request.body)
        access_code = received_json_data['code']

        post_data = {
          "client_id": client_id,
          "client_secret": client_secret,
          "grant_type": "authorization_code",
          "code": access_code,
          "redirect_uri": settings.APP_URL + "/cronofy/oauth/callback"
        }
        result = requests.post(settings.CRONOFY_AUTH_URL + "/token", data=post_data)
        content = json.loads(result.content)
        token = content['access_token']
        request.session['cronofy_access_token'] = token

        if 'event_range' in request.session:
            if _populate_tasks(request) == STATUS_CODES.NO_TOKEN:
                return HttpResponseRedirect(reverse('import_tasks'))

        response = HttpResponse()
        response.status_code = 200
        return response

    return HttpResponseRedirect(reverse_lazy('home'))


def _populate_tasks(request):
    token = request.session.get('cronofy_access_token')
    event_range = request.session.get('event_range')
    tzid = request.session.get('time_zone')
    login = request.session.get('login')
    user_id = request.session.get('user_id')

    to_date = date.today() + relativedelta(days=1)
    to_date = to_date.strftime('%Y-%m-%d')
    if 'Month' in event_range:
        from_date = date.today() - relativedelta(months=1)
    else:
        num_weeks = int(float(event_range[:1]))
        num_days = 7*num_weeks
        from_date = date.today() - relativedelta(days=num_days)
    from_date = from_date.strftime('%Y-%m-%d')

    try:
        client = CronofyClient(token)
        calendar_id = None

        try:
            result = client.get_calendars()
            event_calendars = result['calendars']
            for calendar in event_calendars:
                if calendar['calendar_name'] == 'Calendar' and calendar['profile_name'] == login:
                    calendar_id = calendar['calendar_id']
        except Unauthorized as e:
            if 'cronofy_access_token' in request.session:
                del request.session['cronofy_access_token']
            return STATUS_CODES.NO_TOKEN

        if not calendar_id:
            return STATUS_CODES.NO_CALENDAR

        params = {
            "calendar_id": calendar_id,
            "tzid": tzid,
            "from": from_date,
            "to": to_date,
        }
        result = client.get_events(params)
        events = result['events']
        for event in events:
            print('event: {0} {1}'.format(event['event_uid'], event['summary']))
            task = Task.objects.filter(event_uid=event['event_uid'])
            if task:
                print('already exists')
            else:
                new = Task(event_uid=event['event_uid'],
                           summary=event['summary'],
                           calendar_id=calendar_id,
                           okta_user_id=user_id,
                           start=event['start'],
                           end=event['end'],
                           description=event['description'],
                           status_code='N'
                           )
                new.save()
    except Exception as e:
        print("There was an exception: {}".format(e))

    return STATUS_CODES.SUCCESS


def forcecom_oauth_auth(request):
    user_id = _nosession_check(request)
    if not user_id:
        return HttpResponseRedirect(reverse_lazy('home'))

    base = settings.SFDC_URL + "/services/oauth2/authorize"
    params = {
        'response_type': 'code',
        'client_id': settings.SFDC_CLIENT_ID,
        'redirect_uri': settings.APP_URL + '/sfdc/oauth/callback',
    }
    params_str = __dict_to_query_params(params)
    return HttpResponseRedirect(base + params_str)


def forcecom_oauth_callback(request):
    return render(request, 'forcecom_oauth_callback.html')


def forcecom_access_token(request):
    user_id = _nosession_check(request)
    if not user_id:
        return HttpResponseRedirect(reverse_lazy('home'))

    if request.method == 'POST':
        client_id = settings.SFDC_CLIENT_ID
        client_secret = settings.SFDC_SECRET
        received_json_data = json.loads(request.body)
        access_code = received_json_data['code']

        post_data = {
          "client_id": client_id,
          "client_secret": client_secret,
          "grant_type": "authorization_code",
          "code": access_code,
          "redirect_uri": settings.APP_URL + "/sfdc/oauth/callback"
        }
        result = requests.post(settings.SFDC_URL + "/services/oauth2/token", data=post_data)
        content = json.loads(result.content)
        token = content['access_token']
        print("force.com access token retrieved: {}".format(token))
        request.session['forcecom_access_token'] = token

        response = HttpResponse()
        response.status_code = 200
        return response

    return HttpResponseRedirect(reverse_lazy('home'))


def forcecom_recent(request):
    client = ForcedotcomClient(request.session['forcecom_access_token'])

    opportunities = client.recent_opportunities()
    print('recents: {}'.format(opportunities))
    for opp in opportunities:
        print("recent opportunity: {0}".format(opp['Name']))

    response = HttpResponse()
    response.status_code = 200
    return response


class api_view(APIView):
    def post(self, request, format=None):
        login = sfdc_login_serializer(data=request.data)
        if login.is_valid():
            print('username={}'.format(login.data['username']))
            print('password={}'.format(login.data['password']))

        return Response(
            {'success': True,
             'message': 'This is successful'},
            status=status.HTTP_200_OK
        )
