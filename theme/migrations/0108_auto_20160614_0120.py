# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-14 05:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0107_auto_20160614_0048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyprofile',
            name='company',
            field=models.CharField(max_length=60),
        ),
        migrations.RemoveField(
            model_name='companyprofile',
            name='reps',
        ),
        migrations.AddField(
            model_name='companyprofile',
            name='reps',
            field=models.ManyToManyField(related_name='reps', to='theme.CompanyRep'),
        ),
        migrations.RemoveField(
            model_name='companyprofile',
            name='reps_alumni',
        ),
        migrations.AddField(
            model_name='companyprofile',
            name='reps_alumni',
            field=models.ManyToManyField(related_name='alumni', to='theme.CompanyRep'),
        ),
    ]
