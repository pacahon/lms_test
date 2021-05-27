from django.urls import include, path, re_path, register_converter

from courses.urls import RE_COURSE_URI
from learning.gradebook.views import (
    GradeBookCSVView, GradeBookView, ImportAssignmentScoresByEnrollmentIDView,
    ImportAssignmentScoresByStepikIDView, ImportAssignmentScoresByYandexLoginView
)
from staff.api.views import StudentSearchJSONView
from staff.views import (
    AdmissionApplicantsReportView, AdmissionExamReportView,
    CourseParticipantsIntersectionView, ExportsView, FutureGraduateDiplomasCSVView,
    FutureGraduateDiplomasTeXView, FutureGraduateStatsView, GradeBookListView,
    HintListView, InterviewerFacesView, InvitationStudentsProgressReportView,
    OfficialDiplomasCSVView, OfficialDiplomasListView, OfficialDiplomasTeXView,
    ProgressReportForSemesterView, ProgressReportFullView, StudentFacesView,
    StudentSearchCSVView, StudentSearchView, SurveySubmissionsReportView,
    SurveySubmissionsStatsView, WillGraduateStatsReportView, autograde_projects,
    create_alumni_profiles
)

app_name = 'staff'


class SupportedExportFormatConverter:
    regex = 'csv|xlsx'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(SupportedExportFormatConverter, 'export_fmt')


urlpatterns = [
    path('gradebooks/', include([
        path('', GradeBookListView.as_view(), name='gradebook_list'),
        re_path(RE_COURSE_URI, include([
            path('', GradeBookView.as_view(is_for_staff=True, permission_required="teaching.view_gradebook"), name='gradebook'),
            path('csv/', GradeBookCSVView.as_view(permission_required="teaching.view_gradebook"), name='gradebook_csv'),
        ])),
        path('<int:course_id>/import/', include([
            path('stepic', ImportAssignmentScoresByStepikIDView.as_view(), name='gradebook_import_scores_by_stepik_id'),
            path('yandex', ImportAssignmentScoresByYandexLoginView.as_view(), name='gradebook_import_scores_by_yandex_login'),
            path('enrollments', ImportAssignmentScoresByEnrollmentIDView.as_view(), name='gradebook_import_scores_by_enrollment_id'),
        ])),
    ])),

    path('student-search/', StudentSearchView.as_view(), name='student_search'),
    path('student-search.json', StudentSearchJSONView.as_view(), name='student_search_json'),
    # Note: CSV view doesn't use pagination
    path('student-search.csv', StudentSearchCSVView.as_view(), name='student_search_csv'),


    path('faces/', StudentFacesView.as_view(), name='student_faces'),
    path('faces/interviewers/', InterviewerFacesView.as_view(), name='interviewer_faces'),

    path('commands/create-alumni-profiles/', create_alumni_profiles, name='create_alumni_profiles'),
    path('commands/autograde-projects/', autograde_projects, name='autograde_projects'),

    path('course-participants/', CourseParticipantsIntersectionView.as_view(), name='course_participants_intersection'),


    path('exports/', ExportsView.as_view(), name='exports'),

    # FIXME: Is it useful?
    re_path(r'^reports/learning/will_graduate/(?P<output_format>csv|xlsx)/$', WillGraduateStatsReportView.as_view(), name='exports_report_will_graduate'),
    re_path(r'^reports/future-graduates/(?P<branch_id>\d+)/', include([
        path('stats/', FutureGraduateStatsView.as_view(), name='export_future_graduates_stats'),
        path('tex/', FutureGraduateDiplomasTeXView.as_view(), name='exports_future_graduates_diplomas_tex'),
        path('csv/', FutureGraduateDiplomasCSVView.as_view(), name='exports_future_graduates_diplomas_csv'),
    ])),
    path('reports/students-progress/', include([
        re_path(r'^(?P<output_format>csv|xlsx)/(?P<on_duplicate>max|last)/$', ProgressReportFullView.as_view(), name='students_progress_report'),
        re_path(r'^terms/(?P<term_year>\d+)/(?P<term_type>\w+)/(?P<output_format>csv|xlsx)/$', ProgressReportForSemesterView.as_view(), name='students_progress_report_for_term'),
        re_path(r'^invitations/(?P<invitation_id>\d+)/(?P<output_format>csv|xlsx)/$', InvitationStudentsProgressReportView.as_view(), name='students_progress_report_for_invitation'),
    ])),
    re_path(r'^reports/official-diplomas/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/', include([
        path('list/', OfficialDiplomasListView.as_view(), name='exports_official_diplomas_list'),
        path('tex/', OfficialDiplomasTeXView.as_view(), name='exports_official_diplomas_tex'),
        path('csv/', OfficialDiplomasCSVView.as_view(), name='exports_official_diplomas_csv'),
    ])),
    path('reports/admission/<int:campaign_id>/applicants/<export_fmt:output_format>/', AdmissionApplicantsReportView.as_view(), name='exports_report_admission_applicants'),
    path('reports/admission/<int:campaign_id>/exam/<export_fmt:output_format>/', AdmissionExamReportView.as_view(), name='exports_report_admission_exam'),
    re_path(r'^reports/surveys/(?P<survey_pk>\d+)/(?P<output_format>csv|xlsx)/$', SurveySubmissionsReportView.as_view(), name='exports_report_survey_submissions'),
    re_path(r'^reports/surveys/(?P<survey_pk>\d+)/txt/$', SurveySubmissionsStatsView.as_view(), name='exports_report_survey_submissions_stats'),


    path('warehouse/', HintListView.as_view(), name='staff_warehouse'),
]


