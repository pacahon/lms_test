# -*- coding: utf-8 -*-

import logging
from itertools import groupby

from django.apps import apps
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.db import transaction
from django.db.models import Case, BooleanField, Prefetch, Count, Value, When
from django.forms import modelformset_factory, inlineformset_factory
from django.http import Http404, HttpResponse, HttpResponseForbidden, \
    HttpResponseRedirect
from django.http.response import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views import generic, View
from django.views.generic.edit import FormMixin, BaseUpdateView, ModelFormMixin
from django_filters.views import BaseFilterView, FilterMixin
from extra_views.formsets import BaseModelFormSetView
from vanilla.model_views import CreateView

from core import comment_persistence
from core.exceptions import Redirect
from core.timezone import now_local
from core.urls import reverse, reverse_lazy
from core.utils import hashids
from core.views import LoginRequiredMixin
from courses.models import Semester
from courses.utils import get_current_term_index
from projects.constants import ProjectTypes
from projects.filters import ProjectsFilter, CurrentTermProjectsFilter
from projects.forms import ReportCommentForm, ReportReviewForm, \
    ReportStatusForm, ReportSummarizeForm, ReportForm, \
    ReportCuratorAssessmentForm, StudentResultsModelForm, PracticeCriteriaForm
from projects.models import Project, ProjectStudent, Report, \
    ReportComment, Review, ReportingPeriod, ReportingPeriodKey, PracticeCriteria
from notifications import NotificationTypes
from notifications.signals import notify
from users.constants import Roles, GenderTypes
from users.mixins import ProjectReviewerGroupOnlyMixin, StudentOnlyMixin, \
    CuratorOnlyMixin
from users.models import User

__all__ = (
    'ReportListReviewerView', 'ReportListCuratorView', 'CurrentTermProjectsView',
    'ProjectListView', 'ProjectDetailView',
    'ProjectResultsView', 'ProjectPrevNextView', 'ProjectEnrollView',
    'ReportUpdateStatusView', 'ReportCuratorAssessmentView',
    'ReportCuratorSummarizeView', 'ReportView', 'ReportAttachmentDownloadView',
    'StudentProjectsView', 'ProjectDetailView', 'ReportView',
)


logger = logging.getLogger(__name__)


class RaiseRedirect(Exception):
    pass


# Formset for student results
ResultsFormSet = modelformset_factory(
    ProjectStudent, form=StudentResultsModelForm, extra=0,
)


class ReportListViewMixin:
    context_object_name = "reports"
    template_name = "learning/projects/reports.html"

    def get_queryset(self):
        # FIXME: respect timezone. Hard coded city code
        current_term_index = get_current_term_index()
        qs = (Report.objects
              .filter(project_student__project__semester__index=current_term_index)
                # FIXME: replace with custom manager
              .exclude(project_student__project__status=Project.Statuses.CANCELED)
              .select_related("project_student",
                              "project_student__student",
                              "project_student__project",
                              "reporting_period")
              .order_by("project_student__project__name",
                        "project_student__project__id",
                        "project_student__student__last_name"))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reports = list(context[self.context_object_name])
        projects = []
        for k, g in groupby(reports, key=lambda r: r.project_student.project):
            projects.append(list(g))
        context[self.context_object_name] = projects
        context["current_term"] = Semester.get_current()
        return context


class ReportListReviewerView(ProjectReviewerGroupOnlyMixin,
                             ReportListViewMixin,
                             generic.ListView):
    def get_queryset(self):
        return (super().get_queryset()
                .filter(project_student__project__reviewers=self.request.user))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context["reports"] and self.request.user.is_curator:
            msg = ("Вы были перенаправлены на список всех отчетов "
                   "текущего семестра")
            messages.info(self.request, msg, extra_tags="timeout")
            raise Redirect(to=reverse("projects:report_list_curators"))
        return context


