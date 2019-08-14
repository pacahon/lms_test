# -*- coding: utf-8 -*-
import factory
from django.contrib.sites.models import Site
from post_office.models import EmailTemplate

from core.models import City, Branch, Venue
from core.tests.utils import ANOTHER_DOMAIN, TEST_DOMAIN
from learning.settings import Branches

__all__ = ('CityFactory', 'EmailTemplateFactory', 'BranchFactory',
           'SiteFactory', 'VenueFactory', 'Venue', 'Site', 'City',
           'EmailTemplate', 'Branch',)


class SiteFactory(factory.DjangoModelFactory):
    class Meta:
        model = Site
        django_get_or_create = ('domain',)

    domain = factory.Iterator(x for x in (TEST_DOMAIN, ANOTHER_DOMAIN))
    name = factory.Sequence(lambda n: "Site Name %03d" % n)


class CityFactory(factory.DjangoModelFactory):
    class Meta:
        model = City
        django_get_or_create = ('code',)

    code = factory.Sequence(lambda n: "%03d" % n)
    name = factory.Sequence(lambda n: "City name %03d" % n)
    abbr = factory.Sequence(lambda n: "%03d" % n)


class EmailTemplateFactory(factory.DjangoModelFactory):
    class Meta:
        model = EmailTemplate
        django_get_or_create = ["name"]


class BranchFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: "Branch %03d" % n)
    code = factory.Iterator(x for x, _ in Branches.choices)
    site = factory.SubFactory(SiteFactory)
    city = factory.SubFactory(CityFactory)
    time_zone = 'Europe/Moscow'

    class Meta:
        model = Branch
        django_get_or_create = ('code',)


class VenueFactory(factory.DjangoModelFactory):
    class Meta:
        model = Venue

    city = factory.Iterator(City.objects.all())
    name = factory.Sequence(lambda n: "Test venue %03d" % n)
    description = factory.Sequence(lambda n: "special venue for tests %03d" % n)
