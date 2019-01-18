# Generated by Django 2.1.5 on 2019-01-09 13:44

from django.db import migrations, models
import django.db.models.deletion
import learning.gallery.models
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('slug', models.SlugField(help_text='Short name in ASCII, used in images upload path', max_length=70, unique=True, verbose_name='Slug')),
                ('order', models.IntegerField(default=100, verbose_name='Order')),
                ('brief', models.CharField(blank=True, default='', help_text='Short description', max_length=255, verbose_name='Brief')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
            ],
            options={
                'verbose_name': 'Album',
                'verbose_name_plural': 'Albums',
                'ordering': ('order', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Title')),
                ('order', models.IntegerField(default=0, verbose_name='Order')),
                ('image', sorl.thumbnail.fields.ImageField(max_length=255, upload_to=learning.gallery.models.gen_path_to_image, verbose_name='File')),
                ('album', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='gallery.Album', verbose_name='Album')),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='courses.Course', verbose_name='Course offering')),
            ],
            options={
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
                'ordering': ('order', 'id'),
            },
        ),
    ]