class ReportListCuratorView(CuratorOnlyMixin, ReportListViewMixin,
                            generic.ListView):
    pass


class CurrentTermProjectsView(ProjectReviewerGroupOnlyMixin, FilterMixin,
                              generic.ListView):
    paginate_by = 50
    filterset_class = CurrentTermProjectsFilter
    context_object_name = "projects"
    template_name = "learning/projects/available.html"

    def get_queryset(self):
        # FIXME: Respect timezone, hard coded city code
        current_term_index = get_current_term_index()
        qs = (Project.objects
              .filter(semester__index=current_term_index)
              .exclude(status=Project.Statuses.CANCELED)
              .select_related("semester")
              .prefetch_related("students", "reviewers", "supervisors")
              .annotate(reviewers_cnt=Count("reviewers"))
              .annotate(
                have_reviewers=Case(
                    When(reviewers_cnt__gt=0, then=Value(1)),
                    default=Value(0),
                    output_field=BooleanField()))
              .order_by("have_reviewers", "name", "pk"))
        if not self.request.user.is_curator:
            qs = qs.filter(project_type=ProjectTypes.practice)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_term"] = Semester.get_current()
        if self.request.user.is_curator:
            context["filter"] = self.filterset
        else:
            context["filter"] = ""
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_curator:
            return super().get(request, *args, **kwargs)
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)
        self.object_list = self.filterset.qs
        context = self.get_context_data(filter=self.filterset,
                                        object_list=self.object_list)
        return self.render_to_response(context)


class ProjectListView(CuratorOnlyMixin, BaseFilterView, generic.ListView):
    strict = False
    paginate_by = 50
    filterset_class = ProjectsFilter
    context_object_name = "projects"
    template_name = "learning/projects/all.html"

    def get_queryset(self):
        queryset = (Project.objects
                    .select_related("semester")
                    .prefetch_related("students", "reviewers", "supervisors")
                    .order_by("-semester__index", "name", "pk"))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context


class StudentProjectsView(StudentOnlyMixin, generic.ListView):
    context_object_name = "projects"
    template_name = "learning/projects/student_projects.html"

    def get_queryset(self):
        return (ProjectStudent.objects
                .filter(student=self.request.user)
                .select_related("project", "project__semester", "student")
                .order_by("-project__semester__index", "project__name"))


class ProjectDetailView(CreateView):
    model = Report
    form_class = ReportForm
    context_object_name = "report"
    template_name = "learning/projects/project_detail.html"

    def get(self, request, *args, **kwargs):
        project = self.get_project()
        project_student = self.get_authenticated_project_student(project)
        context = self.get_context_data(project=project,
                                        project_student=project_student)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        project = self.get_project()
        if not project.is_active():
            return HttpResponseForbidden()
        project_student = self.get_authenticated_project_student(project)
        if project_student is None or project_student.has_final_grade():
            return HttpResponseForbidden()
        form = self.get_form(data=request.POST, files=request.FILES,
                             project_student=project_student)
        if form.is_valid():
            rp = form.cleaned_data.get('reporting_period')
            # Allow sending report after deadline
            if (not rp or not rp.is_started(project) or
                    rp.term_id != project.semester_id):
                return HttpResponseForbidden()
            return self.form_valid(form)
        else:
            # Inline `form_invalid` to pass `project` for context
            context = self.get_context_data(project=project,
                                            project_student=project_student,
                                            form=form)
            return self.render_to_response(context)

    def get_project(self):
        queryset = (Project.objects
                    .select_related("semester")
                    .prefetch_related(
                        Prefetch(
                            "projectstudent_set",
                            queryset=(ProjectStudent.objects
                                      .select_related("student")
                                      .prefetch_related("reports"))
                        ),
                        "reviewers"))
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        try:
            lookup = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        except KeyError:
            msg = "Lookup field '%s' was not provided in view kwargs to '%s'"
            raise ImproperlyConfigured(msg % (lookup_url_kwarg,
                                              self.__class__.__name__))
        return get_object_or_404(queryset, **lookup)

    def get_authenticated_project_student(self, project):
        """
        Returns related student_project instance if authenticated user
        is student participant of current project
        """
        for ps in project.projectstudent_set.all():
            if ps.student == self.request.user:
                return ps
        return None

    def get_success_url(self):
        messages.success(self.request,
                         _("Report successfully has been sent"),
                         extra_tags="timeout")
        return self.object.get_absolute_url()

    def get_context_data(self, project, project_student, **kwargs):
        user = self.request.user
        you_enrolled = user in project.reviewers.all()
        can_send_report = (project_student and
                           not project_student.has_final_grade())
        # FIXME: только для залогиненных.
        key = ReportingPeriodKey(project.branch_id, project.project_type)
        reporting_periods = (ReportingPeriod.get_periods(term_id=project.semester_id)
                             .get(key, []))
        reports = Report.objects.filter(project_student__project=project)
        context = {
            "project": project,
            "project_student": project_student,
            "reports": reports,
            "reporting_periods": reporting_periods,
            "can_send_report": can_send_report,
            "you_enrolled": you_enrolled,
            "can_enroll": (
                (user.is_project_reviewer or user.is_curator)
                and project.is_active()),
            "can_view_report": you_enrolled or user.is_curator,
            "results_formset": ResultsFormSet(
                queryset=project.projectstudent_set.select_related("student")
            )
        }
        return context


