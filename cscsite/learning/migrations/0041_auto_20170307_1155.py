# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-07 08:55
from __future__ import unicode_literals

from django.db import migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0040_remove_studyprogram_sort'),
    ]

    operations = [
        migrations.AddField(
            model_name='studyprogram',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='studyprogram',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
    ]
