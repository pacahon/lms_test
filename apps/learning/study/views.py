from typing import Iterable

from django.apps import apps
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.utils.translation import gettext_lazy as _
from django.views import generic
from isoweek import Week
from vanilla import TemplateView

from auth.mixins import PermissionRequiredMixin
from core.exceptions import Redirect
from core.urls import reverse
from courses.calendar import CalendarEventW
from courses.constants import SemesterTypes
from courses.models import Semester, Course, CourseTeacher
from courses.utils import get_current_term_pair, MonthPeriod, \
    extended_month_date_range
from courses.views import WeekEventsView, MonthEventsCalendarView
from info_blocks.constants import CurrentInfoBlockTags
from info_blocks.models import InfoBlock
from info_blocks.permissions import ViewInternships
from learning import utils
from learning.calendar import get_student_calendar_events, get_calendar_events
from learning.forms import AssignmentCommentForm
from learning.models import StudentAssignment, Enrollment, \
    AssignmentSubmissionTypes, AssignmentComment
from learning.permissions import ViewOwnStudentAssignments, \
    ViewOwnStudentAssignment, ViewCourses, \
    CreateAssignmentCommentAsLearner, CreateOwnAssignmentSolution
from learning.roles import Roles
from learning.services import get_student_classes, get_student_profile
from learning.study.services import get_solution_form, get_draft_solution
from learning.views import AssignmentSubmissionBaseView
from learning.views.views import AssignmentCommentUpsertView, \
    AssignmentSubmissionUpsertView


class CalendarFullView(PermissionRequiredMixin, MonthEventsCalendarView):
    """
    Shows all non-course events and classes in the city of
    the authenticated student.
    """
    permission_required = "study.view_schedule"

    def get_events(self, month_period: MonthPeriod, **kwargs) -> Iterable:
        start_date, end_date = extended_month_date_range(month_period, expand=1)
        student_profile = get_student_profile(self.request.user,
                                              self.request.site)
        branches = [student_profile.branch_id]
        return get_calendar_events(branch_list=branches, start_date=start_date,
                                   end_date=end_date)


class CalendarPersonalView(CalendarFullView):
    """
    Shows non-course events filtered by student city and classes for courses
    on which authenticated student enrolled.
    """
    calendar_type = "student"
    template_name = "lms/courses/calendar.html"

    def get_events(self, month_period: MonthPeriod, **kwargs) -> Iterable:
        start_date, end_date = extended_month_date_range(month_period, expand=1)
        student_profile = get_student_profile(self.request.user,
                                              self.request.site)
        if not student_profile:
            return []
        return get_student_calendar_events(student_profile=student_profile,
                                           start_date=start_date,
                                           end_date=end_date)


class TimetableView(PermissionRequiredMixin, WeekEventsView):
    """Shows classes for courses which authorized student enrolled in"""
    template_name = "learning/study/timetable.html"
    permission_required = "study.view_schedule"

    def get_events(self, iso_year, iso_week) -> Iterable[CalendarEventW]:
        w = Week(iso_year, iso_week)
        in_range = [Q(date__range=[w.monday(), w.sunday()])]
        cs = get_student_classes(self.request.user, in_range, with_venue=True)
        for c in cs:
            yield CalendarEventW(c)


class StudentAssignmentListView(PermissionRequiredMixin, TemplateView):
    """Shows assignments for the current term."""
    template_name = "learning/study/assignment_list.html"
    permission_required = ViewOwnStudentAssignments.name

    def get_queryset(self, current_term):
        return (StudentAssignment.objects
                .for_user(self.request.user)
                .in_term(current_term)
                .order_by('assignment__deadline_at',
                          'assignment__course__meta_course__name',
                          'pk'))

    def get_context_data(self, **kwargs):
        current_term = Semester.get_current()
        student = self.request.user
        assignment_list = self.get_queryset(current_term)
        enrolled_in = (Enrollment.active
                       .filter(course__semester=current_term, student=student)
                       .values_list("course", flat=True))
        in_progress, archive = utils.split_on_condition(
            assignment_list,
            lambda sa: not sa.assignment.deadline_is_exceeded and
                       sa.assignment.course_id in enrolled_in)
        archive.reverse()
        # Map student projects in current term to related reporting periods
        reporting_periods = None
        if apps.is_installed("projects"):
            from projects.services import get_project_reporting_periods
            reporting_periods = get_project_reporting_periods(student,
                                                              current_term)
        context = {
            'assignment_list_open': in_progress,
            'assignment_list_archive': archive,
            'tz_override': student.time_zone,
            'reporting_periods': reporting_periods
        }
        return context


class StudentAssignmentDetailView(PermissionRequiredMixin,
                                  AssignmentSubmissionBaseView):
    template_name = "learning/study/student_assignment_detail.html"
    permission_required = ViewOwnStudentAssignment.name

    def get_permission_object(self):
        return self.student_assignment

    def handle_no_permission(self):
        user = self.request.user
        if user.is_authenticated:
            course = self.student_assignment.assignment.course
            is_curator = Roles.CURATOR in user.roles
            is_teacher = Roles.TEACHER in user.roles
            if is_curator or (is_teacher and user in course.teachers.all()):
                # Redirects course teacher to the teaching/ section
                raise Redirect(to=self.student_assignment.get_teacher_url())
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sa = self.student_assignment
        comment_form = context['comment_form']
        add_comment_url = reverse('study:assignment_comment_create',
                                  kwargs={'pk': sa.pk})
        comment_form.helper.form_action = add_comment_url
        # Format datetime in student timezone
        context['timezone'] = self.request.user.time_zone
        # Solution Form
        draft_solution = get_draft_solution(self.request.user, sa)
        solution_form = get_solution_form(sa, instance=draft_solution)
        if solution_form:
            add_solution_url = reverse('study:assignment_solution_create',
                                       kwargs={'pk': sa.pk})
            solution_form.helper.form_action = add_solution_url
        context['solution_form'] = solution_form
        return context


