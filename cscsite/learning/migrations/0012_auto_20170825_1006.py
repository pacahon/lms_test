# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-25 10:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0011_auto_20170825_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semester',
            name='enrollment_start_at',
            field=models.DateField(blank=True, help_text='Leave blank to fill in with the date of the beginning of the term', null=True, verbose_name='Enrollment start at'),
        ),
        migrations.AlterField(
            model_name='semester',
            name='enrollment_end_at',
            field=models.DateField(blank=True, help_text='Students can enroll on or leave the course before this date (inclusive)', null=True, verbose_name='Enrollment end at'),
        ),
    ]