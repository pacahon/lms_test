from datetime import datetime, timedelta
from operator import attrgetter
from typing import Dict, List, Optional, Tuple

from post_office import mail
from post_office.models import STATUS as EMAIL_STATUS
from post_office.models import Email, EmailTemplate
from post_office.utils import get_email_template
from rest_framework.exceptions import APIException, NotFound

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone, translation
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

from admission.constants import (
    INTERVIEW_FEEDBACK_TEMPLATE, INVITATION_EXPIRED_IN_HOURS, InterviewFormats,
    InterviewInvitationStatuses
)
from admission.models import (
    Applicant, Campaign, Exam, Interview, InterviewInvitation, InterviewSlot,
    InterviewStream
)
from admission.utils import logger
from core.timezone.constants import DATE_FORMAT_RU
from core.utils import bucketize
from grading.api.yandex_contest import YandexContestAPI
from learning.services import create_student_profile, get_student_profile
from users.models import StudentTypes, User


def get_email_from(campaign: Campaign):
    # TODO: add email to Campaign model?
    return campaign.branch.default_email_from


def create_invitation(streams: List[InterviewStream], applicant: Applicant):
    """Create invitation and send email to applicant."""
    streams = list(streams)  # Queryset -> list
    first_stream = min(streams, key=attrgetter('date'))
    tz = first_stream.get_timezone()
    first_day_interview_naive = datetime.combine(first_stream.date,
                                                 datetime.min.time())
    first_day_interview = tz.localize(first_day_interview_naive)
    # Calculate deadline for invitation. It can't be later than 00:00
    # of the first interview day
    expired_in_hours = INVITATION_EXPIRED_IN_HOURS
    expired_at = timezone.now() + timedelta(hours=expired_in_hours)
    expired_at = min(expired_at, first_day_interview)
    invitation = InterviewInvitation(applicant=applicant,
                                     expired_at=expired_at)
    with transaction.atomic():
        invitation.save()
        invitation.streams.add(*streams)
        EmailQueueService.generate_interview_invitation(invitation)


def import_campaign_contest_results(*, campaign: Campaign, model_class):
    api = YandexContestAPI(access_token=campaign.access_token)
    on_scoreboard_total = 0
    updated_total = 0
    for contest in campaign.contests.filter(type=model_class.CONTEST_TYPE):
        logger.debug(f"Starting processing contest {contest.pk}")
        on_scoreboard, updated = model_class.import_results(api, contest)
        on_scoreboard_total += on_scoreboard
        updated_total += updated
        logger.debug(f"Scoreboard total = {on_scoreboard}")
        logger.debug(f"Updated = {updated}")
    return on_scoreboard_total, updated_total


def import_exam_results(*, campaign: Campaign):
    import_campaign_contest_results(campaign=campaign, model_class=Exam)


class UsernameError(Exception):
    """Raise this exception if fail to create a unique username"""
    pass


def create_student_from_applicant(applicant):
    """
    Creates new model or override existent with data from application form.
    """
    branch = applicant.campaign.branch
    try:
        user = User.objects.get(email=applicant.email)
    except User.DoesNotExist:
        username = applicant.email.split("@", maxsplit=1)[0]
        if User.objects.filter(username=username).exists():
            username = User.generate_random_username(attempts=5)
        if not username:
            raise UsernameError(f"Имя {username} уже занято. "
                                f"Cлучайное имя сгенерировать не удалось")
        random_password = User.objects.make_random_password()
        user = User.objects.create_user(username=username,
                                        email=applicant.email,
                                        time_zone=branch.time_zone,
                                        password=random_password)
    campaign_year = applicant.campaign.year
    student_profile = get_student_profile(
        user=user, site=branch.site,
        profile_type=StudentTypes.REGULAR,
        filters=[Q(year_of_admission=campaign_year)])
    # Don't override existing student profile for this campaign since it could
    # be already changed
    if student_profile is None:
        create_student_profile(
            user=user, branch=branch,
            profile_type=StudentTypes.REGULAR,
            year_of_admission=campaign_year,
            year_of_curriculum=campaign_year,
            level_of_education_on_admission=applicant.level_of_education,
            university=applicant.university.name)
    user.first_name = applicant.first_name
    user.last_name = applicant.last_name
    user.patronymic = applicant.patronymic if applicant.patronymic else ""
    user.phone = applicant.phone
    user.workplace = applicant.workplace if applicant.workplace else ""
    # Social accounts info
    try:
        user.stepic_id = int(applicant.stepic_id)
    except (TypeError, ValueError):
        pass
    user.yandex_login = applicant.yandex_login if applicant.yandex_login else ""
    # For github.com store part after github.com/
    if applicant.github_login:
        user.github_login = applicant.github_login.split("github.com/",
                                                         maxsplit=1)[-1]
    user.save()
    return user


