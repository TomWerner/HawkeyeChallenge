# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-07-14 00:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minos', '0005_submission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='submission_time',
            field=models.DateTimeField(),
        ),
    ]
