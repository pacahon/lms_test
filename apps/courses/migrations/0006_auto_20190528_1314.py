# Generated by Django 2.2.1 on 2019-05-28 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_auto_20190426_1339'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='semester',
            name='projects_grade_excellent',
        ),
        migrations.RemoveField(
            model_name='semester',
            name='projects_grade_good',
        ),
        migrations.RemoveField(
            model_name='semester',
            name='projects_grade_pass',
        ),
        migrations.RemoveField(
            model_name='semester',
            name='report_ends_at',
        ),
        migrations.RemoveField(
            model_name='semester',
            name='report_starts_at',
        ),
    ]
