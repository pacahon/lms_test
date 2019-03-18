# Generated by Django 2.1.5 on 2019-03-18 11:26

import courses.models
from django.db import migrations, models
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_assignment_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='metacourse',
            name='cover',
            field=sorl.thumbnail.fields.ImageField(blank=True, upload_to=courses.models.meta_course_cover_upload_to, verbose_name='MetaCourse|cover'),
        ),
        migrations.AddField(
            model_name='metacourse',
            name='short_description',
            field=models.TextField(blank=True, verbose_name='Course|short_description'),
        ),
        migrations.AddField(
            model_name='metacourse',
            name='short_description_en',
            field=models.TextField(blank=True, null=True, verbose_name='Course|short_description'),
        ),
        migrations.AddField(
            model_name='metacourse',
            name='short_description_ru',
            field=models.TextField(blank=True, null=True, verbose_name='Course|short_description'),
        ),
    ]
