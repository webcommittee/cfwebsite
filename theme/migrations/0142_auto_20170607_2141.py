# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-06-08 01:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0141_auto_20160922_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paypalinfo',
            name='friday_price',
            field=models.IntegerField(default=560, help_text="Friday's base fee.  THis includes the registration fee, one table, two reps, breakfast and lunch"),
        ),
        migrations.AlterField(
            model_name='paypalinfo',
            name='item_name',
            field=models.CharField(default='SHPE Company Career Fair Registration Fee 2017', help_text='What is the name of the item/service they are buying?', max_length=400),
        ),
        migrations.AlterField(
            model_name='paypalinfo',
            name='price_per_alumni_rep',
            field=models.IntegerField(default=100, help_text='Price per RPI alumni representative'),
        ),
        migrations.AlterField(
            model_name='paypalinfo',
            name='price_per_rep',
            field=models.IntegerField(default=100, help_text='Price per representative beyond the first two'),
        ),
        migrations.AlterField(
            model_name='paypalinfo',
            name='price_per_table',
            field=models.IntegerField(default=125, help_text='Price per table beyond the first'),
        ),
    ]
