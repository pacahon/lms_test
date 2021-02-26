# Generated by Django 2.2.10 on 2020-03-30 15:31
import core.timezone.fields
import core.timezone.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0004_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursesurvey',
            name='expire_at',
            field=core.timezone.fields.TimezoneAwareDateTimeField(help_text="With published selected, won't be shown after this time. Datetime should be specified in the timezone of the root course branch. Students will see deadline in MSK timezone", verbose_name='Expires on'),
        ),
    ]
