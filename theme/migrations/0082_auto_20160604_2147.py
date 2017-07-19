# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-05 01:47
from __future__ import unicode_literals

from django.db import migrations, models
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0081_auto_20160604_2131'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companyprofile',
            name='alumni_reps',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='misc_info_redirect',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='misc_info_redirect_text',
        ),
        migrations.AddField(
            model_name='companyprofile',
            name='reps_alumni',
            field=models.TextField(default='', null=True),
        ),
        migrations.AddField(
            model_name='companyprofile',
            name='total_bill',
            field=models.IntegerField(default=500),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='misc_info_body',
            field=mezzanine.core.fields.RichTextField(default='About us', help_text='Body for misc info field', max_length=2000),
        ),
    ]