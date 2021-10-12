from typing import Any, Optional

from djangorestframework_camel_case.render import (
    CamelCaseBrowsableAPIRenderer, CamelCaseJSONRenderer
)
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import ListAPIView, UpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _

from api.authentication import TokenAuthentication
from api.mixins import ApiErrorsMixin
from api.permissions import CuratorAccessPermission
from api.utils import get_serializer_fields, inline_serializer
from api.views import APIBaseView
from auth.mixins import RolePermissionRequiredMixin
from core.api.fields import CharSeparatedField, ScoreField
from core.http import AuthenticatedAPIRequest, HttpRequest
from courses.api.serializers import CourseTeacherSerializer
from courses.models import Assignment, Course
from courses.permissions import CreateAssignment
from courses.selectors import course_personal_assignments, personal_assignments_list
from learning.api.serializers import (
    BaseStudentAssignmentSerializer, CourseAssignmentSerializer,
    CourseNewsNotificationSerializer, MyCourseSerializer, MyEnrollmentSerializer,
    StudentAssignmentAssigneeSerializer, StudentProfileSerializer, UserSerializer
)
from learning.models import CourseNewsNotification, Enrollment, StudentAssignment
from learning.permissions import EditStudentAssignment, ViewEnrollments


class CourseNewsUnreadNotificationsView(ListAPIView):
    permission_classes = [CuratorAccessPermission]
    serializer_class = CourseNewsNotificationSerializer

    def get_queryset(self):
        return (CourseNewsNotification.unread
                .filter(course_offering_news_id=self.kwargs.get('news_pk'))
                .select_related("user")
                .order_by("user__last_name"))


class CourseList(ListAPIView):
    """
    List courses the authenticated user participated in as a teacher.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MyCourseSerializer

    def get_queryset(self):
        return (Course.objects
                .filter(teachers=self.request.user)
                .select_related('meta_course', 'semester', 'main_branch'))


class CourseAssignmentList(RolePermissionRequiredMixin, ApiErrorsMixin, ListAPIView):
    """List assignments of the course."""
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [CreateAssignment]
    serializer_class = CourseAssignmentSerializer
    renderer_classes = (CamelCaseJSONRenderer, CamelCaseBrowsableAPIRenderer)
    course: Course

    def initial(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course.objects.get_queryset(), pk=kwargs['course_id'])
        super().initial(request, *args, **kwargs)

    def get_permission_object(self) -> Course:
        return self.course

    def get_queryset(self):
        return (Assignment.objects
                .filter(course_id=self.kwargs['course_id'])
                .order_by('-deadline_at'))


class EnrollmentList(ListAPIView):
    """
    List students enrolled in the course.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, ViewEnrollments]
    serializer_class = MyEnrollmentSerializer
    course: Course

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.course = get_object_or_404(Course.objects.get_queryset(),
                                        pk=kwargs['course_id'])
        self.check_object_permissions(self.request, self.course)

    def get_queryset(self):
        return (Enrollment.active
                .select_related('student_profile__user',
                                'student_profile__branch')
                .filter(course_id=self.kwargs['course_id']))


class PersonalAssignmentList(RolePermissionRequiredMixin, APIBaseView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [CreateAssignment]
    renderer_classes = (CamelCaseJSONRenderer, CamelCaseBrowsableAPIRenderer)
    course: Course

    class FilterSerializer(serializers.Serializer):
        assignments = CharSeparatedField(label='test', allow_blank=True, required=False)

    class OutputSerializer(serializers.ModelSerializer):
        state = serializers.SerializerMethodField()
        score = ScoreField(coerce_to_string=True)
        student = UserSerializer(fields=('id', 'first_name', 'last_name', 'patronymic'))
        assignee = inline_serializer(fields={
            "id": serializers.IntegerField(),
            "teacher": UserSerializer(fields=('id', 'first_name', 'last_name', 'patronymic'))
        })
        activity = serializers.SerializerMethodField()

        class Meta:
            model = StudentAssignment
            fields = ('id', 'assignment_id', 'score', 'state', 'student',
                      'assignee', 'activity')

        def get_state(self, obj: StudentAssignment):
            return obj.state.value

        def get_activity(self, obj: StudentAssignment) -> Optional[str]:
            """Returns latest activity."""
            if not obj.meta or 'stats' not in obj.meta:
                return None
            return obj.meta['stats'].get('activity', None)

    def initial(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course.objects.get_queryset(), pk=kwargs['course_id'])
        super().initial(request, *args, **kwargs)

    def get_permission_object(self) -> Course:
        return self.course

    def get(self, request: AuthenticatedAPIRequest, **kwargs: Any):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)
        personal_assignments = course_personal_assignments(course=self.course,
                                                           filters=filters_serializer.validated_data)
        data = self.OutputSerializer(personal_assignments, many=True).data
        return Response(data)


class StudentAssignmentUpdate(UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [EditStudentAssignment]
    serializer_class = BaseStudentAssignmentSerializer
    lookup_url_kwarg = 'student_id'
    lookup_field = 'student_id'

    def get_queryset(self):
        return (StudentAssignment.objects
                .filter(assignment_id=self.kwargs['assignment_id'])
                .select_related('assignment')
                .order_by())


class StudentAssignmentAssigneeUpdate(UpdateAPIView):
    permission_classes = [EditStudentAssignment]
    serializer_class = StudentAssignmentAssigneeSerializer
    lookup_url_kwarg = 'student_id'
    lookup_field = 'student_id'

    def get_queryset(self):
        return (StudentAssignment.objects
                .filter(assignment_id=self.kwargs['assignment_id'])
                .select_related('assignment__course')
                .order_by())
