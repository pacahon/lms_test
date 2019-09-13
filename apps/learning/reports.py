# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from datetime import datetime
from operator import attrgetter
from typing import List

from django.db.models import Q, Prefetch, Count
from django.http import HttpResponse
from django.utils import formats
from pandas import DataFrame

from admission.models import Applicant
from core.reports import ReportFileOutput
from core.timezone.constants import DATE_FORMAT_RU, TIME_FORMAT_RU
from courses.models import Semester
from learning.models import AssignmentComment, Enrollment
from learning.permissions import has_master_degree
from learning.settings import StudentStatuses, GradeTypes
from projects.models import ReportComment, ProjectStudent
from users.constants import Roles
from users.models import User, SHADCourseRecord


class DataFrameResponse:
    @staticmethod
    def as_csv(df: DataFrame, filename):
        response = HttpResponse(df.to_csv(index=False),
                                content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = \
            'attachment; filename="{}.csv"'.format(filename)
        return response


class ProgressReport:
    """
    Generates report for students progress: courses, shad/online courses
    and projects.

    Usage example:
        # Call `.grade_honest` method on `Enrollment` model
        report = ProgressReport(grade_getter="grade_honest")
        custom_queryset = report.get_queryset().filter(pk=404)
        df: pandas.DataFrame = report.generate(custom_queryset)
        # Return response in csv format
        response = DataFrameResponse.as_csv(df, 'report_file.csv')
    """

    __metaclass__ = ABCMeta

    def __init__(self, grade_getter="grade_display"):
        self.grade_getter = attrgetter(grade_getter)
        self._all_courses = {}
        self._shads_max = 0
        self._online_max = 0
        self._projects_max = 0

    @abstractmethod
    def get_queryset(self):
        return User.objects.none()

    @abstractmethod
    def _generate_headers(self):
        return []

    @abstractmethod
    def _export_row(self, student):
        return []

    @abstractmethod
    def get_filename(self):
        return "report.txt"

    def generate(self, queryset=None) -> DataFrame:
        students = queryset if queryset is not None else self.get_queryset()
        # Aggregate max number of courses for each type. Result headers
        # depend on these values.
        shad_max, online_max, projects_max = 0, 0, 0
        for student in students:
            self.before_process_row(student)
            enrollments = {}
            for e in student.enrollments_progress:
                if self.skip_enrollment(e, student):
                    continue
                meta_course_id = e.course.meta_course_id
                self._all_courses[meta_course_id] = e.course.meta_course.name
                if meta_course_id in enrollments:
                    # Get the highest grade
                    if e.grade_weight > enrollments[meta_course_id].grade_weight:
                        enrollments[meta_course_id] = e
                else:
                    enrollments[meta_course_id] = e
            student.unique_enrollments = enrollments
            # FIXME: mb объединить before/after? сейчас такое разделение никак не используется вроде, проверить
            self.after_process_row(student)

            shad_max = max(shad_max, len(student.shads))
            online_max = max(online_max, len(student.online_courses))
            projects_max = max(projects_max, len(student.projects_progress))

        self._shads_max = shad_max
        self._online_max = online_max
        self._projects_max = projects_max

        return DataFrame.from_records(
            columns=self._generate_headers(),
            data=[self._export_row(s) for s in students],
            index='ID')

    def before_process_row(self, student):
        pass

    def after_process_row(self, student):
        pass

    def skip_enrollment(self, enrollment, student):
        """Hook for collecting some stats"""
        return False

    @staticmethod
    def get_courses_headers(courses_headers):
        if not courses_headers:
            return []
        return [h for _, course_name in courses_headers.items()
                for h in (f'{course_name}, оценка',
                          f'{course_name}, преподаватели')]

    @staticmethod
    def generate_projects_headers(headers_number):
        return [h for i in range(1, headers_number + 1)
                for h in (f'Проект {i}, название',
                          f'Проект {i}, оценка',
                          f'Проект {i}, руководители',
                          f'Проект {i}, семестр')]

    @staticmethod
    def generate_shad_courses_headers(headers_number):
        return [h for i in range(1, headers_number + 1)
                for h in ('ШАД, курс {}, название'.format(i),
                          'ШАД, курс {}, преподаватели'.format(i),
                          'ШАД, курс {}, оценка'.format(i))]

    @staticmethod
    def generate_online_courses_headers(headers_number):
        return [f'Онлайн-курс {i}, название' for i in
                range(1, headers_number + 1)]

    def _export_courses(self, student) -> List[str]:
        step = 2  # Number of columns for each course
        values = [''] * len(self._all_courses) * step
        for i, meta_course_id in enumerate(self._all_courses):
            if meta_course_id in student.unique_enrollments:
                enrollment = student.unique_enrollments[meta_course_id]
                teachers = ", ".join(t.get_full_name() for t in
                                     enrollment.course.teachers.all())
                values[i * step] = self.grade_getter(enrollment).lower()
                values[i * step + 1] = teachers
        return values

    def _export_projects(self, student) -> List[str]:
        step = 4  # Number of columns for each project
        values = [''] * self._projects_max * step
        for i, ps in enumerate(student.projects_progress):
            values[i * step] = ps.project.name
            values[i * step + 1] = ps.get_final_grade_display()
            values[i * step + 2] = ', '.join(s.get_abbreviated_name() for s in
                                             ps.project.supervisors.all())
            values[i * step + 3] = ps.project.semester
        return values

    def _export_shad_courses(self, student) -> List[str]:
        step = 3  # Number of columns for each shad course
        values = [''] * self._shads_max * step
        for i, course in enumerate(student.shads):
            values[i * step] = course.name
            values[i * step + 1] = course.teachers
            values[i * step + 2] = course.grade_display.lower()
        return values

    def _export_online_courses(self, student) -> List[str]:
        values = [''] * self._online_max
        for i, course in enumerate(student.online_courses):
            values[i] = course.name
        return values

    @staticmethod
    def links_to_application_forms(student):
        return "\r\n".join(a.get_absolute_url() for a in
                           student.applicant_set.all())


class ProgressReportForDiplomas(ProgressReport):
    def get_queryset(self):
        """
        Explicitly exclude rows with bad grades (or without) on query level.
        """
        return (User.objects
                .has_role(Roles.STUDENT,
                          Roles.GRADUATE,
                          Roles.VOLUNTEER)
                .student_progress(exclude_grades=[GradeTypes.UNSATISFACTORY,
                                                  GradeTypes.NOT_GRADED])
                .filter(status=StudentStatuses.WILL_GRADUATE)
                .select_related('graduate_profile')
                .prefetch_related('graduate_profile__academic_disciplines'))

    def _generate_headers(self):
        return [
            'ID',
            'Фамилия',
            'Имя',
            'Отчество',
            'Почта',
            'Университет',
            'Направления выпуска',
            'Успешно сдано курсов (Центр/Клуб/ШАД/Онлайн) всего',
            'Ссылка на анкету',
            *self.get_courses_headers(self._all_courses),
            *self.generate_shad_courses_headers(self._shads_max),
            *self.generate_projects_headers(self._projects_max),
        ]

    def _export_row(self, student):
        if hasattr(student, "graduate_profile"):
            disciplines = student.graduate_profile.academic_disciplines.all()
        else:
            disciplines = []
        return [
            student.pk,
            student.last_name,
            student.first_name,
            student.patronymic,
            student.email,
            student.university,
            " и ".join(s.name for s in disciplines),
            self.passed_courses_total(student),
            self.links_to_application_forms(student),
            *self._export_courses(student),
            *self._export_shad_courses(student),
            *self._export_projects(student),
        ]

    def get_filename(self):
        today = datetime.now()
        return "diplomas_{}".format(today.year)

    def passed_courses_total(self, student):
        """Don't consider adjustment for club courses"""
        center = 0
        club = 0
        shad = 0
        online = len(student.online_courses)
        for enrollment in student.unique_enrollments.values():
            if enrollment.grade in GradeTypes.satisfactory_grades:
                if enrollment.course.is_open:
                    club += 1
                else:
                    center += 1
        for course in student.shads:
            shad += int(course.grade in GradeTypes.satisfactory_grades)
        return center + club + shad + online


class ProgressReportFull(ProgressReport):
    def get_queryset(self):
        return (User.objects
                .has_role(Roles.STUDENT,
                          Roles.GRADUATE,
                          Roles.VOLUNTEER)
                .student_progress()
                .select_related('branch', 'graduate_profile')
                .defer('graduate_profile__testimonial', 'private_contacts',
                       'social_networks', 'bio')
                .prefetch_related(
                    Prefetch('applicant_set',
                             queryset=Applicant.objects.only('pk', 'user_id')),
                    'graduate_profile__academic_disciplines'))

    def _generate_headers(self):
        return [
            'ID',
            'Фамилия',
            'Имя',
            'Отчество',
            'Отделение',
            'Вольнослушатель',
            'Магистратура',
            'Почта',
            'Телефон',
            'ВУЗ',
            'Курс (на момент поступления)',
            'Год поступления',
            'Год программы обучения',
            'Год выпуска',
            'Яндекс ID',
            'Направления обучения',
            'Статус',
            'Дата статуса или итога (изменения)',
            'Комментарий',
            'Дата последнего изменения комментария',
            'Работа',
            'Ссылка на профиль',
            'Ссылка на анкету',
            'Успешно сдано курсов (Центр/Клуб/ШАД/Онлайн) всего',
            *self.get_courses_headers(self._all_courses),
            *self.generate_projects_headers(self._projects_max),
            *self.generate_shad_courses_headers(self._shads_max),
            *self.generate_online_courses_headers(self._online_max),
        ]

    def _export_row(self, student):
        total_success_passed = (
            sum(1 for c in student.unique_enrollments.values() if
                c.grade in GradeTypes.satisfactory_grades) +
            sum(1 for c in student.shads if
                c.grade in GradeTypes.satisfactory_grades) +
            sum(1 for _ in student.online_courses)
        )
        dt_format = f"{TIME_FORMAT_RU} {DATE_FORMAT_RU}"
        # FIXME: кажется, тут надо брать из профиля студента, только для дипломов у выпускника
        if hasattr(student, "graduate_profile"):
            disciplines = student.graduate_profile.academic_disciplines.all()
            graduation_year = student.graduate_profile.graduation_year
        else:
            disciplines = []
            graduation_year = ""
        return [
            student.pk,
            student.last_name,
            student.first_name,
            student.patronymic,
            student.branch,
            "+" if student.is_volunteer else "",
            "+" if has_master_degree(student) else "",
            student.email,
            student.phone,
            student.university,
            student.get_uni_year_at_enrollment_display(),
            student.enrollment_year,
            student.curriculum_year,
            graduation_year,
            student.yandex_login,
            " и ".join(s.name for s in disciplines),
            student.get_status_display(),
            '',  # FIXME: error in student.status_changed_at field
            student.comment,
            student.comment_changed_at.strftime(dt_format),
            student.workplace,
            student.get_absolute_url(),
            self.links_to_application_forms(student),
            total_success_passed,
            *self._export_courses(student),
            *self._export_projects(student),
            *self._export_shad_courses(student),
            *self._export_online_courses(student),
        ]

    def get_filename(self):
        today = formats.date_format(datetime.now(), "SHORT_DATE_FORMAT")
        return f"sheet_{today}"


class ProgressReportForSemester(ProgressReport):
    """
    Input data must contain all student enrollments until target
    semester (inclusive), even without grades.
    Exported data contains club and center courses if target term already
    passed and additionally shad- and online-courses if target term is current.
    """

    UNSUCCESSFUL_GRADES = [GradeTypes.NOT_GRADED, GradeTypes.UNSATISFACTORY]

    def __init__(self, term):
        self.target_semester = term
        super().__init__(grade_getter="grade_honest")

    def get_queryset(self):
        return (User.objects
                .has_role(Roles.STUDENT, Roles.VOLUNTEER)
                .select_related('branch')
                .student_progress(before_term=self.target_semester)
                .exclude(status=StudentStatuses.EXPELLED))

    def before_process_row(self, student):
        student.enrollments_eq_target_semester = 0
        # During one term student can't enroll on 1 course twice, but for
        # previous terms we should consider this situation and count only
        # unique course ids
        student.success_eq_target_semester = 0
        student.success_lt_target_semester = set()
        # Shad courses specific attributes
        student.shad_eq_target_semester = 0
        student.success_shad_eq_target_semester = 0
        student.success_shad_lt_target_semester = 0

    def after_process_row(self, student):
        """
        Convert `success_lt_target_semester` to int repr.
        Collect statistics for shad courses.
        """
        student.success_lt_target_semester = len(student.success_lt_target_semester)
        if not student.shads:
            return
        shads = []
        # During one term student can't enroll on 1 course twice, for
        # previous terms we assume they can't do that.
        for shad in student.shads:
            if shad.semester == self.target_semester:
                student.shad_eq_target_semester += 1
                if shad.grade not in self.UNSUCCESSFUL_GRADES:
                    student.success_shad_eq_target_semester += 1
                # Show shad enrollments for target term only
                shads.append(shad)
            elif shad.grade not in self.UNSUCCESSFUL_GRADES:
                student.success_shad_lt_target_semester += 1
        student.shads = shads

    def skip_enrollment(self, enrollment: Enrollment, student):
        """
        Count stats for enrollments from passed terms and skip them.
        """
        if enrollment.course.semester_id == self.target_semester.pk:
            student.enrollments_eq_target_semester += 1
            if enrollment.grade not in self.UNSUCCESSFUL_GRADES:
                student.success_eq_target_semester += 1
        else:
            if enrollment.grade not in self.UNSUCCESSFUL_GRADES:
                student.success_lt_target_semester.add(
                    enrollment.course.meta_course_id
                )
            # Show enrollments for target term only
            return True
        return False

    def get_courses_headers(self, courses_headers):
        if not courses_headers:
            return []
        return [f"{course_name}, оценка" for course_name in
                courses_headers.values()]

    def _generate_headers(self):
        return [
            'ID',
            'Фамилия',
            'Имя',
            'Отчество',
            'Отделение',
            'Вольнослушатель',
            'Магистратура',
            'Почта',
            'Телефон',
            'ВУЗ',
            'Курс (на момент поступления)',
            'Год поступления',
            'Год программы обучения',
            'Год выпуска',
            'Яндекс ID',
            'Направления обучения',
            'Статус',
            'Дата статуса или итога (изменения)',
            'Комментарий',
            'Дата последнего изменения комментария',
            'Работа',
            'Ссылка на профиль',
            'Успешно сдано (Центр/Клуб/ШАД/Онлайн) до семестра "%s"' % self.target_semester,
            'Успешно сдано (Центр/Клуб/ШАД) за семестр "%s"' % self.target_semester,
            'Записей на курсы (Центр/Клуб/ШАД) за семестр "%s"' % self.target_semester,
            *self.get_courses_headers(self._all_courses),
            *self.generate_shad_courses_headers(self._shads_max),
            *self.generate_online_courses_headers(self._online_max),
        ]

    def _export_courses(self, student) -> List[str]:
        values = [''] * len(self._all_courses)
        for i, meta_course_id in enumerate(self._all_courses):
            if meta_course_id in student.unique_enrollments:
                enrollment = student.unique_enrollments[meta_course_id]
                values[i] = self.grade_getter(enrollment).lower()
        return values

    def _export_row(self, student):
        success_total_lt_target_semester = (
            student.success_lt_target_semester +
            student.success_shad_lt_target_semester +
            len(student.online_courses))
        success_total_eq_target_semester = (
            student.success_eq_target_semester +
            student.success_shad_eq_target_semester)
        enrollments_eq_target_semester = (
            student.enrollments_eq_target_semester +
            student.shad_eq_target_semester
        )
        dt_format = f"{TIME_FORMAT_RU} {DATE_FORMAT_RU}"
        if hasattr(student, "graduate_profile"):
            disciplines = student.graduate_profile.academic_disciplines.all()
            graduation_year = student.graduate_profile.graduation_year
        else:
            disciplines = []
            graduation_year = ""
        return [
            student.pk,
            student.last_name,
            student.first_name,
            student.patronymic,
            student.branch,
            "+" if student.is_volunteer else "",
            "+" if has_master_degree(student) else "",
            student.email,
            student.phone,
            student.university,
            student.get_uni_year_at_enrollment_display(),
            student.enrollment_year,
            student.curriculum_year,
            graduation_year,
            student.yandex_login,
            " и ".join(s.name for s in disciplines),
            student.get_status_display(),
            '',  # FIXME: error with student.status_changed_at
            student.comment,
            student.comment_changed_at.strftime(dt_format),
            student.workplace,
            student.get_absolute_url(),
            success_total_lt_target_semester,
            success_total_eq_target_semester,
            enrollments_eq_target_semester,
            *self._export_courses(student),
            *self._export_shad_courses(student),
            *self._export_online_courses(student),
        ]

    def get_filename(self):
        return "sheet_{}_{}".format(self.target_semester.year,
                                    self.target_semester.type)


class ProgressReportForInvitation(ProgressReportForSemester):
    def __init__(self, invitation):
        self.invitation = invitation
        term = invitation.courses.first().semester
        super().__init__(term)

    def get_queryset(self):
        invited_students = (Enrollment.objects
                            .filter(invitation_id=self.invitation.pk)
                            .values('student_id'))
        return (User.objects
                .has_role(Roles.INVITED)
                .select_related('branch')
                .student_progress(before_term=self.target_semester)
                .filter(pk__in=invited_students)
                .exclude(status=StudentStatuses.EXPELLED))


class WillGraduateStatsReport(ReportFileOutput):
    """Unoptimized piece of code"""

    def __init__(self):
        self.headers = [
            "Город",
            "ФИО",
            "1. У кого сколько оставлено комментариев на сайте с 23:00 до 8:00 по мск (задания + проекты, входит отправка заданий)",
            "2. У кого сколько вообще комментариев на сайте центра (задания + проекты, входит отправка заданий)",
            "3. Процентное соотношение (курсы с оценкой зачёт и выше) / (все взятые курсы)",
            "4.1 Максимальное количество сданных курсов + практик за один семестр",
            "4.2 Какой именно это семестр",
            "5. Сколько проектов сдано осенью? ",
            "6. Сколько проектов сдано весной?",
            "7. Сдано курсов всего (ШАД/Клуб/Центр/Онлайн)",
            "8. Не сдал курсов всего (ШАД/Клуб/Центр/Онлайн)",
        ]

        self.data = []
        students = self.get_queryset()
        current_semester = Semester.get_current()
        for student in students.all():
            stats = student.stats(current_semester)
            # 1. Оставлено комментариев на сайте с 23:00 до 8:00 по мск
            time_range_in_utc = Q(created__hour__gte=20) | Q(created__hour__lte=5)
            assignment_comments_after_23 = (
                AssignmentComment.objects
                .filter(student_assignment__student_id=student.pk)
                .filter(time_range_in_utc)
                .count())
            report_comments_after_23 = (
                ReportComment.objects
                .filter(author_id=student.pk)
                .filter(time_range_in_utc)
                .count())
            comments_after_23_total = report_comments_after_23 + assignment_comments_after_23
            # 2. Сколько вообще комментариев на сайте центра
            assignment_comments_count = (
                AssignmentComment.objects
                .filter(student_assignment__student_id=student.pk)
                .count())
            report_comments_count = (
                ReportComment.objects
                .filter(author_id=student.pk)
                .count())
            comments_total = assignment_comments_count + report_comments_count
            # 3. (курсы с оценкой зачёт и выше) / (все взятые курсы)
            enrollments_qs = student.enrollment_set.filter(is_deleted=False)
            all_enrollments_count = (enrollments_qs.count() +
                                     student.onlinecourserecord_set.count() +
                                     student.shadcourserecord_set.count())
            passed = (stats["passed"]["total"]) / all_enrollments_count
            # 4. Максимальное количество сданных курсов + практик за один
            # семестр, какой именно это семестр
            # Collect all unique terms among practices, center, shad and
            # club courses
            all_enrollments_terms = enrollments_qs.values_list(
                "course__semester_id",
                flat=True)
            semesters = {v for v in all_enrollments_terms}
            all_shad_terms = (SHADCourseRecord.objects
                              .filter(student_id=student.pk)
                              .values_list("semester_id", flat=True))
            unique_shad_terms = {v for v in all_shad_terms}
            all_projects_terms = (ProjectStudent.objects
                                  .filter(student_id=student.pk)
                                  .values_list("project__semester_id",
                                               flat=True))
            project_semesters = {v for v in all_projects_terms}
            semesters = semesters.union(unique_shad_terms, project_semesters)
            max_in_term = 0
            max_in_term_semester_id = 0
            for semester_id in semesters:
                enrollments_in_term_qs = enrollments_qs.filter(
                    course__semester_id=semester_id).all()
                in_term = sum(int(e.grade in GradeTypes.satisfactory_grades) for e in
                              enrollments_in_term_qs)
                projects_in_term_qs = ProjectStudent.objects.filter(
                    project__semester_id=semester_id,
                    student_id=student.pk).all()
                in_term += sum(int(p.final_grade in GradeTypes.satisfactory_grades) for p in
                               projects_in_term_qs)
                shad_courses_in_term_qs = SHADCourseRecord.objects.filter(
                    student_id=student.pk, semester_id=semester_id).all()
                in_term += sum(int(c.grade in GradeTypes.satisfactory_grades) for c in
                               shad_courses_in_term_qs)
                if in_term > max_in_term:
                    max_in_term = in_term
                    max_in_term_semester_id = semester_id
            # 6. Сколько проектов сдано осенью?
            projects_qs = ProjectStudent.objects.filter(
                project__semester__type="autumn", student_id=student.pk).all()
            projects_in_autumn = sum(
                int(p.final_grade in GradeTypes.satisfactory_grades) for p in projects_qs)
            # 7. Сколько проектов сдано весной?
            projects_qs = ProjectStudent.objects.filter(
                project__semester__type="spring", student_id=student.pk).all()
            projects_in_spring = sum(
                int(p.final_grade in GradeTypes.satisfactory_grades) for p in projects_qs)
            row = [
                student.branch.name,
                student.get_abbreviated_short_name(),
                comments_after_23_total,
                comments_total,
                "%.2f" % (passed * 100),
                max_in_term,
                Semester.objects.get(pk=max_in_term_semester_id),
                projects_in_autumn,
                projects_in_spring,
                stats["passed"]["total"],
                stats["failed"]["total"],
            ]
            self.data.append(row)

    def get_queryset(self):
        enrollments_queryset = (
            Enrollment.active
            .select_related(
                'course',
                'course__semester',
                'course__meta_course',)
            .annotate(classes_total=Count('course__courseclass'))
            .order_by('student', 'course_id'))
        shad_courses_queryset = (SHADCourseRecord.objects
                                 .select_related("semester"))
        prefetch_list = [
            Prefetch('enrollment_set', queryset=enrollments_queryset),
            Prefetch('shadcourserecord_set', queryset=shad_courses_queryset),
            'onlinecourserecord_set',
        ]
        qs = (User.objects
              .filter(status=StudentStatuses.WILL_GRADUATE)
              .select_related('branch')
              .prefetch_related(*prefetch_list))
        return qs

    def export_row(self, row):
        return row

    def get_filename(self):
        today = datetime.now()
        return "will_graduate_report_{}".format(
            formats.date_format(today, "SHORT_DATE_FORMAT"))