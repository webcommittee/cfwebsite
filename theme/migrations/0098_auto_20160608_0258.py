# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-08 06:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0097_auto_20160608_0232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyprofile',
            name='interview_friday_from',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='companyprofile',
            name='interview_friday_to',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='companyprofile',
            name='interview_saturday_from',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='companyprofile',
            name='interview_saturday_to',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
