# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-25 15:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0017_auto_20160525_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyprofile',
            name='has_submitted_payment',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='companyprofile',
            name='is_company',
            field=models.BooleanField(default=True),
        ),
    ]