# Generated by Django 3.2.12 on 2022-03-03 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.PositiveIntegerField(verbose_name='External ID')),
                ('name', models.TextField(verbose_name='Name')),
                ('display_name', models.TextField(verbose_name='Display Name')),
            ],
            options={
                'verbose_name': 'City',
                'verbose_name_plural': 'Cities',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.PositiveIntegerField(verbose_name='External ID')),
                ('name', models.TextField(verbose_name='Name')),
                ('display_name', models.TextField(verbose_name='Display Name')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='universities', to='universities.city', verbose_name='City')),
            ],
            options={
                'verbose_name': 'University',
                'verbose_name_plural': 'Universities',
            },
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.PositiveIntegerField(verbose_name='External ID')),
                ('name', models.TextField(verbose_name='Name')),
                ('display_name', models.TextField(verbose_name='Display Name')),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='faculties', to='universities.university', verbose_name='University')),
            ],
            options={
                'verbose_name': 'Faculty',
                'verbose_name_plural': 'Faculties',
            },
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cities', to='universities.country', verbose_name='Country'),
        ),
        migrations.AddConstraint(
            model_name='university',
            constraint=models.UniqueConstraint(fields=('external_id',), name='unique_university_external_id'),
        ),
        migrations.AddConstraint(
            model_name='faculty',
            constraint=models.UniqueConstraint(fields=('external_id',), name='unique_faculty_external_id'),
        ),
        migrations.AddConstraint(
            model_name='city',
            constraint=models.UniqueConstraint(fields=('external_id',), name='unique_city_external_id'),
        ),
    ]