class ProjectResultsView(CuratorOnlyMixin, BaseModelFormSetView):
    """
    XXX: Assumed only for valid POST-actions.
    The probability of validation errors is about 0.0001%!
    (Only if data was compromised)
    """
    http_method_names = ["post", "put"]
    model = ProjectStudent
    form_class = StudentResultsModelForm

    def formset_invalid(self, formset):
        msg = "<br>".join(" ".join(errors) for e in formset.errors
                          for errors in e.values())
        messages.error(self.request, "Данные не сохранены!<br>" + msg)
        url = reverse("projects:project_detail", args=[self.kwargs.get("pk")])
        return HttpResponseRedirect(url)

    def get_success_url(self):
        messages.success(self.request, _("Данные успешно сохранены"),
                         extra_tags='timeout')
        return reverse("projects:project_detail",
                       args=[self.kwargs.get("pk")])


class ProjectPrevNextView(generic.RedirectView):
    """
    Based on `direction` get prev or next project relative to passed project id
    """
    direction = None

    # TODO: add tests
    def get_queryset(self):
        # FIXME: Respect timezone, hard coded city code
        # FIXME: get timezone by project_id
        current_term_index = get_current_term_index()
        qs = (Project.objects
              .filter(semester__index=current_term_index)
              .exclude(status=Project.Statuses.CANCELED)
              .annotate(reviewers_cnt=Count("reviewers"))
              .annotate(
                have_reviewers=Case(
                    When(reviewers_cnt__gt=0, then=Value(1)),
                    default=Value(0),
                    output_field=BooleanField())
              )
              .values_list("pk", flat=True)
              .order_by("have_reviewers", "name", "pk"))
        if not self.request.user.is_curator:
            qs = qs.filter(project_type=ProjectTypes.practice)
        return qs

    def get_redirect_url(self, *args, **kwargs):
        project_id = int(self.kwargs.get("project_id"))
        # Not so many projects to care about performance
        qs = self.get_queryset()
        if self.direction == "prev":
            qs = qs.reverse()
        next_project_id, first, prev_id = (None,) * 3
        for p in qs:
            if prev_id == project_id:
                next_project_id = p
                break
            if first is None:
                # Rotate if we didn't find next project
                next_project_id = p
                first = p
            prev_id = p
        return reverse("projects:project_detail", args=[next_project_id])


