# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-28 04:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0047_auto_20160528_0034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='armorytabledata',
            name='dimension_x',
        ),
        migrations.RemoveField(
            model_name='armorytabledata',
            name='dimension_y',
        ),
    ]