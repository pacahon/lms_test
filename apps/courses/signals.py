import datetime
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rq.queues import get_queue

from courses.models import Assignment, CourseTeacher, Semester
from courses.tasks import recalculate_invited_priority
from learning.models import EnrollmentPeriod
from django.utils import timezone

        
@receiver(post_save, sender=Semester)
def schedule_invited_stundent_priority_recalculation(sender, instance: Semester,
                                                created, *args, **kwargs):
    """Schedule job that recalculates priority of every invited student profiles of this semester"""
    queue = get_queue('default')
    recalculation_day = instance.ends_at.date() + datetime.timedelta(days=1)
    # Tests trigger job scheduling. Scheduled ones are deleted after using clear_scheduled_jobs command
    # This is needed to prevent jobs to be queued without scheduling while the tests are running
    if recalculation_day <= timezone.now().date():
        return
    scheduled_registry = queue.scheduled_job_registry
    for job_id in scheduled_registry.get_job_ids():
        job = queue.fetch_job(job_id)
        if job and job.kwargs.get('semester_id', None) == instance.id:
            return
    job = queue.enqueue_at(
        datetime.datetime(recalculation_day.year, recalculation_day.month, recalculation_day.day),
        recalculate_invited_priority,
        semester_id=instance.id
    )
