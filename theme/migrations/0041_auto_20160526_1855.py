# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-26 22:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0040_studentprofile_picture'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companyprofile',
            old_name='email',
            new_name='public_email',
        ),
    ]
