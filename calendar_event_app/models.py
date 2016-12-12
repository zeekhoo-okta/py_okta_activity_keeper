from django.db import models
from django.conf import settings
from dateutil import tz

from_zone = tz.gettz(settings.TIME_ZONE)


class Task(models.Model):
    to_zone = tz.gettz('America/Los_Angeles')
    okta_user_id = models.CharField(db_index=True, max_length=100)
    calendar_id = models.CharField(max_length=100)
    event_uid = models.CharField(max_length=100, db_index=True, unique=True)
    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField(db_index=True)
    description = models.TextField(blank=True)
    summary = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=100, blank=True)
    due_date = models.DateField(null=True, blank=True)
    time_spent = models.IntegerField(null=True, blank=True)
    status_code = models.CharField(max_length=2)

    class Meta:
        db_table = "task"

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
        newstring = self.description.replace("\r\n", '<br/>')
        arr = newstring.split('<br/>')
        return arr

    def start_date_local(self):
        utc = self.start.replace(tzinfo=from_zone)
        local = utc.astimezone(self.to_zone)
        return local.date().strftime('%a %B %-d %Y')


class UserPreference(models.Model):
    okta_user_id = models.CharField(db_index=True, max_length=100, unique=True)
    time_zone = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "user_preference"
