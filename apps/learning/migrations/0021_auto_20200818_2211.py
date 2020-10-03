# Generated by Django 3.0.9 on 2020-08-18 22:11

from django.db import migrations
import files.models
import learning.models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0020_auto_20200625_2102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentcomment',
            name='attached_file',
            field=files.models.ConfigurableStorageFileField(blank=True, max_length=150, upload_to=learning.models.assignment_submission_attachment_upload_to),
        ),
    ]
