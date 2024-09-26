# Generated by Django 3.2.18 on 2024-08-27 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0048_course_hours'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='translation_link',
            field=models.URLField(blank=True, verbose_name='Translation link'),
        ),
        migrations.AddField(
            model_name='courseclass',
            name='recording_link',
            field=models.URLField(blank=True, verbose_name='Recording link'),
        ),
        migrations.AddField(
            model_name='courseclass',
            name='translation_link',
            field=models.URLField(blank=True, verbose_name='Translation link'),
        ),
        migrations.AlterField(
            model_name='course',
            name='default_grade',
            field=models.CharField(choices=[('without_grade', 'Without Grade'), ('not_graded', 'Not graded')], default='not_graded', max_length=100, verbose_name='Enrollment|default_grade'),
        ),
        migrations.AlterField(
            model_name='courseclass',
            name='type',
            field=models.CharField(choices=[('lecture', 'Lecture'), ('seminar', 'Seminar'), ('lecture_and_seminar', 'Lecture and seminar'), ('invited_lecture', 'Invited lecture')], max_length=100, verbose_name='Type'),
        ),
    ]