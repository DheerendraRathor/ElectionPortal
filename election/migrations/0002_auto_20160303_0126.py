# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-02 19:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='display_manifesto',
            field=models.BooleanField(default=True, help_text='Display manifestos for candidates if present'),
        ),
        migrations.AddField(
            model_name='historicalelection',
            name='display_manifesto',
            field=models.BooleanField(default=True, help_text='Display manifestos for candidates if present'),
        ),
    ]
