import json
import requests
from datetime import date

from api.clients.CronofyClient import CronofyClient
from api.clients.ForcedotcomClient import ForcedotcomClient
from api.clients.ForcedotcomOAuthClient import ForcedotcomOAuthClient
from api.utils import dict_to_query_params
from .api.errors import Unauthorized
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404

from calendar_event_app.api.StatusCodes import StatusCodes
from forms import AddTaskForm, ImportTaskForm, PreferenceForm
from models import Task, UserPreference


OKTA_ORG = ''.join(['https://', settings.OKTA_ORG])
SESSION_COOKIES = ['userId',
                   'user_id',
                   'login',
                   'time_zone',
                   'event_range',
                   'cronofy_access_token',
                   'forcecom_access_token'
                   ]

STATUS_CODES = StatusCodes()


def logout(request):
    for name in SESSION_COOKIES:
        if name in request.session:
            del request.session[name]
    return render(request, 'logged_out.html')


def login_session(request):
    if request.method == 'POST':
        user = json.loads(request.body)

        # Set the okta session
        user_id = user['id']
        profile = user['profile']
        if profile['firstName'] and profile['lastName']:
            name = profile['firstName'] + ' ' + profile['lastName']
        else:
            name = 'Unknown'
        if profile['timeZone']:
            time_zone = profile['timeZone']
        else:
            time_zone = None

        request.session['user_id'] = user_id
        try:
            preference = get_object_or_404(UserPreference, okta_user_id=user_id)
            preference.name = name
            preference.time_zone = time_zone
            preference.save()
        except Exception as e:
            preference = UserPreference(okta_user_id=user_id, name=name, time_zone=time_zone)
            preference.save()

        if profile['login']:
            request.session['login'] = profile['login']
        else:
            request.session['login'] = None
        if profile['timeZone']:
            request.session['time_zone'] = profile['timeZone']
        else:
            request.session['time_zone'] = 'America/Los_Angeles'

    return HttpResponseRedirect(reverse_lazy('home'))


def _nosession_check(request):
    if 'user_id' in request.session:
        return request.session['user_id']
    return None


def _forcecom_session_check(request):
    if 'forcecom_access_token' in request.session:
        token = request.session['forcecom_access_token']
        client = ForcedotcomClient(token)
        if client.check_token():
            return token
    else:
        return None


def home_view(request):
    if _nosession_check(request) is not None:
        return HttpResponseRedirect(reverse('mytasks'))
    return render(request, 'index.html')


def preferences(request):
    user_id = _nosession_check(request)
    if not user_id:
        return HttpResponseRedirect(reverse_lazy('home'))

    preference = UserPreference.objects.get(okta_user_id=user_id)
    if request.method == 'POST':
        if preference:
            form = PreferenceForm(request.POST)
            if form.is_valid():
                preference.time_zone = form.cleaned_data['time_zone']
                preference.save()
                request.session['time_zone'] = preference.time_zone

        return HttpResponseRedirect(reverse('mytasks'))

    return render(request, 'preferences.html', {'form': preference})


def task_view(request, p):
    task = None
    if p != 'new':
        task = Task.objects.get(pk=p)

    if request.method == 'DELETE':
        if task:
            task.status_code = 'C'
            task.save()
        response = HttpResponse()
        response.status_code = 204
        return response

    token = _forcecom_session_check(request)
    if not token:
        return HttpResponseRedirect(reverse('forcecom_auth_init'))

    if request.method == 'POST':
        form = AddTaskForm(request.POST)
        if form.is_valid():
            try:
                client = ForcedotcomClient(token)
                activity_date = form.cleaned_data['activity_date'].strftime('%Y-%m-%-d')

                result = client.post_task(
                    form.cleaned_data['opportunity_id'],
                    form.cleaned_data['subject'],
                    activity_date,
                    form.cleaned_data['time_spent'],
                    form.cleaned_data['task_type']
                )
                if task:
                    task.status_code = 'C'
                    task.save()

            except Exception as e:
                print('There was an error: {0}: {1}'.format(e.status_code, e.message))
                if e.status_code == 401:
                    return HttpResponseRedirect(reverse('forcecom_auth_init'))

            return HttpResponseRedirect(reverse('mytasks'))
    elif task:
        form = AddTaskForm(initial={
            'activity_date': task.start.date().strftime('%m/%d/%Y'),
            'subject': task.summary,
            'time_spent': '{0:0g}'.format((task.end - task.start).total_seconds() / 60)
        })
    else:
        # blank form
        form = AddTaskForm(initial={
            'activity_date': '',
            'subject': '',
            'time_spent': 0
        })

    return render(request, 'task.html', {'form': form, 'id': p})


