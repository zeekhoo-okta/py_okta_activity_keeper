# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-24 01:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendar_event_app', '0014_task_completed_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='completed_time',
            field=models.CharField(blank=True, max_length=19),
        ),
    ]
