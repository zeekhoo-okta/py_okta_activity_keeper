from django.db import models
from django.conf import settings
from dateutil import tz
from datetime import datetime
import requests

from_zone = tz.gettz(settings.TIME_ZONE)
ama_la = 'America/Los_Angeles'


class Task(models.Model):
    to_zone = tz.gettz(ama_la)

    okta_user_id = models.CharField(db_index=True, max_length=100)
    calendar_id = models.CharField(max_length=100)
    event_uid = models.CharField(max_length=100, db_index=True, unique=True)
    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField(db_index=True)
    description = models.TextField(blank=True)
    summary = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True)
    organizer = models.CharField(max_length=100, blank=True)
    attendees = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=100, blank=True)
    due_date = models.DateField(null=True, blank=True)
    time_spent = models.IntegerField(null=True, blank=True)
    status_code = models.CharField(max_length=2)
    opportunity = models.CharField(max_length=100, blank=True)
    completed_time = models.CharField(max_length=19, blank=True)

    class Meta:
        db_table = "task"
        index_together = [
            ["okta_user_id", "status_code"],
        ]

    def set_tz(self, zone):
        self.to_zone = tz.gettz(zone)

    def start_time(self):
        utc = self.start.replace(tzinfo=from_zone)
        local = utc.astimezone(self.to_zone)
        return local.time().strftime('%I:%M %p')

    def end_time(self):
        utc = self.end.replace(tzinfo=from_zone)
        local = utc.astimezone(self.to_zone)
        return local.time().strftime('%I:%M %p')

    def desc(self):
        desc = 'Organizer: ' + self.organizer + '<br/>'\
               + 'Attendees: ' + self.attendees + '<br/><br/>'\
               + self.description.replace("\r\n", '<br/>')
        arr = desc.split('<br/>')
        return arr

    def start_date_local(self):
        utc = self.start.replace(tzinfo=from_zone)
        local = utc.astimezone(self.to_zone)
        return local.date().strftime('%a %B %-d %Y')

    def set_completed_time(self):
        curr = datetime.now().strftime('%Y-%m-%d %I:%M %p')
        # UTC current time
        self.completed_time = curr


class UserPreference(models.Model):
    okta_user_id = models.CharField(db_index=True, max_length=100, unique=True)
    time_zone = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "user_preference"


class StatusCodes(object):
    def __init__(self):
        self.NO_TOKEN = 'NO_TOKEN'
        self.NO_CALENDAR = 'NO_CALENDAR'
        self.SUCCESS = 'SUCCESS'


# class Config:
#     def __init__(self):
#         self.org_url = 'https://{}'.format(settings.OKTA_ORG)
#         self.grant_type = 'authorization_code'
#         self.client_id = settings.CLIENT_ID
#         self.client_secret = settings.CLIENT_SECRET
#         self.issuer = settings.ISSUER
#         self.scopes = 'openid profile'
#         self.redirect_uri = '{}/oidc/callback'.format(settings.APP_URL)


# class DiscoveryDocument:
#     # Find the OIDC metadata through discovery
#     def __init__(self, issuer_uri):
#         r = requests.get(issuer_uri + "/.well-known/openid-configuration")
#         self.json = r.json()
#
#     def getJson(self):
#         return self.json
