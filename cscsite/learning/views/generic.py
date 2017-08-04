import datetime

from dateutil.relativedelta import relativedelta
from django.http import HttpResponseRedirect
from django.views import generic

from learning.calendar import EventsCalendar, CalendarQueryParams
from learning.utils import now_local

__all__ = ['CalendarGenericView']


class CalendarGenericView(generic.TemplateView):
    calendar_type = "full"
    template_name = "learning/calendar.html"

    def get(self, request, *args, **kwargs):
        """Validates GET-parameters, set defaults if no values provided."""
        query_params = CalendarQueryParams(data=request.GET)
        if not query_params.is_valid():
            return HttpResponseRedirect(request.path)
        city_code = self.get_city_code()
        today = now_local(city_code).date()
        year = query_params.validated_data.get('year', today.year)
        month = query_params.validated_data.get('month', today.month)
        context = self.get_context_data(year, month, city_code, today, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, year, month, city_code, today, **kwargs):
        calendar = EventsCalendar()
        events = self.get_events(year, month, city_code)
        calendar.add_events(*events)
        current = datetime.date(year=year, month=month, day=1)
        context = {
            "current": current,
            "prev": current + relativedelta(months=-1),
            "next": current + relativedelta(months=+1),
            "calendar_type": self.calendar_type,
            "month": calendar.as_matrix(year, month, today)
        }
        return context

    def get_events(self, year, month, city_code) -> list:
        raise NotImplementedError()

    def get_city_code(self):
        """Returns city code for authenticated user"""
        raise NotImplementedError()