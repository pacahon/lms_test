# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-21 13:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admission_test', '0002_auto_20180220_1336'),
    ]

    operations = [
        migrations.AddField(
            model_name='admissiontestapplicant',
            name='status_code',
            field=models.IntegerField(blank=True, editable=False, null=True, verbose_name='Yandex API Response'),
        ),
    ]