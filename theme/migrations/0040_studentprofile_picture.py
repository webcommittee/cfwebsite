# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-26 19:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0039_remove_studentprofile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='picture',
            field=models.ImageField(blank=True, upload_to='uploads/student_images'),
        ),
    ]