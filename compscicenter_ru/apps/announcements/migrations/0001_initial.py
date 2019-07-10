# Generated by Django 2.2.1 on 2019-06-27 13:52

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('publish_start_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Publish Start at')),
                ('publish_end_at', models.DateTimeField(verbose_name='Publish End at')),
                ('event_date_at', models.DateTimeField(blank=True, null=True, verbose_name='Publish Start at')),
                ('event_place', models.CharField(blank=True, max_length=255, verbose_name='Event Place')),
                ('event_actions', models.TextField(blank=True, default='<a class="btn _big _primary _m-wide" href="">Зарегистрироваться</a>', verbose_name='Actions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AnnouncementTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='Slug')),
            ],
            options={
                'verbose_name': 'Announcement Tag',
                'verbose_name_plural': 'Announcement Tags',
            },
        ),
        migrations.CreateModel(
            name='TaggedAnnouncement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='announcements.Announcement')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='announcements_taggedannouncement_items', to='announcements.AnnouncementTag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='announcement',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='announcements.TaggedAnnouncement', to='announcements.AnnouncementTag', verbose_name='Tags'),
        ),
    ]