def my_tasks_view(request):
    user_id = _nosession_check(request)
    if not user_id:
        return HttpResponseRedirect(reverse_lazy('home'))

    if 'time_zone' in request.session:
        time_zone = request.session['time_zone']
    else:
        time_zone = 'America/Los_Angeles'

    list_of_tasks = Task.objects.filter(okta_user_id=user_id, status_code='N').order_by('start')
    dates = []
    for task in list_of_tasks:
        task.set_tz(time_zone)
        if task.start_date_local() not in dates:
            dates.append(task.start_date_local())

    c = {'tasks': list_of_tasks, 'dates': dates}

    if 'forcecom_access_token' in request.session:
        c['has_token'] = '1'

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
            import_range = form.cleaned_data['ImportRange']
            request.session['event_range'] = import_range

    if 'cronofy_access_token' in request.session:
        if _populate_tasks(request) == STATUS_CODES.NO_TOKEN:
            return HttpResponseRedirect(reverse('import_tasks'))
        else:
            return HttpResponseRedirect(reverse('mytasks'))
    else:
        base = settings.CRONOFY_AUTH_URL + "/authorize"
        params = {
            'response_type': 'code',
            'client_id': settings.CRONOFY_CLIENT_ID,
            'redirect_uri': settings.APP_URL + '/cronofy/oauth/callback',
            'scope': 'read_events'

        }
        params_str = dict_to_query_params(params)
        return HttpResponseRedirect(base + params_str)


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
            if not len(event['start']) == 10:
                task = Task.objects.filter(event_uid=event['event_uid'])
                if not task:
                    attendee_list = ''
                    attendees = event['attendees']
                    for attendee in attendees:
                        if len(attendee_list) < 255 - len(attendee['display_name']) - 2:
                            attendee_list = attendee_list + attendee['display_name'] + ', '
                    new = Task(event_uid=event['event_uid'],
                               summary=event['summary'],
                               calendar_id=calendar_id,
                               okta_user_id=user_id,
                               start=event['start'],
                               end=event['end'],
                               description=event['description'][0:254],
                               organizer=event['organizer']['display_name'][0:99],
                               attendees=attendee_list[0:254],
                               status_code='N'
                               )
                    new.save()
    except Exception as e:
        print("There was an exception: {}".format(e))

    return STATUS_CODES.SUCCESS


def forcecom_auth_init(request):
    return render(request, 'sfdc_auth_init.html')


def forcecom_auth_complete(request):
    return render(request, 'sfdc_auth_complete.html')


def forcecom_oauth_auth(request, task_id=None):
    user_id = _nosession_check(request)
    if not user_id:
        return HttpResponseRedirect(reverse_lazy('home'))

    client = ForcedotcomOAuthClient()
    return HttpResponseRedirect(client.auth_code(task_id))


def forcecom_oauth_callback(request):
    return render(request, 'forcecom_oauth_callback.html')


def forcecom_access_token(request):
    response = HttpResponse()

    if not _nosession_check(request):
        response.content = STATUS_CODES.NO_TOKEN
        response.status_code = 401

    if request.method == 'POST':
        try:
            received_json_data = json.loads(request.body)
            access_code = received_json_data['code']
            client = ForcedotcomOAuthClient()
            result = client.access_token(access_code)
            token = result['access_token']
            request.session['forcecom_access_token'] = token
        except Exception as e:
            response.content = e.message
            response.status_code = e.status_code

        return response

    return render(request, 'forcecom_oauth_callback.html')


def forcecom_search(request):
    status = 200
    reason = None
    try:
        client = ForcedotcomClient(request.session['forcecom_access_token'])

        if 'q' in request.GET:
            q = request.GET['q']
            opportunities = client.search_opportunities(q)
        else:
            opportunities = client.recent_opportunities()

        response = json.dumps({'opportunities': opportunities})
    except Exception as e:
        response = json.dumps({'opportunities': 'error'})
        status = e.status_code
        reason = e.message

    return HttpResponse(response, status=status, reason=reason, content_type='application/json; charset=utf8')

