# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-29 18:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0059_studentprofile_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='bio',
            field=models.TextField(blank=True, max_length=1000),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='website',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
