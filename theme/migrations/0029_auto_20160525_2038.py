# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-26 00:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0028_auto_20160525_2033'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companyprofile',
            old_name='User',
            new_name='user',
        ),
    ]