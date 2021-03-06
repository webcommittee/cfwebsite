# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-02 06:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0133_auto_20160802_0207'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staffprofile',
            name='committee',
        ),
        migrations.AddField(
            model_name='committee',
            name='committee_members',
            field=models.ManyToManyField(related_name='Committee', to='theme.StaffProfile'),
        ),
        migrations.AddField(
            model_name='staffprofile',
            name='aboutpage',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='aboutpage', to='theme.AboutPage'),
        ),
    ]
