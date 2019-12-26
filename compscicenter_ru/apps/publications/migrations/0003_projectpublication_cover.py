# Generated by Django 2.2.7 on 2019-12-03 16:03

from django.db import migrations
import publications.models
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0002_auto_20190830_0814'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectpublication',
            name='cover',
            field=sorl.thumbnail.fields.ImageField(blank=True, help_text='Min height - 180px', upload_to=publications.models.publication_photo_upload_to, verbose_name='Cover'),
        ),
    ]