class ProjectEnrollView(ProjectReviewerGroupOnlyMixin, generic.View):
    http_method_names = ['post']
    raise_exception = True  # raise if not in project_reviewer group

    def post(self, request, *args, **kwargs):
        project_pk = kwargs.get("pk")
        project = get_object_or_404(
            Project.objects
                   .select_related("semester")
                   .filter(pk=project_pk)
        )
        if not project.is_active():
            return HttpResponseForbidden()

        project.reviewers.add(request.user.pk)
        project.save()
        # TODO: add notification when user unsubscribed?
        notify.send(
            request.user,  # actor
            type=NotificationTypes.PROJECT_REVIEWER_ENROLLED,
            verb='enrolled in',
            action_object=project,
            public=False,
            recipient="")
        messages.success(self.request,
                         _("You successfully enrolled on the project"),
                         extra_tags='timeout')
        url = reverse("projects:project_detail", args=[project.pk])
        return HttpResponseRedirect(url)


class ReportView(FormMixin, generic.DetailView):
    model = Report
    http_method_names = ["get", "post", "put"]
    context_object_name = "report"
    template_name = "learning/projects/report.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_author = None
        self.is_project_reviewer = None
        self.is_curator = None

    def get_object(self, queryset=None):
        report_id = self.kwargs.get("report_id")
        report = get_object_or_404(
            Report.objects
            .filter(pk=report_id)
            .select_related(
                "reporting_period",
                "project_student",
                "project_student__student",
                "project_student__project",
                "project_student__project__semester"))
        return report

    def set_roles(self, report):
        """Cache roles of authenticated user in current project """
        user = self.request.user
        self.is_author = report.project_student.student_id == user.pk
        self.is_project_reviewer = (
            user in report.project_student.project.reviewers.all())
        self.is_curator = user.is_curator

    def has_permissions(self, report):
        """Check authenticated user has access to GET- or POST-actions"""
        is_author = self.is_author
        is_project_reviewer = self.is_project_reviewer
        is_curator = self.request.user.is_curator
        is_project_participant = is_author or is_project_reviewer or is_curator
        add_comment_action = ReportCommentForm.prefix in self.request.POST
        if is_curator:
            return True
        # Restrict send comment for all except curators if review is completed
        if add_comment_action and report.status in [report.COMPLETED,
                                                    report.SUMMARY]:
            return False
        # Hide view for reviewers until report status is `SENT`.
        if is_project_reviewer and report.status == Report.SENT:
            return False
        return is_project_participant

    def form_valid(self, form):
        model = form.save()
        return super(ReportView, self).form_valid(form)

    def form_invalid(self, **kwargs):
        messages.error(self.request, _("Data not saved. Fix errors."))
        context = self.get_context_data(**kwargs)
        context["has_errors"] = True
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # skip FormMixin.get_context_data() here
        context = super(FormMixin, self).get_context_data(**kwargs)
        report = context[self.context_object_name]
        form_kwargs = {
            "report": report,
            "author": self.request.user
        }
        if report.status == report.SUMMARY and self.request.user.is_curator:
            context[ReportSummarizeForm.prefix] = ReportSummarizeForm(
                instance=report)
        if ReportStatusForm.prefix not in context:
            context[ReportStatusForm.prefix] = ReportStatusForm(
                instance=report)
        if ReportCuratorAssessmentForm.prefix not in context:
            context[ReportCuratorAssessmentForm.prefix] = \
                ReportCuratorAssessmentForm(instance=report)
        if ReportCommentForm.prefix not in context:
            context[ReportCommentForm.prefix] = ReportCommentForm(**form_kwargs)
        own_review = self.get_review_object(report)
        if ReportReviewForm.prefix not in context:
            form_kwargs["instance"] = own_review
            context[ReportReviewForm.prefix] = ReportReviewForm(**form_kwargs)
            criteria = own_review.criteria if own_review else None
            # FIXME: form_class depends on project type
            context["review_criteria_form"] = PracticeCriteriaForm(instance=criteria)
        comments = (ReportComment.objects
                    .filter(report=report)
                    .order_by('created')
                    .select_related('author'))
        context["comments"] = comments
        context['clean_comments_json'] = comment_persistence.get_hashes_json()
        context["can_comment"] = self.can_comment(report, own_review)
        context["can_assess"] = (report.status == report.SENT and
                                 self.request.user.is_curator)
        context["is_reviewer"] = self.is_project_reviewer
        context["is_author"] = self.is_author
        context["reviewers"] = report.project_student.project.reviewers.all()
        # Preliminary scores
        if self.request.user.is_curator:
            context['reviews'] = (Review.objects
                                  .filter(report=report)
                                  .select_related('reviewer')
                                  .prefetch_related('criteria'))
            # Collect those who without report at all
            has_reviews = [r.reviewer_id for r in context['reviews']]
            context["without_reviews"] = [r for r in context["reviewers"]
                                          if r.pk not in has_reviews]
        else:
            context['reviews'] = set()
            context["without_reviews"] = set()
        context['own_review'] = own_review
        return context

    def can_comment(self, report, review):
        # When report has sent, reviewers can't see the whole page until
        # next status
        if report.status == report.SENT:
            return True
        # On review stage reviewers can't comment after review was completed
        if report.status == report.REVIEW:
            if (self.is_project_reviewer and not self.is_curator and
                    review and review.is_completed):
                return False
            return True
        # On last 2 stages nobody can comment
        return False

    def get_review_object(self, report):
        if report.status == report.SENT:
            # No reviews at all on this stage
            return None
        try:
            review = Review.objects.get(report=report,
                                        reviewer=self.request.user)
        except Review.DoesNotExist:
            review = None
        return review

    def get(self, request, *args, **kwargs):
        report = self.object = self.get_object()
        self.set_roles(report)
        if not self.has_permissions(self.object):
            return redirect_to_login(request.get_full_path())
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        report = self.object = self.get_object()
        self.set_roles(report)
        if not self.has_permissions(self.object):
            return HttpResponseForbidden()
        if ReportCommentForm.prefix not in request.POST:
            return HttpResponseBadRequest()
        # TODO: Check `can_comment` permissions
        form_name = ReportCommentForm.prefix
        form_kwargs = self.get_form_kwargs()
        form = ReportCommentForm(**form_kwargs)
        if form.is_valid():
            response = self.form_valid(form)
            success_msg = _("Comment successfully added.")
            messages.success(self.request, success_msg, extra_tags='timeout')
            return response
        else:
            return self.form_invalid(**{form_name: form})

    def get_form_kwargs(self):
        form_kwargs = super(ReportView, self).get_form_kwargs()
        # Required fields for both models, not represented in form
        form_kwargs["report"] = self.object
        form_kwargs["author"] = self.request.user
        return form_kwargs

    def get_success_url(self):
        project_pk = self.kwargs.get("project_pk")
        if self.is_author:
            url_name = "projects:student_project_report"
        else:
            url_name = "projects:project_report"
        return reverse_lazy(
            url_name,
            kwargs={
                "project_pk": project_pk,
                "report_id": self.object.pk
            }
        )


