# Generated by Django 3.0.9 on 2020-09-29 15:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0031_auto_20200929_1522'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('learning', '0027_auto_20200922_0849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentgroup',
            name='type',
            field=models.CharField(choices=[('system', 'System'), ('manual', 'Manual'), ('branch', 'Branch')], default='branch', max_length=100, verbose_name='Type'),
        ),
        migrations.CreateModel(
            name='StudentGroupAssignee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Assignee')),
                ('assignment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.Assignment', verbose_name='Assignment')),
                ('student_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning.StudentGroup', verbose_name='Student Group')),
            ],
            options={
                'verbose_name': 'Student Group Assignee',
                'verbose_name_plural': 'Student Group Assignees',
            },
        ),
        migrations.AddConstraint(
            model_name='studentgroupassignee',
            constraint=models.UniqueConstraint(fields=('student_group', 'assignee', 'assignment'), name='unique_assignee_per_student_or_assignment_group'),
        ),
    ]
