import datetime

import pytest
import pytz
from rest_framework.exceptions import NotFound

from django.core.exceptions import ValidationError
from django.utils import timezone

from admission.constants import (
    INVITATION_EXPIRED_IN_HOURS, ChallengeStatuses, InterviewFormats, InterviewSections
)
from admission.models import Exam, Interview
from admission.services import (
    EmailQueueService, create_interview_from_slot, create_student_from_applicant,
    get_meeting_time, get_streams
)
from admission.tests.factories import (
    ApplicantFactory, CampaignFactory, ExamFactory, InterviewFactory,
    InterviewFormatFactory, InterviewInvitationFactory, InterviewSlotFactory,
    InterviewStreamFactory
)
from core.tests.factories import BranchFactory, EmailTemplateFactory
from users.models import StudentTypes


@pytest.mark.django_db
def test_new_exam_invitation_email():
    email_template = EmailTemplateFactory()
    campaign = CampaignFactory(template_exam_invitation=email_template.name)
    applicant = ApplicantFactory(campaign=campaign)
    with pytest.raises(Exam.DoesNotExist):
        EmailQueueService.new_exam_invitation(applicant)
    exam = ExamFactory(applicant=applicant, status=ChallengeStatuses.REGISTERED,
                       yandex_contest_id='42')
    email, created = EmailQueueService.new_exam_invitation(applicant)
    assert created
    assert email.template == email_template
    assert email.to == [applicant.email]
    # Render on delivery
    assert not email.subject
    assert not email.message
    assert not email.html_message
    assert 'YANDEX_LOGIN' in email.context
    assert email.context['YANDEX_LOGIN'] == applicant.yandex_login
    assert 'CONTEST_ID' in email.context
    assert email.context['CONTEST_ID'] == '42'
    email2, created = EmailQueueService.new_exam_invitation(applicant)
    assert not created
    assert email2 == email
    email3, created = EmailQueueService.new_exam_invitation(applicant,
                                                            allow_duplicates=True)
    assert created
    assert email3.pk > email2.pk


@pytest.mark.django_db
def test_create_student_from_applicant(settings):
    branch = BranchFactory(time_zone='Asia/Yekaterinburg')
    campaign = CampaignFactory(branch=branch)
    applicant = ApplicantFactory(campaign=campaign)
    user = create_student_from_applicant(applicant)
    student_profile = user.get_student_profile(settings.SITE_ID)
    assert student_profile.branch == branch
    assert student_profile.year_of_admission == applicant.campaign.year
    assert student_profile.type == StudentTypes.REGULAR
    assert user.time_zone == branch.time_zone


@pytest.mark.django_db
def test_create_interview_from_slot():
    dt = timezone.now() + datetime.timedelta(days=3)
    slot = InterviewSlotFactory(
        interview=None,
        stream__section=InterviewSections.MATH,
        stream__date=dt.date(),
        start_at=datetime.time(14, 0),
        end_at=datetime.time(16, 0),
    )
    invitation1 = InterviewInvitationFactory(interview=None, streams=[slot.stream])
    invitation2 = InterviewInvitationFactory(interview=None)
    with pytest.raises(NotFound) as e:
        create_interview_from_slot(invitation1, slot_id=0)
    with pytest.raises(ValidationError) as e:
        create_interview_from_slot(invitation2, slot_id=slot.pk)
    assert "not associated" in e.value.message
    interview1 = InterviewFactory(section=InterviewSections.ALL_IN_ONE)
    invitation1.interview = interview1
    with pytest.raises(ValidationError) as e:
        create_interview_from_slot(invitation1, slot_id=slot.pk)
    assert e.value.code == 'corrupted'
    interview2 = InterviewFactory(section=InterviewSections.ALL_IN_ONE,
                                  applicant=invitation1.applicant)
    invitation1.interview = interview2
    with pytest.raises(ValidationError) as e:
        create_interview_from_slot(invitation1, slot_id=slot.pk)
    assert e.value.code == 'accepted'
    invitation1.interview = None
    create_interview_from_slot(invitation1, slot_id=slot.pk)
    assert Interview.objects.count() == 3
    interview = Interview.objects.exclude(pk__in=[interview1.pk, interview2.pk]).get()
    assert interview.date.date() == dt.date()
    assert interview.date_local().hour == 14
    assert interview.section == slot.stream.section
    invitation1.refresh_from_db()
    assert invitation1.interview_id == interview.id
    # TODO: occupy slot


@pytest.mark.django_db
def test_get_streams():
    campaign = CampaignFactory(current=True,
                               branch__time_zone=pytz.timezone('Europe/Moscow'))
    # Make sure invitation is active
    dt = timezone.now() + datetime.timedelta(hours=INVITATION_EXPIRED_IN_HOURS)
    stream = InterviewStreamFactory(start_at=datetime.time(14, 10),
                                    end_at=datetime.time(15, 10),
                                    duration=20,
                                    date=dt.date(),
                                    with_assignments=False,
                                    campaign=campaign,
                                    section=InterviewSections.ALL_IN_ONE,
                                    format=InterviewFormats.OFFLINE)
    assert stream.slots.count() == 3
    invitation = InterviewInvitationFactory(
        expired_at=dt,
        applicant__campaign=stream.campaign,
        interview=None,
        streams=[stream])
    streams = get_streams(invitation)
    assert len(streams) == 1
    assert stream in streams
    slots = streams[stream]
    assert len(slots) == 3
    slot1, slot2, slot3 = slots
    assert slot1.start_at == datetime.time(hour=14, minute=10)
    assert slot2.start_at == datetime.time(hour=14, minute=30)
    assert slot3.start_at == datetime.time(hour=14, minute=50)


@pytest.mark.django_db
def test_get_meeting_time():
    dt = timezone.now() + datetime.timedelta(hours=INVITATION_EXPIRED_IN_HOURS)
    campaign = CampaignFactory(current=True,
                               branch__time_zone=pytz.timezone('Europe/Moscow'))
    # Make sure invitation is active
    stream = InterviewStreamFactory(start_at=datetime.time(14, 10),
                                    end_at=datetime.time(14, 30),
                                    duration=20,
                                    date=dt.date(),
                                    with_assignments=False,
                                    campaign=campaign,
                                    section=InterviewSections.ALL_IN_ONE,
                                    format=InterviewFormats.OFFLINE)
    assert stream.slots.count() == 1
    slot = stream.slots.first()
    meeting_at = get_meeting_time(slot.datetime_local, stream)
    assert meeting_at.time() == datetime.time(hour=14, minute=10)
    # 30 min diff if stream with assignments
    stream.with_assignments = True
    stream.save()
    meeting_at = get_meeting_time(slot.datetime_local, stream)
    assert meeting_at.time() == datetime.time(hour=13, minute=40)
    # Don't adjust time for online interview format
    InterviewFormatFactory(campaign=campaign, format=InterviewFormats.ONLINE)
    stream.format = InterviewFormats.ONLINE
    stream.save()
    meeting_at = get_meeting_time(slot.datetime_local, stream)
    assert meeting_at.time() == datetime.time(hour=14, minute=10)