def get_streams(invitation: InterviewInvitation) -> Dict[InterviewStream, List[InterviewSlot]]:
    """
    Returns streams related to the invitation where
    slots are sorted by time in ASC order.
    """
    slots = (InterviewSlot.objects
             .filter(stream__interview_invitations=invitation)
             .select_related("stream__interview_format",
                             "stream__venue__city")
             .order_by("stream__date", "start_at"))
    return bucketize(slots, key=lambda s: s.stream)


# TODO: change exception type
class InterviewCreateError(APIException):
    pass


def decline_interview_invitation(invitation: InterviewInvitation):
    if invitation.is_expired:
        raise ValidationError("Interview Invitation is expired", code="expired")
    is_unprocessed_invitation = (invitation.status == InterviewInvitationStatuses.CREATED)
    if not is_unprocessed_invitation:
        raise ValidationError("Status transition is not supported", code="malformed")
    invitation.status = InterviewInvitationStatuses.DECLINED
    invitation.save(update_fields=['status'])


def accept_interview_invitation(invitation: InterviewInvitation, slot_id: int) -> Interview:
    """
    Creates interview, occupies slot and sends confirmation via email.

    It is allowed to accept only ongoing unprocessed invitation.
    """
    # Checks for more detailed errors
    if invitation.is_accepted:
        # Interview was created but reassigned to another participant
        if invitation.applicant_id != invitation.interview.applicant_id:
            code = "corrupted"
        else:
            code = "accepted"  # by invited participant
        raise ValidationError("Приглашение уже принято", code=code)
    elif invitation.is_expired:
        raise ValidationError("Приглашение больше не актуально", code="expired")
    is_unprocessed_invitation = (invitation.status == InterviewInvitationStatuses.CREATED)
    if not is_unprocessed_invitation:
        raise ValidationError(f"You can't accept invitation with {invitation.status} status", code="malformed")

    try:
        slot = InterviewSlot.objects.get(pk=slot_id)
    except InterviewSlot.DoesNotExist:
        raise NotFound(_("Interview slot not found"))
    # TODO: What if slot is occupied
    if slot.stream_id not in (s.id for s in invitation.streams.all()):
        raise ValidationError(_("Interview slot is not associated with the invitation"))

    interview = Interview(applicant=invitation.applicant,
                          status=Interview.APPROVED,
                          section=slot.stream.section,
                          date=slot.datetime_local)
    with transaction.atomic():
        sid = transaction.savepoint()
        interview.save()
        is_slot_has_taken = InterviewSlot.objects.lock(slot, interview)
        if not is_slot_has_taken:
            transaction.savepoint_rollback(sid)
            raise InterviewCreateError("Извините, но слот уже был занят другим участником. "
                                       "Выберите другое время и повторите попытку.", code="slot_occupied")
        interview.interviewers.set(slot.stream.interviewers.all())
        # FIXME: delay or remove .on_commit
        transaction.on_commit(lambda: slot.stream.compute_fields('slots_occupied_count'))
        EmailQueueService.generate_interview_confirmation(interview, slot.stream)
        EmailQueueService.generate_interview_reminder(interview, slot.stream)
        # Mark invitation as accepted
        (InterviewInvitation.objects
         .filter(pk=invitation.pk)
         .update(interview_id=interview.id,
                 status=InterviewInvitationStatuses.ACCEPTED,
                 modified=timezone.now()))
        transaction.savepoint_commit(sid)
        return interview