class ProcessReviewFormView(LoginRequiredMixin, ModelFormMixin, View):
    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        try:
            review = (Review.objects
                      .select_related("report",
                                      "report__project_student",
                                      "report__project_student__project")
                      .get(report_id=report_id, reviewer=request.user))
            criteria = PracticeCriteria.objects.get(review=review)
            report = review.report
        except Review.DoesNotExist:
            review = None
            criteria = None
            report = get_object_or_404(Report.objects.filter(pk=report_id))
        # Check permissions
        if report.status != report.REVIEW:
            return HttpResponseForbidden()
        if request.user not in report.project_student.project.reviewers.all():
            return HttpResponseForbidden()
        review_form = ReportReviewForm(data=request.POST,
                                       instance=review,
                                       report=report,
                                       author=request.user)
        criteria_form = PracticeCriteriaForm(data=request.POST,
                                             instance=criteria)
        if review_form.is_valid() and criteria_form.is_valid():
            with transaction.atomic():
                review = review_form.save()
                criteria_form.instance.review = review
                criteria = criteria_form.save()
                review.criteria = criteria
                # FIXME: No need to send signals here
                review.save()
            if review.is_completed:
                self.send_notification_to_curators(review)
            if ReportReviewForm.prefix + "-draft" in request.POST:
                success_msg = _("The draft successfully saved.")
            else:
                success_msg = _("The review successfully saved.")
            messages.success(request, success_msg, extra_tags='timeout')
            return HttpResponseRedirect(report.get_absolute_url())
        else:
            messages.error(self.request, _("Data not saved. Fix errors."))
            return HttpResponseRedirect(report.get_absolute_url())

    def send_notification_to_curators(self, review):
        """Reviewer completed assessment"""
        curators = (User.objects
                    .has_role(Roles.CURATOR_PROJECTS)
                    # FIXME: replace with CURATOR role
                    .filter(is_staff=True))
        report = (Report.objects
                  .select_related("project_student",
                                  "project_student__project",
                                  "project_student__student")
                  .get(pk=review.report_id))
        other_reports = (Report.objects
            .filter(project_student__project=report.project_student.project)
            .exclude(project_student=report.project_student)
            .values_list("pk", flat=True))
        student = report.project_student.student
        student_declension = ""
        if student.gender == GenderTypes.FEMALE:
            student_declension = "a"
        context = {
            "report_id": report.pk,
            "student_pk": student.pk,
            "student": student.get_short_name(),
            "student_declension": student_declension,
            "project_pk": report.project_student.project.pk,
            "project_name": report.project_student.project.name,
            "other_reports": other_reports
        }
        for recipient in curators:
            notify.send(
                self.request.user,  # Reviewer
                type=NotificationTypes.PROJECT_REPORT_REVIEW_COMPLETED,
                verb='changed',
                action_object=review,
                target=report,
                recipient=recipient,
                data=context
            )


