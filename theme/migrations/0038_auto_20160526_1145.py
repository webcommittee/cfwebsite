# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-26 15:45
from __future__ import unicode_literals

from django.db import migrations, models
import theme.validators


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0037_auto_20160526_0536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprofile',
            name='resume',
            field=models.FileField(blank=True, upload_to='resumes', validators=[theme.validators.validate_file_extension]),
        ),
    ]