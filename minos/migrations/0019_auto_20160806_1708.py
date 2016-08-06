# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-08-06 21:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('minos', '0018_rule'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClarificationAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ClarificationRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='minos.Question')),
            ],
        ),
        migrations.AddField(
            model_name='clarificationanswer',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='minos.ClarificationRequest'),
        ),
    ]
