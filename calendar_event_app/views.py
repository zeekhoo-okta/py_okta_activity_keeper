import json
import requests
from datetime import date

from api.clients.CronofyClient import CronofyClient
from api.clients.ForcedotcomClient import ForcedotcomClient
from api.clients.ForcedotcomOAuthClient import ForcedotcomOAuthClient
from api.clients.UserClient import UserClient
from api.clients.OidcClient import OidcClient
from api.utils import dict_to_query_params
from api.errors import *
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from calendar_event_app.api.StatusCodes import StatusCodes
from forms import AddTaskForm, ImportTaskForm, PreferenceForm, RegistrationForm
from models import Task, UserPreference


OKTA_ORG = ''.join(['https://', settings.OKTA_ORG])
ENV = {'okta_org': OKTA_ORG, 'client_id': settings.CLIENT_ID}

SESSION_COOKIES = ['userId',
                   'user_id',
                   'login',
                   'time_zone',
                   'event_range',
                   'event_from_date',
                   'event_to_date',
                   'cronofy_access_token',
                   'forcecom_access_token'
                   ]

STATUS_CODES = StatusCodes()


def logout(request):
    for name in SESSION_COOKIES:
        if name in request.session:
            del request.session[name]
    return render(request, 'logged_out.html', ENV)


@csrf_exempt
def oidc_callback(request):
    if request.method == 'POST':
        if 'id_token' in request.POST:
            id_token = request.POST['id_token']
            #introspect
            oidcClient = OidcClient(OKTA_ORG)
            response = oidcClient.introspect(settings.CLIENT_ID, settings.CLIENT_SECRET, id_token, "id_token")
            status = response.status_code
            if status == 200:
                token = response.json()

                # Set the Okta session
                user_id = token['sub']
                if token['name']:
                    name = token['name']
                elif token['given_name'] and token['family_name']:
                    name = token['given_name'] + ' ' + token['family_name']
                else:
                    name = 'Unknown'

                if token['zoneinfo']:
                    time_zone = token['zoneinfo']
                else:
                    time_zone = 'America/Los_Angeles'

                request.session['user_id'] = user_id
                try:
                    preference = get_object_or_404(UserPreference, okta_user_id=user_id)
                    preference.name = name
                    if not preference.time_zone or preference.time_zone == '':
                        preference.time_zone = time_zone
                    else:
                        time_zone = preference.time_zone
                    preference.save()
                except Exception as e:
                    print(e)
                    preference = UserPreference(okta_user_id=user_id, name=name, time_zone=time_zone)
                    preference.save()

                if token['username']:
                    request.session['login'] = token['username']
                else:
                    request.session['login'] = None

                request.session['time_zone'] = time_zone

    return HttpResponseRedirect(reverse_lazy('home'))


# def login_session(request):
#     if request.method == 'POST':
#         user = json.loads(request.body)
#
#         # Set the Okta session
#         user_id = user['id']
#         profile = user['profile']
#         if profile['firstName'] and profile['lastName']:
#             name = profile['firstName'] + ' ' + profile['lastName']
#         else:
#             name = 'Unknown'
#         if profile['timeZone']:
#             time_zone = profile['timeZone']
#         else:
#             time_zone = 'America/Los_Angeles'
#
#         request.session['user_id'] = user_id
#         try:
#             preference = get_object_or_404(UserPreference, okta_user_id=user_id)
#             preference.name = name
#             if not preference.time_zone or preference.time_zone == '':
#                 preference.time_zone = time_zone
#             else:
#                 time_zone = preference.time_zone
#             preference.save()
#         except Exception as e:
#             print(e)
#             preference = UserPreference(okta_user_id=user_id, name=name, time_zone=time_zone)
#             preference.save()
#
#         if profile['login']:
#             request.session['login'] = profile['login']
#         else:
#             request.session['login'] = None
#
#         request.session['time_zone'] = time_zone
#
#     return HttpResponseRedirect(reverse_lazy('home'))


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            firstName = form.cleaned_data['firstName']
            lastName = form.cleaned_data['lastName']

            try:
                client = UserClient(OKTA_ORG, settings.API_TOKEN)
                response = client.create_user(email, firstName, lastName)
                if response['status_code'] == 200:
                    return HttpResponseRedirect(reverse('registration_success'))
            except Exception as e:
                form.add_error(field=None, error=e)
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


def registration_success(request):
    return render(request, 'registration_success.html')


