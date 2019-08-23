# Generated by Django 2.2.4 on 2019-08-22 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0020_learningspace'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseclass',
            name='venue_new',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='venuw_nwe', to='courses.LearningSpace', verbose_name='CourseClass|Venue'),
            preserve_default=False,
        ),
    ]
