# Generated by Django 2.2.1 on 2019-06-10 08:06

from django.db import migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0013_graduateprofile_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='graduateprofile',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='graduateprofile',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
    ]