# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-05 17:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0088_auto_20160605_0207'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companyprofile',
            old_name='bio',
            new_name='company_bio',
        ),
        migrations.RenameField(
            model_name='companyprofile',
            old_name='application_website',
            new_name='company_website',
        ),
        migrations.RemoveField(
            model_name='companyprofile',
            name='is_company',
        ),
        migrations.AddField(
            model_name='companyprofile',
            name='number_of_tables',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='companyprofile',
            name='sponsor',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='companyprofile',
            name='number_of_representatives',
            field=models.IntegerField(default=1),
        ),
    ]
