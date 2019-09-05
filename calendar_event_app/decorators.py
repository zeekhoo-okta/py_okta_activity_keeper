from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from calendar_event_app.clients.ForcedotcomClient import ForcedotcomClient


def okta_login_required(func):
    def wrapper(request, *args, **kw):
        if 'user_id' not in request.session:
            if request.method == 'POST':
                response = HttpResponse()
                response.status_code = 401
                return response
            else:
                return HttpResponseRedirect(reverse_lazy('login'))
        else:
            return func(request, *args, **kw)
    return wrapper


def sfdc_login_required(func):
    def wrapper(request, *args, **kw):
        if 'forcecom_access_token' not in request.session:
            request_path = request.path.split('/')
            if request.method == 'DELETE' and len(request_path)>1 and request_path[1] == 'task':
                return func(request, *args, **kw)
            elif request.method == 'POST':
                response = HttpResponse()
                response.status_code = 401
                return response
            else:
                return HttpResponseRedirect(reverse('forcecom_auth_init'))
        else:
            token = request.session['forcecom_access_token']
            client = ForcedotcomClient(token)
            if client.check_token():
                return func(request, *args, **kw)
            else:
                if request.method == 'POST':
                    response = HttpResponse()
                    response.status_code = 401
                    return response
                else:
                    return HttpResponseRedirect(reverse('forcecom_auth_init'))
    return wrapper
