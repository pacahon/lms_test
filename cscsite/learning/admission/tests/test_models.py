import pytest

from learning.admission.factories import CampaignFactory, ContestFactory, \
    ApplicantFactory
from learning.admission.models import Contest


@pytest.mark.django_db
def test_applicant_set_contest_id(client):
    """Test contest id rotation"""
    campaign = CampaignFactory.create()
    contests = ContestFactory.create_batch(4, campaign=campaign,
                                           type=Contest.TYPE_TEST)
    ContestFactory(campaign=campaign, type=Contest.TYPE_EXAM)
    c1, c2, c3, c4 = sorted(contests, key=lambda x: x.contest_id)
    a = ApplicantFactory(campaign=campaign)
    assert a.contest_id == c2.contest_id
    a = ApplicantFactory(campaign=campaign)
    assert a.contest_id == c3.contest_id
    a = ApplicantFactory(campaign=campaign)
    assert a.contest_id == c4.contest_id
    a = ApplicantFactory(campaign=campaign)
    assert a.contest_id == c1.contest_id
