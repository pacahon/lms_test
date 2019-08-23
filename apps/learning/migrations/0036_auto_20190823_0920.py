# Generated by Django 2.2.4 on 2019-08-23 09:20

from django.db import migrations


def copy_venues(apps, schema_editor):
    Branch = apps.get_model('core', 'Branch')
    Event = apps.get_model('learning', 'Event')
    for event in Event.objects.select_related('venue'):
        code = event.venue.city_id
        if code == 'online':
            code = 'distance'
        event.branch = Branch.objects.get(code=code, site_id=1)
        event.save(update_fields=['branch'])


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0035_auto_20190823_0920'),
    ]

    operations = [
        migrations.RunPython(copy_venues)
    ]
