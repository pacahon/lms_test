# Generated by Django 3.0.9 on 2021-02-11 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0033_auto_20201007_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseteacher',
            name='notify_by_default',
            field=models.BooleanField(default=True, verbose_name='Notifications'),
        ),
    ]