class ReportUpdateViewMixin(CuratorOnlyMixin, BaseUpdateView):
    http_method_names = ["post", "put"]
    model = Report
    pk_url_kwarg = 'report_id'

    def get_success_url(self):
        messages.success(self.request,
                         self.get_success_msg(),
                         extra_tags='timeout')
        return self.object.get_absolute_url()

    @staticmethod
    def get_success_msg():
        return _("Report was successfully updated.")

    @staticmethod
    def get_error_msg(form):
        return _("Data not saved. Check errors.")

    def form_invalid(self, form):
        """
        Silently fail and redirect. Form will be invalid only if you fake data.
        """
        messages.error(self.request, self.get_error_msg(form))
        return HttpResponseRedirect(reverse(
            "projects:project_report",
            kwargs={
                "project_pk": self.kwargs.get("project_pk"),
                "report_id": self.kwargs.get("report_id")
            }
        ))


class ReportUpdateStatusView(ReportUpdateViewMixin):
    form_class = ReportStatusForm

    @staticmethod
    def get_success_msg():
        return _("Status was successfully updated.")

    @staticmethod
    def get_error_msg(form):
        msg = "<br>".join("<br>".join(errors) for errors in
                          form.errors.values())
        return "Статус не был обновлён.<br>" + msg

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related("project_student__project")

    def form_valid(self, form):
        response = super().form_valid(form)
        report = self.object
        project_id = report.project_student.project_id
        if "status" in form.changed_data and report.status == Report.REVIEW:
            project_students = (ProjectStudent.objects
                                .filter(project_id=project_id)
                                .select_related("student")
                                .prefetch_related("reports"))
            reporting_period = report.reporting_period
            all_reports_in_review_state = False
            reports = []
            for ps in project_students:
                # FIXME: N запросов
                report = ps.get_report(reporting_period)
                if report:
                    if report.status != Report.REVIEW:
                        break
                    reports.append((report.pk, ps.student.get_short_name()))
                else:
                    # Don't take into account if student already has
                    # unsatisfactory grade. It means he left the project.
                    if ps.final_grade != ProjectStudent.GRADES.UNSATISFACTORY:
                        break
            else:
                all_reports_in_review_state = True
            if all_reports_in_review_state:
                self.send_email_notification(reports)
        return response

    def send_email_notification(self, reports):
        """ Send notification to reviewers that all reports in review state """
        report = self.object
        context = {
            "project_pk": report.project_student.project.pk,
            "project_name": report.project_student.project.name,
            "reports": reports
        }
        # Consider situation when we rollback all reports to `review` stage.
        # In that case we shouldn't send notification to those reviewers
        # who already sent review.
        has_reviews = Review.objects.filter(
            report=report).values_list("reviewer_id", flat=True)
        reviewers = report.project_student.project.reviewers.exclude(
            id__in=has_reviews).all()
        for recipient in reviewers:
            notify.send(
                self.request.user,  # Curator who changed status
                type=NotificationTypes.PROJECT_REPORTS_IN_REVIEW_STATE,
                verb='changed',
                target=report,
                recipient=recipient,
                data=context
            )


