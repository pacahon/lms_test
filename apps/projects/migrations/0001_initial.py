# Generated by Django 2.2.4 on 2019-08-30 08:14
import core.db.fields
import core.db.mixins
import core.db.models
import core.timezone.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import projects.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='PracticeCriteria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score_global_issue', models.PositiveSmallIntegerField(blank=True, choices=[(0, '0 - Does not understand the task at all'), (1, '1 - Understands, but very superficial'), (2, '2 - Understands everything')], null=True, verbose_name='The global task for term')),
                ('score_usefulness', models.PositiveSmallIntegerField(blank=True, choices=[(0, '0 - Does not understand'), (1, '1 - Writing something about the usefulness'), (2, '2 - Understands and explains')], null=True, verbose_name='Possible uses and scenarios')),
                ('score_progress', models.PositiveSmallIntegerField(blank=True, choices=[(0, '0 - Understand only theory, or even less'), (1, '1 - Some progress, but not enough'), (2, '2 - The normal rate of work')], null=True, verbose_name='What has been done since the start of the project.')),
                ('score_problems', models.PositiveSmallIntegerField(blank=True, choices=[(0, '0 - Problems not mentioned in the report'), (1, '1 - Problems are mentioned without any details'), (2, '2 - Problems are mentioned and explained how they been solved')], null=True, verbose_name='What problems have arisen in the process.')),
                ('score_technologies', models.PositiveSmallIntegerField(blank=True, choices=[(0, '0 - Listed, but not explained why.'), (1, '1 - The student does not understand about everything and does not try to understand, but knows something'), (2, '2 - Understands why choose one or the other technology')], null=True, verbose_name='The choice of technologies or method of integration with the existing development')),
                ('score_plans', models.PositiveSmallIntegerField(blank=True, choices=[(0, '0 - Much less than what has already been done, or the student does not understand them'), (1, '1 - It seems to have plans of normal size, but does not understand what to do.'), (2, '2 - All right with them')], null=True, verbose_name='Future plan')),
                ('score_global_issue_note', models.TextField(blank=True, null=True, verbose_name='Note for criterion #1')),
                ('score_usefulness_note', models.TextField(blank=True, null=True, verbose_name='Note for criterion #2')),
                ('score_progress_note', models.TextField(blank=True, null=True, verbose_name='Note for criterion #3')),
                ('score_problems_note', models.TextField(blank=True, null=True, verbose_name='Note for criterion #4')),
                ('score_technologies_note', models.TextField(blank=True, null=True, verbose_name='Note for criterion #5')),
                ('score_plans_note', models.TextField(blank=True, null=True, verbose_name='Note for criterion #6')),
            ],
            options={
                'verbose_name': 'Practice Criteria',
                'verbose_name_plural': 'Practice Criteria',
            },
            bases=(projects.models.CriteriaScoresMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=255, verbose_name='StudentProject|Name')),
                ('project_type', models.CharField(choices=[('practice', 'StudentProject|Practice'), ('research', 'StudentProject|Research')], max_length=10, verbose_name='StudentProject|Type')),
                ('is_external', models.BooleanField(default=False, verbose_name='External project')),
                ('status', models.CharField(blank=True, choices=[('canceled', 'Canceled'), ('continued', 'Continued without intermediate results')], max_length=10, null=True, verbose_name='StudentProject|Status')),
                ('description', models.TextField(blank=True, help_text='How to style text read <a href="/commenting-the-right-way/" target="_blank">here</a>. Partially HTML is enabled too.', verbose_name='Description')),
                ('supervisor', models.CharField(help_text='Format: Last_name First_name Patronymic, Organization', max_length=255, verbose_name='StudentProject|Supervisor')),
                ('supervisor_presentation', models.FileField(blank=True, upload_to=projects.models.project_presentations_upload_to, verbose_name='Supervisor presentation')),
                ('supervisor_presentation_url', models.URLField(blank=True, help_text='Supported public link to Yandex.Disk only', null=True, verbose_name='Link to supervisor presentation')),
                ('supervisor_presentation_slideshare_url', models.URLField(blank=True, null=True, verbose_name='SlideShare URL for supervisor presentation')),
                ('presentation', models.FileField(blank=True, upload_to=projects.models.project_presentations_upload_to, verbose_name='Participants presentation')),
                ('presentation_url', models.URLField(blank=True, help_text='Supported public link to Yandex.Disk only', null=True, verbose_name='Link to participants presentation')),
                ('presentation_slideshare_url', models.URLField(blank=True, null=True, verbose_name='SlideShare URL for participants presentation')),
            ],
            options={
                'verbose_name': 'Student project',
                'verbose_name_plural': 'Student projects',
            },
            bases=(core.timezone.models.TimezoneAwareMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ProjectStudent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('supervisor_grade', models.SmallIntegerField(blank=True, help_text='Integer value from -15 to 15', null=True, validators=[django.core.validators.MinValueValidator(-15), django.core.validators.MaxValueValidator(15)], verbose_name='Supervisor grade')),
                ('supervisor_review', models.TextField(blank=True, verbose_name='Review from supervisor')),
                ('presentation_grade', models.PositiveSmallIntegerField(blank=True, help_text='Integer value from 0 to 10', null=True, validators=[django.core.validators.MaxValueValidator(10)], verbose_name='Presentation grade')),
                ('final_grade', models.CharField(choices=[('not_graded', 'Not graded'), ('unsatisfactory', 'Enrollment|Unsatisfactory'), ('pass', 'Enrollment|Pass'), ('good', 'Good'), ('excellent', 'Excellent')], default='not_graded', max_length=15, verbose_name='Final grade')),
            ],
            options={
                'verbose_name': 'Project student',
                'verbose_name_plural': 'Project students',
            },
            bases=(core.timezone.models.TimezoneAwareMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('status', models.CharField(choices=[('sent', 'New Report'), ('review', 'Review'), ('rating', 'Waiting for final score'), ('completed', 'Completed')], default='sent', max_length=15, verbose_name='Status')),
                ('text', models.TextField(blank=True, help_text='How to style text read <a href="/commenting-the-right-way/" target="_blank">here</a>. Partially HTML is enabled too.', verbose_name='Description')),
                ('file', models.FileField(blank=True, null=True, upload_to=projects.models.report_file_upload_to, verbose_name='Report file')),
                ('score_activity', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Poor commit history'), (1, 'Normal activity')], null=True, validators=[django.core.validators.MaxValueValidator(1)], verbose_name='Student activity in cvs')),
                ('score_activity_note', models.TextField(blank=True, null=True, verbose_name='Note for criterion `score_activity`')),
                ('score_quality', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Bad report quality and unrelated comments'), (1, 'Bad report quality, but sensible comments'), (2, 'Good report quality and sensible comments')], null=True, validators=[django.core.validators.MaxValueValidator(2)], verbose_name="Report's quality")),
                ('score_quality_note', models.TextField(blank=True, null=True, verbose_name='Note for criterion `score_quality`')),
                ('final_score', core.db.fields.ScoreField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Final Score')),
                ('final_score_note', models.TextField(blank=True, null=True, verbose_name='Final score note')),
            ],
            options={
                'verbose_name': 'Reports',
                'verbose_name_plural': 'Reports',
            },
            bases=(core.timezone.models.TimezoneAwareMixin, core.db.mixins.DerivableFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ReportComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('text', models.TextField(blank=True, help_text='LaTeX+Markdown is enabled', verbose_name='ReportComment|text')),
                ('attached_file', models.FileField(blank=True, upload_to=projects.models.report_comment_attachment_upload_to)),
            ],
            options={
                'verbose_name': 'Report comment',
                'verbose_name_plural': 'Report comments',
                'ordering': ['created'],
            },
            bases=(core.timezone.models.TimezoneAwareMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ReportingPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, help_text='Helps to distinguish student reports for the project.', max_length=150, verbose_name='Label')),
                ('start_on', models.DateField(help_text='First day of the report period.', verbose_name='Start On')),
                ('end_on', models.DateField(help_text='The last day of the report period.', verbose_name='End On')),
                ('project_type', models.CharField(blank=True, choices=[('practice', 'StudentProject|Practice'), ('research', 'StudentProject|Research')], max_length=10, null=True, verbose_name='StudentProject|Type')),
                ('score_excellent', models.SmallIntegerField(blank=True, help_text='Projects with final score >= this value will be graded as Excellent', null=True, verbose_name='Min score for EXCELLENT')),
                ('score_good', models.SmallIntegerField(blank=True, help_text='Projects with final score in [GOOD; EXCELLENT) will be graded as Good.', null=True, verbose_name='Min score for GOOD')),
                ('score_pass', models.SmallIntegerField(blank=True, help_text='Projects with final score in [PASS; GOOD) will be graded as Pass, with score < PASS as Unsatisfactory.', null=True, verbose_name='Min score for PASS')),
            ],
            options={
                'verbose_name': 'Reporting Period',
                'verbose_name_plural': 'Reporting Periods',
            },
        ),
        migrations.CreateModel(
            name='Supervisor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255, verbose_name='Full Name')),
                ('workplace', models.CharField(blank=True, max_length=200, verbose_name='Workplace')),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('o', 'Other/Prefer Not to Say')], max_length=1, verbose_name='Gender')),
            ],
            options={
                'verbose_name': 'Supervisor',
                'verbose_name_plural': 'Supervisors',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('criteria_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('is_completed', models.BooleanField(default=False, help_text='Check if you already completed the assessment.', verbose_name='Completed')),
                ('criteria_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.ContentType')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='projects.Report')),
            ],
            options={
                'verbose_name': 'Review',
                'verbose_name_plural': 'Reviews',
            },
        ),
    ]
