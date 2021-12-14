# Generated by Django 3.2.9 on 2021-12-14 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_user_yandex_login_normalized'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studentstatuslog',
            options={'verbose_name_plural': 'Student Status Log'},
        ),
        migrations.AddField(
            model_name='user',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Date of Birth'),
        ),
    ]
