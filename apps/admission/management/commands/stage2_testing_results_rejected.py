# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from post_office import mail
from post_office.models import Email
from post_office.utils import get_email_template

from ._utils import CurrentCampaignMixin, EmailTemplateMixin
from admission.models import Test, Applicant
from admission.services import get_email_from


class Command(EmailTemplateMixin, CurrentCampaignMixin, BaseCommand):
    help = """
    Updates applicant status to REJECTED_BY_TEST if they failed testing, then
    send notification to them.
    """

    TEMPLATE_PATTERN = "admission-{year}-{branch_code}-testing-fail"

    def handle(self, *args, **options):
        campaigns = self.get_current_campaigns(options)
        if input(self.CURRENT_CAMPAIGNS_AGREE) != "y":
            self.stdout.write("Canceled")
            return

        template_name_pattern = options['template_pattern']
        self.validate_templates(campaigns, template_name_pattern)

        for campaign in campaigns:
            self.stdout.write(str(campaign))
            testing_passing_score = campaign.online_test_passing_score
            if not testing_passing_score:
                self.stdout.write(f"Passing score for campaign '{campaign}' must be non zero. Skip")
                continue

            template_name = self.get_template_name(campaign, template_name_pattern)
            template = get_email_template(template_name)

            email_from = get_email_from(campaign)

            applicants = (Applicant.objects
                          .filter(campaign_id=campaign.pk)
                          .filter(Q(online_test__score__lt=testing_passing_score) |
                                  Q(online_test__score__isnull=True))
                          .values("pk",
                                  "online_test__score",
                                  "online_test__yandex_contest_id",
                                  "yandex_login",
                                  "email"))
            total = 0
            generated = 0
            for a in applicants:
                total += 1
                recipients = [a["email"]]
                if not Email.objects.filter(to=recipients,
                                            template=template).exists():
                    score = 0 if a["online_test__score"] is None else int(a["online_test__score"])
                    assert score < testing_passing_score
                    context = {
                        'LOGIN': a["yandex_login"],
                        'TEST_SCORE': score,
                        'TEST_CONTEST_ID': a["online_test__yandex_contest_id"],
                    }
                    with transaction.atomic():
                        (Applicant.objects
                         .filter(pk=a["pk"])
                         .update(status=Applicant.REJECTED_BY_TEST))
                        mail.send(
                            recipients,
                            sender=email_from,
                            template=template,
                            context=context,
                            # If emails rendered on delivery, they will store
                            # value of the template id. It makes `exists`
                            # method above works correctly.
                            render_on_delivery=True,
                            backend='ses',
                        )
                        generated += 1
            self.stdout.write(f"    total: {total}")
            self.stdout.write(f"    updated: {generated}")
        self.stdout.write("Done")
