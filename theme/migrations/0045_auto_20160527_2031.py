# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-28 00:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0044_auto_20160527_1721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyprofile',
            name='public_email',
            field=models.EmailField(blank=True, max_length=120),
        ),
        migrations.AlterField(
            model_name='companyprofile',
            name='public_phone_number',
            field=models.CharField(blank=True, max_length=12),
        ),
    ]