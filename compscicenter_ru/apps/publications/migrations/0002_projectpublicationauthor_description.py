# Generated by Django 2.1.8 on 2019-04-11 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectpublicationauthor',
            name='description',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Short Description'),
        ),
    ]