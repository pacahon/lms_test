# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from post_office import mail
from post_office.models import Email
from post_office.utils import get_email_template

from admission.models import Applicant
from admission.services import get_email_from
from ._utils import EmailTemplateMixin, CurrentCampaignMixin


class Command(EmailTemplateMixin, CurrentCampaignMixin, BaseCommand):
    help = """Generate emails about exam results."""

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--fail-only', action='store_true',
            dest="fail_only",
            help="Send emails only to those who didn't pass to the next stage")

    def handle(self, *args, **options):
        campaigns = self.get_current_campaigns(options)
        if input(self.CURRENT_CAMPAIGNS_AGREE) != "y":
            self.stdout.write("Canceled")
            return

        email_types = ["exam-fail"]
        if not options["fail_only"]:
            email_types.append("exam-success")
        self.validate_templates(campaigns, types=email_types)

        for campaign in campaigns:
            self.stdout.write("{}:".format(campaign))
            email_from = get_email_from(campaign)
            statuses = [
                Applicant.REJECTED_BY_EXAM,
            ]
            if not options["fail_only"]:
                statuses.append(Applicant.INTERVIEW_TOBE_SCHEDULED)
            applicants = (Applicant.objects
                          .filter(campaign=campaign.pk,
                                  status__in=statuses)
                          .only("email", "status"))
            succeed = 0
            total = 0
            generated = 0
            for a in applicants.iterator():
                total += 1
                succeed += int(a.status == Applicant.INTERVIEW_TOBE_SCHEDULED)
                template = self.get_template(a, campaign)
                recipients = [a.email]
                if not Email.objects.filter(to=recipients,
                                            template=template).exists():
                    context = {
                        'BRANCH': campaign.branch.name
                    }
                    mail.send(
                        recipients,
                        sender=email_from,
                        template=template,
                        # If emails rendered on delivery, they will store
                        # value of the template id. It makes
                        # `Email.objects.exists()` work correctly.
                        render_on_delivery=True,
                        context=context,
                        backend='ses',
                    )
                    generated += 1
            self.stdout.write("Total: {}".format(total))
            self.stdout.write("Succeed: {}".format(succeed))
            self.stdout.write("Fail: {}".format(total - succeed))
            self.stdout.write("Emails generated: {}".format(generated))
        self.stdout.write("Done")

    def get_template(self, applicant, campaign):
        if applicant.status == Applicant.INTERVIEW_TOBE_SCHEDULED:
            template_type = "exam-success"
        else:
            template_type = "exam-fail"
        template_name = self.get_template_name(campaign, type=template_type)
        return get_email_template(template_name)

