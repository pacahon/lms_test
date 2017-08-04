import datetime
import pytest
import pytz
from bs4 import BeautifulSoup

from learning.factories import CourseOfferingFactory, CourseOfferingNewsFactory

SPB_OFFSET = 3
NSK_OFFSET = 7


@pytest.mark.django_db
def test_news_get_city_timezone(settings):
    news = CourseOfferingNewsFactory(course_offering__city_id='nsk')
    assert news.get_city_timezone() == settings.TIME_ZONES['nsk']
    news.course_offering.city_id = 'spb'
    news.refresh_from_db()
    assert news.get_city_timezone() == settings.TIME_ZONES['spb']


@pytest.mark.django_db
def test_course_offering_news(settings, admin_client):
    settings.LANGUAGE_CODE = 'ru'
    news = CourseOfferingNewsFactory(course_offering__city_id='spb',
                                     created=datetime.datetime(2017, 1, 13,
                                                               20, 0, 0, 0,
                                                               tzinfo=pytz.UTC))
    co = news.course_offering
    date_in_utc = news.created
    localized = date_in_utc.astimezone(settings.TIME_ZONES['spb'])
    assert localized.utcoffset() == datetime.timedelta(hours=SPB_OFFSET)
    assert localized.hour == 23
    date_str = "{:02d}".format(localized.day)
    assert date_str == "13"
    response = admin_client.get(co.get_absolute_url())
    html = BeautifulSoup(response.content, "html.parser")
    assert any(date_str in s.string for s in
               html.find_all('div', {"class": "date"}))
    # For NSK we should live in the next day
    co.city_id = 'nsk'
    co.save()
    localized = date_in_utc.astimezone(settings.TIME_ZONES['nsk'])
    assert localized.utcoffset() == datetime.timedelta(hours=NSK_OFFSET)
    assert localized.hour == 3
    assert localized.day == 14
    date_str = "{:02d}".format(localized.day)
    assert date_str == "14"
    response = admin_client.get(co.get_absolute_url())
    html = BeautifulSoup(response.content, "html.parser")
    assert any(date_str in s.string for s in
               html.find_all('div', {"class": "date"}))