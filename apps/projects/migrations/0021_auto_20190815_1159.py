# Generated by Django 2.2.4 on 2019-08-15 11:59

from django.db import migrations


def sync_branch(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')
    Branch = apps.get_model('core', 'Branch')
    for o in Project.objects.all():
        if o.city_id:
            o.branch = Branch.objects.get(code=o.city_id, site_id=1)
            o.save(update_fields=['branch'])


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0020_auto_20190814_1524'),
    ]

    operations = [
        migrations.RunPython(sync_branch)
    ]