class ReportCuratorAssessmentView(ReportUpdateViewMixin):
    form_class = ReportCuratorAssessmentForm

    @staticmethod
    def get_success_msg():
        return _("Grades successfully updated.")


class ReportCuratorSummarizeView(ReportUpdateViewMixin):
    form_class = ReportSummarizeForm

    @staticmethod
    def get_success_msg():
        return _("The report results are summed up successfully.")

    def form_valid(self, form):
        response = super().form_valid(form)

        # Send email notification to student participant
        if self.object.status == self.object.COMPLETED:
            self.send_email_notification()
        return response

    def send_email_notification(self):
        """Email notification with final results and comments for student"""
        # FIXME: test db hitting
        context = {
            "project_name": self.object.project_student.project.name,
            "final_score": self.object.final_score,
            "message": self.object.final_score_note
        }
        notify.send(
            self.request.user,  # Curator who complete reviewing
            type=NotificationTypes.PROJECT_REPORT_COMPLETED,
            verb='complete',
            # In this case action_object and target are the same
            target=self.object,
            recipient=self.object.project_student.student,
            data=context
        )


class ReportAttachmentDownloadView(LoginRequiredMixin, generic.View):

    def get(self, request, *args, **kwargs):
        try:
            attachment_type, pk = hashids.decode(kwargs['sid'])
        except IndexError:
            raise Http404
        projects_app = apps.get_app_config("projects")
        user = request.user
        if attachment_type == projects_app.REPORT_COMMENT_ATTACHMENT:
            qs = ReportComment.objects.filter(pk=pk)
            if not user.is_project_reviewer and not user.is_curator:
                qs = qs.filter(report__project_student__student=user)
            comment = get_object_or_404(qs)
            if not comment.attached_file:
                raise Http404
            file_name = comment.attached_file_name
            file_url = comment.attached_file.url
        elif attachment_type == projects_app.REPORT_ATTACHMENT:
            qs = Report.objects.filter(pk=pk)
            if not user.is_project_reviewer and not user.is_curator:
                qs = qs.filter(project_student__student=user)
            report = get_object_or_404(qs)
            if not report.file:
                raise Http404
            file_name = report.file_name
            file_url = report.file.url
        else:
            raise Http404

        response = HttpResponse()
        del response['Content-Type']
        response['Content-Disposition'] = "attachment; filename={}".format(
            file_name)
        response['X-Accel-Redirect'] = file_url
        return response