def _nosession_check(request):
    if 'user_id' in request.session:
        return request.session['user_id']
    else:
        raise NoSession()

    return None


def _forcecom_session_check(request):
    try:
        _nosession_check(request)
        if 'forcecom_access_token' in request.session:
            token = request.session['forcecom_access_token']
            client = ForcedotcomClient(token)
            if client.check_token():
                return token
            else:
                raise NoSfdcSession()
        else:
            raise NoSfdcSession()
    except NoSession as e:
        raise NoSession()

    return None


def home_view(request):
    try:
        _nosession_check(request)
    except NoSession as e:
        return render(request, 'index.html', ENV)

    return HttpResponseRedirect(reverse('mytasks'))


def preferences(request):
    try:
        user_id = _nosession_check(request)
        preference = UserPreference.objects.get(okta_user_id=user_id)
        if request.method == 'POST':
            if preference:
                form = PreferenceForm(request.POST)
                if form.is_valid():
                    time_zone = form.cleaned_data['time_zone']
                    preference.time_zone = time_zone
                    preference.save()

                    # Save preferences into session
                    request.session['time_zone'] = preference.time_zone

                    # Save time zone preferece onto user profile

            return HttpResponseRedirect(reverse('mytasks'))
    except NoSession as e:
        return HttpResponseRedirect(reverse_lazy('home'))
    except Exception as e:
        print(e)

    return render(request, 'preferences.html', {'form': preference})


def task_action(request, p):
    try:
        response = HttpResponse()
        token = _forcecom_session_check(request)

        if request.method == 'POST':
            task = Task.objects.get(pk=p)
            if not task:
                response.status_code = 400
                return response

            j = json.loads(request.body)
            action = j['action']
            if not action:
                response.status_code = 400
                return response

            client = ForcedotcomClient(token)
            activity_date = task.start.strftime('%Y-%m-%-d')

            result = client.post_task(
                None,
                task.summary,
                activity_date,
                (task.end - task.start).total_seconds() / 60,
                action
            )
            status = result['status_code']
            if status >= 200:
                if status < 300:
                    task.status_code = 'C'
                    task.save()

    except NoSession as e:
        # return HttpResponseRedirect(reverse_lazy('home'))
        response.status_code = 401
    except NoSfdcSession as e:
        # return HttpResponseRedirect(reverse('forcecom_auth_init'))
        response.status_code = 401
    except Unauthorized as e:
        response.status_code = 401
    except Exception as e:
        response.status_code = 400

    return response


def task_view(request, p):
    task = None

    try:
        _nosession_check(request)

        if p != 'new':
            task = Task.objects.get(pk=p)

        if request.method == 'DELETE':
            if task:
                task.status_code = 'C'
                task.save()
            response = HttpResponse()
            response.status_code = 204
            return response
    except NoSession as e:
        return HttpResponseRedirect(reverse_lazy('home'))

    try:
        token = _forcecom_session_check(request)

        if request.method == 'POST':
            form = AddTaskForm(request.POST)
            if form.is_valid():
                client = ForcedotcomClient(token)
                activity_date = form.cleaned_data['activity_date'].strftime('%Y-%m-%-d')
                opportunity_id = form.cleaned_data['opportunity_id']

                # is_team_member = client.is_team_member(request.session['user_id'], opportunity_id)
                # print('is_team_member? {}'.format(is_team_member))

                result = client.post_task(
                    opportunity_id,
                    form.cleaned_data['subject'],
                    activity_date,
                    form.cleaned_data['time_spent'],
                    form.cleaned_data['task_type']
                )
                if task:
                    task.set_completed_time()

                    task.status_code = 'C'
                    task.opportunity = opportunity_id
                    task.subject = form.cleaned_data['subject']
                    task.time_spent = form.cleaned_data['time_spent']
                    task.type = form.cleaned_data['task_type']
                    task.save()

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
    except NoSession as e:
        return HttpResponseRedirect(reverse_lazy('home'))
    except NoSfdcSession or Unauthorized as e:
        return HttpResponseRedirect(reverse('forcecom_auth_init'))
    except Exception as e:
        print('There was an error: {}'.format(e.message))

    return render(request, 'task.html', {'form': form, 'id': p})


def my_tasks_view(request):
    try:
        user_id = _nosession_check(request)

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

    except NoSession as e:
        return HttpResponseRedirect(reverse_lazy('home'))

    return render(request, 'tasks.html', c)


