# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-09 04:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0099_sponsoruspage_blurb'),
    ]

    operations = [
        migrations.RenameField(
            model_name='armorytabledata',
            old_name='reservations',
            new_name='friday_reservations',
        ),
        migrations.AddField(
            model_name='armorytabledata',
            name='saturday_reservations',
            field=models.TextField(null=True),
        ),
    ]