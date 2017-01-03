"""record_time URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from calendar_event_app.views import home_view, login_session, logout, register, registration_success,\
    task_view, my_tasks_view, preferences
from calendar_event_app.views import import_options_view, import_tasks, cronofy_oauth_callback, cronofy_access_token
from calendar_event_app.views import forcecom_oauth_callback, forcecom_access_token, forcecom_search
from calendar_event_app.views import forcecom_auth_init, forcecom_auth_complete, forcecom_oauth_auth
from calendar_event_app.views import task_action

from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    # django admin
    url(r'^admin/', admin.site.urls),

    # home, login, logout
    url(r'^$', home_view, name='home'),
    url(r'^login/$', login_session, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^register/$', register, name='register'),
    url(r'^register/success/$', registration_success, name='registration_success'),
    url(r'^preferences/$', preferences, name='preferences'),

    # task
    url(r'^task/([a-zA-Z0-9]+)/$', task_view, name='task'),
    url(r'^task/new/$', task_view, name='addtask'),
    url(r'^task/$', my_tasks_view, name='mytasks'),
    url(r'^taskaction/([a-zA-Z0-9]+)/$', task_action, name='action'),

    # cronofy
    url(r'^import_options/$', import_options_view, name='import_options'),
    url(r'^import_tasks/$', import_tasks, name='import_tasks'),
    url(r'^cronofy/oauth/callback/$', cronofy_oauth_callback, name='cronofy_oauth_callback'),
    url(r'^cronofy/oauth/token/$', cronofy_access_token, name='cronofy_access_token'),

    # force.com
    url(r'^sfdc/oauth/callback/$', forcecom_oauth_callback, name='forcecom_oauth_callback'),
    url(r'^sfdc/oauth/token/$', forcecom_access_token, name='forcecom_access_token'),
    url(r'^sfdc/oauth/init/$', forcecom_auth_init, name='forcecom_auth_init'),
    url(r'^sfdc/oauth/complete/$', forcecom_auth_complete, name='forcecom_auth_complete'),
    url(r'^sfdc/oauth/auth/[0-9]*$', forcecom_oauth_auth, name='forcecom_oauth_auth'),
    url(r'^sfdc/search/$', forcecom_search, name='forcecom_search'),
]

urlpatterns += staticfiles_urlpatterns()