def import_options_view(request):
    try:
        _nosession_check(request)
        form = ImportTaskForm()
    except NoSession as e:
        return HttpResponseRedirect(reverse_lazy('home'))

    return render(request, 'import_options.html', {'form': form})


def import_options_range_view(request):
    try:
        _nosession_check(request)
        form = ImportTaskForm()
    except NoSession as e:
        return HttpResponseRedirect(reverse_lazy('home'))

    return render(request, 'import_options_range.html', {'form': form})


def import_tasks(request):
    try:
        _nosession_check(request)

        if request.method == 'POST':
            form = ImportTaskForm(request.POST)
            if form.is_valid():
                import_range = form.cleaned_data['ImportRange']
                from_date = form.cleaned_data['FromDate']
                to_date = form.cleaned_data['ToDate']

                request.session['event_range'] = import_range
                if from_date:
                    request.session['event_from_date'] = from_date.strftime('%Y-%m-%d')
                if to_date:
                    request.session['event_to_date'] = to_date.strftime('%Y-%m-%d')

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

    except NoSession as e:
        return HttpResponseRedirect(reverse_lazy('home'))


def cronofy_oauth_callback(request):
    try:
        _nosession_check(request)
    except NoSession as e:
        return HttpResponseRedirect(reverse_lazy('home'))

    return render(request, 'cronofy_oauth_callback.html')


def cronofy_access_token(request):
    try:
        _nosession_check(request)
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

    except NoSession as e:
        return HttpResponseRedirect(reverse_lazy('home'))

    return HttpResponseRedirect(reverse_lazy('home'))


def _populate_tasks(request):
    token = request.session.get('cronofy_access_token')
    tzid = request.session.get('time_zone')
    login = request.session.get('login')
    user_id = request.session.get('user_id')
    event_range = request.session.get('event_range')

    if event_range is None or event_range == '' or event_range == 'None':
        to_date = request.session.get('event_to_date')
        from_date = request.session.get('event_from_date')
    else:
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
                if calendar['calendar_name'] == 'Calendar' and calendar['profile_name'].upper() == login.upper():
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
        events = client.get_events(params)

        skipped = 0
        added = 0
        for event in events:
            if not len(event['start']) == 10:
                task = Task.objects.filter(event_uid=event['event_uid'])
                if task:
                    skipped += 1
                else:
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
                    added += 1
    except Exception as e:
        print("There was an exception: {}".format(e))

    msg = 'Import summary: Added {} tasks'.format(added)
    if skipped > 0:
        msg += ', Skipped {} (already imported previously)'.format(skipped)
    messages.success(request, msg)
    return STATUS_CODES.SUCCESS


def forcecom_auth_init(request):
    try:
        _nosession_check(request)
    except NoSession as e:
        return HttpResponseRedirect(reverse_lazy('home'))

    return render(request, 'sfdc_auth_init.html')


def forcecom_auth_complete(request):
    try:
        _nosession_check(request)
    except NoSession as e:
        return HttpResponseRedirect(reverse_lazy('home'))

    return render(request, 'sfdc_auth_complete.html')


def forcecom_oauth_auth(request, task_id=None):
    try:
        _nosession_check(request)
        client = ForcedotcomOAuthClient()
    except NoSession as e:
        return HttpResponseRedirect(reverse_lazy('home'))

    return HttpResponseRedirect(client.auth_code(task_id))


def forcecom_oauth_callback(request):
    try:
        _nosession_check(request)
    except NoSession as e:
        return HttpResponseRedirect(reverse_lazy('home'))

    return render(request, 'forcecom_oauth_callback.html')


def forcecom_access_token(request):
    try:
        response = HttpResponse()
        _nosession_check(request)
    except NoSession as e:
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


def forcecom_search(request):
    try:
        status = 200
        reason = None
        token = _forcecom_session_check(request)
        client = ForcedotcomClient(token)

        if 'q' in request.GET:
            q = request.GET['q']
            opportunities = client.search_opportunities(q)
        else:
            opportunities = client.recent_opportunities()

        if len(opportunities) <= 0:
            opportunities.append({'Name': 'No results'})

        response = json.dumps({'opportunities': opportunities})

    except NoSession or NoSfdcSession as e:
        response = json.dumps({'opportunities': 'error'})
        status = 401
    except Exception as e:
        response = json.dumps({'opportunities': 'error'})
        status = e.status_code
        reason = e.message

    return HttpResponse(response, status=status, reason=reason, content_type='application/json; charset=utf8')

