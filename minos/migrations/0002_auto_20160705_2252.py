# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-07-06 02:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('body', models.TextField()),
                ('division', models.CharField(choices=[('1', 'Division 1'), ('2', 'Division 2')], max_length=1)),
            ],
        ),
        migrations.DeleteModel(
            name='Greeting',
        ),
    ]