class StudentAssignmentCommentCreateView(PermissionRequiredMixin,
                                         AssignmentCommentUpsertView):
    permission_required = CreateAssignmentCommentAsLearner.name
    submission_type = AssignmentSubmissionTypes.COMMENT

    def get_permission_object(self):
        return self.student_assignment

    def get_form_class(self):
        return AssignmentCommentForm

    def get_success_url(self):
        msg = _("Comment successfully saved")
        messages.success(self.request, msg)
        return self.student_assignment.get_student_url()

    def get_error_url(self):
        return self.student_assignment.get_student_url()


class StudentAssignmentSolutionCreateView(PermissionRequiredMixin,
                                          AssignmentSubmissionUpsertView):
    permission_required = CreateOwnAssignmentSolution.name
    submission_type = AssignmentSubmissionTypes.SOLUTION

    def get_permission_object(self):
        return self.student_assignment

    def get_form(self, data=None, files=None, **kwargs):
        form = get_solution_form(self.student_assignment, data=data,
                                 files=files, **kwargs)
        return form

    def get_success_url(self):
        msg = _("Solution successfully saved")
        messages.success(self.request, msg)
        return self.student_assignment.get_student_url()

    def post(self, request, *args, **kwargs):
        submission = AssignmentComment(
            student_assignment=self.student_assignment,
            author=request.user,
            type=self.submission_type,
            is_published=True)
        form = self.get_form(data=request.POST, files=request.FILES,
                             instance=submission)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_error_url(self):
        return self.student_assignment.get_student_url()


class CourseListView(PermissionRequiredMixin, generic.TemplateView):
    model = Course
    context_object_name = 'course_list'
    template_name = "learning/study/course_list.html"
    permission_required = ViewCourses.name

    def get_context_data(self, **kwargs):
        # Student enrollments
        auth_user = self.request.user
        student_enrollments = (Enrollment.active
                               .filter(student_id=auth_user)
                               .select_related("course")
                               .only('id', 'grade', 'course_id',
                                     'course__grading_type'))
        student_enrolled_in = {e.course_id: e for e in student_enrollments}
        # 1. Union courses from current term and which student enrolled in
        tz = auth_user.time_zone
        current_term = get_current_term_pair(tz)
        current_term_index = current_term.index
        in_current_term = Q(semester__index=current_term_index)
        enrolled_in = Q(id__in=list(student_enrolled_in))
        prefetch_teachers = Prefetch('course_teachers',
                                     queryset=CourseTeacher.get_queryset())
        student_profile = get_student_profile(auth_user, self.request.site)
        course_offerings = (Course.objects
                            .available_in(student_profile.branch_id)
                            .filter(in_current_term | enrolled_in)
                            .select_related('meta_course', 'semester',
                                            'main_branch')
                            .order_by('-semester__index',
                                      'meta_course__name', 'pk')
                            .prefetch_related(prefetch_teachers,
                                              "branches",
                                              "semester__enrollmentperiod_set"))
        # 2. And split them by type.
        ongoing_enrolled, ongoing_rest, archive_enrolled = [], [], []
        for course in course_offerings:
            if course.semester.index == current_term_index:
                if course.pk in student_enrolled_in:
                    # TODO: add `enrollments` to context and get grades explicitly in tmpl
                    course.enrollment = student_enrolled_in[course.pk]
                    ongoing_enrolled.append(course)
                else:
                    ongoing_rest.append(course)
            else:
                course.enrollment = student_enrolled_in[course.pk]
                archive_enrolled.append(course)
        context = {
            "ongoing_rest": ongoing_rest,
            "ongoing_enrolled": ongoing_enrolled,
            "archive_enrolled": archive_enrolled,
            # FIXME: what about custom template tag for this?
            # TODO: Add util method
            "current_term": "{} {}".format(
                SemesterTypes.values[current_term.type],
                current_term.year).capitalize()
        }
        return context


class UsefulListView(PermissionRequiredMixin, generic.ListView):
    context_object_name = "faq"
    template_name = "learning/study/useful.html"
    permission_required = "study.view_faq"

    def get_queryset(self):
        return (InfoBlock.objects
                .for_site(self.request.site)
                .with_tag(CurrentInfoBlockTags.USEFUL)
                .order_by("sort"))


class InternshipListView(PermissionRequiredMixin, generic.ListView):
    context_object_name = "faq"
    template_name = "learning/study/internships.html"
    permission_required = ViewInternships.name

    def get_queryset(self):
        return (InfoBlock.objects
                .for_site(self.request.site)
                .with_tag(CurrentInfoBlockTags.INTERNSHIP)
                .order_by("sort"))


class HonorCodeView(generic.ListView):
    context_object_name = "faq"
    template_name = "learning/study/honor_code.html"

    def get_queryset(self):
        return (InfoBlock.objects
                .for_site(self.request.site)
                .with_tag(CurrentInfoBlockTags.HONOR_CODE)
                .order_by("sort"))
