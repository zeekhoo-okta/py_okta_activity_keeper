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

from calendar_event_app.views import home_view, login_session, logout, api_view, task_view, my_tasks_view
from calendar_event_app.views import import_options_view, import_tasks, cronofy_oauth_callback, cronofy_access_token
from calendar_event_app.views import forcecom_oauth_callback, forcecom_access_token, forcecom_oauth_auth, forcecom_recent


urlpatterns = [
    # django admin
    url(r'^admin/', admin.site.urls),

    # home, login, logout
    url(r'^$', home_view, name='home'),
    url(r'^login/$', login_session, name='login'),
    url(r'^logout/$', logout, name='logout'),

    # task
    url(r'^task/([a-zA-Z0-9]+)/$', task_view, name='task'),
    url(r'^task/new/$', task_view, name='addtask'),
    url(r'^task/$', my_tasks_view, name='mytasks'),


    # cronofy
    url(r'^import_options/$', import_options_view, name='import_options'),
    url(r'^import_tasks/$', import_tasks, name='import_tasks'),
    url(r'^cronofy/oauth/callback/$', cronofy_oauth_callback, name='cronofy_oauth_callback'),
    url(r'^cronofy/oauth/token/$', cronofy_access_token, name='cronofy_access_token'),

    # force.com
    url(r'^sfdc/oauth/callback/$', forcecom_oauth_callback, name='forcecom_oauth_callback'),
    url(r'^sfdc/oauth/token/$', forcecom_access_token, name='forcecom_access_token'),
    url(r'^sfdc/oauth/auth/$', forcecom_oauth_auth, name='forcecom_oauth_auth'),
    url(r'^sfdc/recent/$', forcecom_recent, name='forcecom_recent'),

    # api view
    url(r'^debug/$', api_view.as_view(), name='api_view'),
]
