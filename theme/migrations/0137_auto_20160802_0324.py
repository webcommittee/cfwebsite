# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-02 07:24
from __future__ import unicode_literals

from django.db import migrations, models
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0136_auto_20160802_0253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='answer',
            field=mezzanine.core.fields.RichTextField(null=True, verbose_name='Answer'),
        ),
        migrations.AlterField(
            model_name='question',
            name='question',
            field=models.CharField(default='Question', max_length=500, verbose_name='Question'),
        ),
    ]