def get_meeting_time(meeting_at: datetime, stream: InterviewStream):
    if stream.interview_format.format == InterviewFormats.OFFLINE:
        # Applicants have to solve some assignments before interview part
        if stream.with_assignments:
            meeting_at -= timedelta(minutes=30)
    return meeting_at


class EmailQueueService:
    @staticmethod
    def new_registration(applicant: Applicant) -> Email:
        campaign = applicant.campaign
        return mail.send(
            [applicant.email],
            sender=get_email_from(campaign),
            template=campaign.template_registration,
            context={
                'FIRST_NAME': applicant.first_name,
                'SURNAME': applicant.last_name,
                'PATRONYMIC': applicant.patronymic if applicant.patronymic else "",
                'EMAIL': applicant.email,
                'BRANCH': campaign.branch.name,
                'PHONE': applicant.phone,
                'CONTEST_ID': applicant.online_test.yandex_contest_id,
                'YANDEX_LOGIN': applicant.yandex_login,
            },
            render_on_delivery=False,
            backend='ses',
        )

    @staticmethod
    def new_exam_invitation(applicant: Applicant,
                            allow_duplicates=False) -> Tuple[Email, bool]:
        recipient = applicant.email
        template_name = applicant.campaign.template_exam_invitation
        template = get_email_template(template_name)
        if not allow_duplicates:
            latest_email = (Email.objects
                            .filter(to=recipient, template=template)
                            .order_by('-pk')
                            .first())
            if latest_email:
                return latest_email, False
        return mail.send(
            [recipient],
            sender=get_email_from(applicant.campaign),
            template=template,
            context={
                'CONTEST_ID': applicant.exam.yandex_contest_id,
                'YANDEX_LOGIN': applicant.yandex_login,
            },
            render_on_delivery=True,
            backend='ses',
        ), True

    @staticmethod
    def generate_interview_invitation(interview_invitation) -> Email:
        streams = []
        for stream in interview_invitation.streams.select_related("venue").all():
            with translation.override('ru'):
                date = date_format(stream.date, "j E")
            s = {
                "CITY": stream.venue.city.name,
                "FORMAT": stream.format,
                "DATE": date,
                "VENUE": stream.venue.name,
                "WITH_ASSIGNMENTS": stream.with_assignments,
                "DIRECTIONS": stream.venue.directions,
            }
            streams.append(s)
        campaign = interview_invitation.applicant.campaign
        context = {
            "BRANCH": campaign.branch.name,
            "SECRET_LINK": interview_invitation.get_absolute_url(),
            "STREAMS": streams
        }
        return mail.send(
            [interview_invitation.applicant.email],
            sender=get_email_from(campaign),
            template=campaign.template_appointment,
            context=context,
            render_on_delivery=False,
            backend='ses',
        )

    # noinspection DuplicatedCode
    @staticmethod
    def generate_interview_confirmation(interview: Interview,
                                        stream: InterviewStream) -> Optional[Email]:
        interview_format = stream.interview_format
        if interview_format.confirmation_template_id is None:
            return None
        campaign = interview.applicant.campaign
        meeting_at = get_meeting_time(interview.date_local(), stream)
        with translation.override('ru'):
            date = date_format(meeting_at, "j E")
        context = {
            "BRANCH": campaign.branch.name,
            "DATE": date,
            "TIME": meeting_at.strftime("%H:%M"),
            "DIRECTIONS": stream.venue.directions
        }
        is_online = (stream.format == InterviewFormats.ONLINE)
        if stream.with_assignments and is_online:
            public_url = interview.get_public_assignments_url()
            context['ASSIGNMENTS_LINK'] = public_url
        return mail.send(
            [interview.applicant.email],
            sender=get_email_from(campaign),
            template=interview_format.confirmation_template,
            context=context,
            render_on_delivery=False,
            backend='ses',
        )

    @staticmethod
    def generate_interview_reminder(interview: Interview,
                                    stream: InterviewStream) -> None:
        today = timezone.now()
        interview_format = stream.interview_format
        scheduled_time = interview.date - interview_format.remind_before_start
        # It's not late to send a reminder
        if scheduled_time > today:
            campaign = interview.applicant.campaign
            meeting_at = get_meeting_time(interview.date_local(), stream)
            context = {
                "BRANCH": campaign.branch.name,
                "DATE": meeting_at.strftime(DATE_FORMAT_RU),
                "TIME": meeting_at.strftime("%H:%M"),
                "DIRECTIONS": stream.venue.directions
            }
            is_online = (stream.format == InterviewFormats.ONLINE)
            if stream.with_assignments and is_online:
                public_url = interview.get_public_assignments_url()
                context['ASSIGNMENTS_LINK'] = public_url
            mail.send(
                [interview.applicant.email],
                scheduled_time=scheduled_time,
                sender=get_email_from(campaign),
                template=interview_format.reminder_template,
                context=context,
                # Rendering on delivery stores template id and allowing
                # filtering emails in the future
                render_on_delivery=True,
                backend='ses',
            )

    @staticmethod
    def remove_interview_reminder(interview: Interview) -> None:
        slots = (InterviewSlot.objects
                 .filter(interview=interview)
                 .select_related('stream', 'stream__interview_format'))
        for slot in slots:
            interview_format = slot.stream.interview_format
            (Email.objects
             .filter(template_id=interview_format.reminder_template_id,
                     to=interview.applicant.email)
             .exclude(status=EMAIL_STATUS.sent)
             .delete())

    @staticmethod
    def generate_interview_feedback_email(interview) -> None:
        if interview.status != interview.COMPLETED:
            return
        # Fail silently if template not found
        template_name = INTERVIEW_FEEDBACK_TEMPLATE
        try:
            template = EmailTemplate.objects.get(name=template_name)
        except EmailTemplate.DoesNotExist:
            logger.error("Template with name {} not found".format(template_name))
            return
        interview_date = interview.date_local()
        # It will be send immediately if time is expired
        scheduled_time = interview_date.replace(hour=21, minute=0, second=0,
                                                microsecond=0)
        recipients = [interview.applicant.email]
        try:
            # Update scheduled_time if a feedback task in a queue is
            # not completed
            email_identifiers = {
                "template__name": INTERVIEW_FEEDBACK_TEMPLATE,
                "to": recipients
            }
            email = Email.objects.get(**email_identifiers)
            if email.status != EMAIL_STATUS.sent:
                (Email.objects
                 .filter(**email_identifiers)
                 .update(scheduled_time=scheduled_time))
        except Email.DoesNotExist:
            mail.send(
                recipients,
                scheduled_time=scheduled_time,
                sender='info@compscicenter.ru',
                template=template,
                context={
                    "BRANCH": interview.applicant.campaign.branch.name,
                },
                # Render on delivery, we have no really big amount of
                # emails to think about saving CPU time
                render_on_delivery=True,
                backend='ses',
            )

    @staticmethod
    def remove_interview_feedback_emails(interview):
        (Email.objects
         .filter(template__name=INTERVIEW_FEEDBACK_TEMPLATE,
                 to=interview.applicant.email)
         .exclude(status=EMAIL_STATUS.sent)
         .delete())

    @staticmethod
    def time_to_start_yandex_contest(*, campaign: Campaign,
                                     template: EmailTemplate, participants):
        email_from = get_email_from(campaign)
        generated = 0
        for participant in participants:
            recipients = [participant["applicant__email"]]
            if not Email.objects.filter(to=recipients, template=template).exists():
                mail.send(recipients,
                          sender=email_from,
                          template=template,
                          context={
                              "CONTEST_ID": participant["yandex_contest_id"],
                              "YANDEX_LOGIN": participant["applicant__yandex_login"],
                          },
                          render_on_delivery=True,
                          backend='ses')
                generated += 1
        return generated
