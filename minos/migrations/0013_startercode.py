# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-07-27 01:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minos', '0012_auto_20160714_2251'),
    ]

    operations = [
        migrations.CreateModel(
            name='StarterCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(max_length=20)),
                ('code', models.TextField()),
            ],
        ),
    ]
