# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import datetime

from braces.views._access import AccessMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views import generic
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import BaseUpdateView

from learning.admission.forms import InterviewCommentForm, ApplicantForm
from learning.admission.models import Interview, Interviewer, Comment, Contest


class InterviewListView(generic.ListView):
    context_object_name = 'interviews'
    model = Interview
    template_name = "learning/admission/dashboard.html"

    def get_context_data(self, **kwargs):
        # TODO: In Django 1.9 implemented __date lookup field. Replace after migration
        today_min = datetime.datetime.combine(now(), datetime.time.min)
        today_max = datetime.datetime.combine(now(), datetime.time.max)
        context = super(InterviewListView, self).get_context_data(**kwargs)
        context["total"] = self.get_queryset().count()
        context["today"] = self.get_queryset().filter(date__range=(today_min, today_max)).count()
        return context

    def get_queryset(self):
        today = now()
        return (Interview.objects
                         .filter(date__gte=today,
                                 decision=Interview.WAITING)
                         .select_related("applicant")
                         .prefetch_related(
                            Prefetch(
                                'interviewers',
                                queryset=Interviewer.objects.select_related("user"))
                         )
                         .order_by("date"))


class InterviewerAccessMixin(AccessMixin):
    def __init__(self):
        self.interview = None
        super(InterviewerAccessMixin, self).__init__()

    def dispatch(self, request, *args, **kwargs):
        interview_id = self.kwargs.get("pk", None)
        if not interview_id:
            raise Http404
        self.interview = get_object_or_404(
            Interview.objects
                .filter(pk=interview_id)
                .prefetch_related(
                    Prefetch(
                        'interviewers',
                        queryset=Interviewer.objects.select_related("user")),
                )
                .select_related("applicant", "applicant__online_test",
                                "applicant__exam", "applicant__campaign"))
        interviewers_uids = [u.pk for u in self.interview.interviewers.all()]
        if request.user.pk not in interviewers_uids:
            return self.handle_no_permission(request)

        return super(InterviewerAccessMixin, self).dispatch(
            request, *args, **kwargs)


class InterviewDetailView(InterviewerAccessMixin, TemplateResponseMixin,
                          BaseUpdateView):
    form_class = InterviewCommentForm
    template_name = "learning/admission/interview.html"

    def get_object(self, queryset=None):
        """Try to fetch comment by interview id and interviewer id"""
        if queryset is None:
            queryset = self.get_queryset()
        try:
            obj = queryset.get()
            return obj
        except (AttributeError, queryset.model.DoesNotExist):
            return None

    def get_queryset(self):
        interview_id = self.kwargs.get("pk", None)
        return Comment.objects.filter(interview=interview_id,
                                      interviewer__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(InterviewDetailView, self).get_context_data(**kwargs)
        context["campaign"] = self.interview.applicant.campaign
        context["interview"] = self.interview
        context["applicant"] = ApplicantForm(instance=self.interview.applicant)
        context["online_test"] = self.interview.applicant.online_test
        if context["online_test"].yandex_contest_id:
            context["contests"] = Contest.objects.filter(
                contest_id=context["online_test"].yandex_contest_id).all()
        context["exam"] = self.interview.applicant.exam
        comment = self.get_object()
        if comment:
            context["comments"] = Comment.objects.filter(
                interview=self.interview.pk).select_related("interviewer__user")
        else:
            context["comments"] = False
        return context

    def _get_interviewer(self):
        for i in self.interview.interviewers.all():
            if i.user.pk == self.request.user.pk:
                return i
        return False

    def get_form_kwargs(self):
        interview_id = self.kwargs.get("pk", None)
        interviewer = self._get_interviewer()
        kwargs = super(InterviewDetailView, self).get_form_kwargs()
        kwargs['initial']['interview'] = interview_id
        kwargs['initial']['interviewer'] = interviewer.pk
        # Store values to validate submitted interviewer/interview on form level
        kwargs.update({"interviewer": interviewer})
        kwargs.update({"interview_id": interview_id})
        return kwargs

    def get_success_url(self):
        messages.success(self.request, "Комментарий успешно сохранён",
                         extra_tags='timeout')
        return reverse("admission_interview_detail",
                       args=[self.object.interview.pk])