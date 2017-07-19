# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-05 05:30
from __future__ import unicode_literals

from django.db import migrations, models
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0083_auto_20160604_2153'),
    ]

    operations = [
        migrations.CreateModel(
            name='PayPalInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(help_text='The email account associated with whatever paypal account you plan on using', max_length=254)),
                ('friday_price', models.IntegerField(help_text="Friday's price")),
                ('saturday_price', models.IntegerField(help_text="Saturday's price")),
                ('price_per_rep', models.IntegerField(help_text='Price per representative')),
                ('price_per_alumni_rep', models.IntegerField(help_text='Price per RPI alumni representative')),
            ],
        ),
        migrations.RemoveField(
            model_name='sponsoruspage',
            name='contact',
        ),
        migrations.AlterField(
            model_name='sponsoruspage',
            name='text',
            field=mezzanine.core.fields.RichTextField(default='', help_text='The big blob of text under the heading', max_length=3000),
        ),
    ]