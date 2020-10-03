# Generated by Django 2.2.4 on 2019-08-30 08:14

import core.db.models
import core.timezone.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import learning.models
import model_utils.fields
import sorl.thumbnail.fields
import users.thumbnails


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('text', models.TextField(blank=True, help_text='LaTeX+Markdown is enabled', verbose_name='AssignmentComment|text')),
                ('attached_file', models.FileField(blank=True, max_length=150, upload_to=learning.models.assignment_submission_attachment_upload_to)),
            ],
            options={
                'verbose_name': 'Assignment-comment',
                'verbose_name_plural': 'Assignment-comments',
                'ordering': ['created'],
            },
            bases=(core.timezone.models.TimezoneAwareModel, models.Model),
        ),
        migrations.CreateModel(
            name='AssignmentNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_about_passed', models.BooleanField(default=False, verbose_name='About passed assignment')),
                ('is_about_creation', models.BooleanField(default=False, verbose_name='About created assignment')),
                ('is_about_deadline', models.BooleanField(default=False, verbose_name='About change of deadline')),
                ('is_unread', models.BooleanField(default=True, verbose_name='Unread')),
                ('is_notified', models.BooleanField(default=False, verbose_name='User is notified')),
            ],
            options={
                'verbose_name': 'Assignment notification',
                'verbose_name_plural': 'Assignment notifications',
                'ordering': ['-created'],
            },
            bases=(core.timezone.models.TimezoneAwareModel, models.Model),
        ),
        migrations.CreateModel(
            name='CourseInvitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=128, verbose_name='Token')),
            ],
            options={
                'verbose_name': 'Enrollment Invitation',
                'verbose_name_plural': 'Enrollment Invitations',
            },
        ),
        migrations.CreateModel(
            name='CourseNewsNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_unread', models.BooleanField(default=True, verbose_name='Unread')),
                ('is_notified', models.BooleanField(default=False, verbose_name='User is notified')),
            ],
            options={
                'verbose_name': 'Course offering news notification',
                'verbose_name_plural': 'Course offering news notifications',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('grade', models.CharField(choices=[('not_graded', 'Not graded'), ('unsatisfactory', 'Enrollment|Unsatisfactory'), ('pass', 'Enrollment|Pass'), ('good', 'Good'), ('excellent', 'Excellent')], default='not_graded', max_length=100, verbose_name='Enrollment|grade')),
                ('grade_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='grade', verbose_name='Enrollment|grade changed')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='The student left the course')),
                ('reason_entry', models.TextField(blank=True, verbose_name='Entry reason')),
                ('reason_leave', models.TextField(blank=True, verbose_name='Leave reason')),
            ],
            options={
                'verbose_name': 'Enrollment',
                'verbose_name_plural': 'Enrollments',
            },
            bases=(core.timezone.models.TimezoneAwareModel, models.Model),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=255, verbose_name='CourseClass|Name')),
                ('description', models.TextField(blank=True, help_text='How to style text read <a href="/commenting-the-right-way/" target="_blank">here</a>. Partially HTML is enabled too.', verbose_name='Description')),
                ('date', models.DateField(verbose_name='Date')),
                ('starts_at', models.TimeField(verbose_name='Starts at')),
                ('ends_at', models.TimeField(verbose_name='Ends at')),
            ],
            options={
                'verbose_name': 'Non-course event',
                'verbose_name_plural': 'Non-course events',
                'ordering': ('-date', '-starts_at', 'name'),
            },
        ),
        migrations.CreateModel(
            name='GraduateProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activity')),
                ('graduated_on', models.DateField(help_text='Graduation ceremony date', verbose_name='Graduated on')),
                ('graduation_year', models.PositiveSmallIntegerField(editable=False, help_text='Helps filtering by year', verbose_name='Graduation Year')),
                ('photo', sorl.thumbnail.fields.ImageField(blank=True, upload_to=learning.models.graduate_photo_upload_to, verbose_name='Photo')),
                ('testimonial', models.TextField(blank=True, help_text='Testimonial about Computer Science Center', verbose_name='Testimonial')),
                ('details', core.db.models.PrettyJSONField(blank=True, verbose_name='Details')),
            ],
            options={
                'verbose_name': 'Graduate Profile',
                'verbose_name_plural': 'Graduate Profiles',
            },
            bases=(users.thumbnails.UserThumbnailMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('token', models.CharField(max_length=128, verbose_name='Token')),
            ],
            options={
                'verbose_name': 'Invitation',
                'verbose_name_plural': 'Invitations',
            },
        ),
        migrations.CreateModel(
            name='Useful',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255, verbose_name='Question')),
                ('answer', models.TextField(verbose_name='Answer')),
                ('sort', models.SmallIntegerField(blank=True, null=True, verbose_name='Sort order')),
                ('site', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='sites.Site', verbose_name='Site')),
            ],
            options={
                'verbose_name': 'Useful',
                'verbose_name_plural': 'Useful',
                'ordering': ['sort'],
            },
        ),
        migrations.CreateModel(
            name='StudentAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('score', core.db.models.ScoreField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Grade')),
                ('score_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='score', verbose_name='Assignment|grade changed')),
                ('first_student_comment_at', models.DateTimeField(editable=False, null=True, verbose_name='First Student Comment At')),
                ('last_comment_from', models.PositiveSmallIntegerField(choices=[(0, 'NOBODY'), (1, 'STUDENT'), (2, 'TEACHER')], default=0, editable=False, verbose_name='The author type of the latest comment')),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Assignment', verbose_name='StudentAssignment|assignment')),
            ],
            options={
                'verbose_name': 'Assignment-student',
                'verbose_name_plural': 'Assignment-students',
                'ordering': ['assignment', 'student'],
            },
            bases=(core.timezone.models.TimezoneAwareModel, models.Model),
        ),
    ]
