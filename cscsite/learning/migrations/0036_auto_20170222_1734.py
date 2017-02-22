# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-02-22 14:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('learning', '0035_auto_20170222_1506'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudyProgramCourseGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('courses', models.ManyToManyField(related_name='study_programs', to=settings.AUTH_USER_MODEL, verbose_name='StudyProgramCourseGroup|courses')),
                ('study_program', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='learning.StudyProgram', verbose_name='Study Program')),
            ],
            options={
                'verbose_name_plural': 'Study Program Courses',
                'verbose_name': 'Study Program Course',
            },
        ),
        migrations.RemoveField(
            model_name='studyprogramcourse',
            name='course',
        ),
        migrations.RemoveField(
            model_name='studyprogramcourse',
            name='study_program',
        ),
        migrations.DeleteModel(
            name='StudyProgramCourse',
        ),
    ]
