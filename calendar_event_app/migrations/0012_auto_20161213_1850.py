# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-13 18:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calendar_event_app', '0011_auto_20161213_1849'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='task',
            index_together=set([('okta_user_id', 'status_code')]),
        ),
    ]
