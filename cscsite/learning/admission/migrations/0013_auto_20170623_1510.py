# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-23 12:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0012_interviewinvitation_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='interviewinvitation',
            options={'verbose_name': 'Interview invitation', 'verbose_name_plural': 'Interview invitations'},
        ),
        migrations.AddField(
            model_name='interviewinvitation',
            name='interview',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='admission.Interview', verbose_name='Interview'),
        ),
    ]
