# Generated by Django 2.1.1 on 2018-10-16 17:20

from django.db import migrations

from surveys.constants import COURSE_FORM_TEMPLATES, STATUS_TEMPLATE


def fix_templates(apps, schema_editor):
    Form = apps.get_model('surveys', 'Form')
    for form_template in COURSE_FORM_TEMPLATES:
        Form.objects.filter(slug=form_template).update(status=STATUS_TEMPLATE)


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0005_auto_20181016_1719'),
    ]

    operations = [
        migrations.RunPython(fix_templates),
    ]
