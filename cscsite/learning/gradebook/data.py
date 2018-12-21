from collections import OrderedDict

import numpy as np
from django.utils.translation import ugettext_lazy as _

from courses.models import Course, Assignment
from learning.models import StudentAssignment, Enrollment
from learning.settings import GradeTypes


__all__ = ('StudentMeta', 'StudentProgress', 'GradeBookData', 'gradebook_data')


class StudentMeta:
    def __init__(self, enrollment: Enrollment, index: int):
        self._enrollment = enrollment
        # Will be filled later based on assignments data
        self.total_score = None
        self.index = index

    @property
    def id(self):
        return self._enrollment.student_id

    @property
    def enrollment_id(self):
        return self._enrollment.pk

    @property
    def final_grade(self):
        return self._enrollment.grade

    @property
    def first_name(self):
        return self._enrollment.student.first_name

    @property
    def last_name(self):
        return self._enrollment.student.last_name

    @property
    def patronymic(self):
        return self._enrollment.student.patronymic

    @property
    def username(self):
        return self._enrollment.student.username

    @property
    def yandex_id(self):
        return self._enrollment.student.yandex_id

    def get_absolute_url(self):
        return self._enrollment.student.get_absolute_url()

    def get_abbreviated_name(self):
        return self._enrollment.student.get_abbreviated_name()

    def get_abbreviated_short_name(self):
        return self._enrollment.student.get_abbreviated_short_name()

    @property
    def final_grade_display(self):
        return GradeTypes.values[self.final_grade]


class StudentProgress:
    def __init__(self, student_assignment: StudentAssignment,
                 assignment: Assignment):
        student_assignment.assignment = assignment
        self._student_assignment = student_assignment

    @property
    def id(self):
        return self._student_assignment.id

    @property
    def score(self):
        return self._student_assignment.score

    @property
    def assignment_id(self):
        return self._student_assignment.assignment_id

    @property
    def assignment(self):
        return self._student_assignment.assignment

    @property
    def student_id(self):
        return self._student_assignment.student_id

    def get_state(self):
        return self._student_assignment.state_short


class GradeBookData:
    # Magic "100" constant - width of assignment column
    ASSIGNMENT_COLUMN_WIDTH = 100

    def __init__(self, course: Course, students, assignments, submissions):
        """
        X-axis of submissions ndarray is students data.
        We make some assertions on that, but still can fail in case
        of NxN array.
        """
        self.course = course
        assert submissions.shape == (len(students), len(assignments))
        self.students = students
        self.assignments = assignments
        self.submissions = submissions

    def get_table_width(self):
        # First 3 columns in gradebook table, see `pages/_gradebook.scss`
        magic = 150 + 140 + 66
        return len(self.assignments) * self.ASSIGNMENT_COLUMN_WIDTH + magic

    # TODO: add link to assignment and reuse in template
    def get_headers(self):
        static_headers = [
            _("Last name"),
            _("First name"),
            _("Final grade"),
            _("Total")
        ]
        return static_headers + [a.title for a in self.assignments.values()]


def gradebook_data(course: Course) -> GradeBookData:
    """
    Returns:
        students = OrderedDict(
            1: StudentMeta(
                "pk": 1,
                "full_name": "serg",
                "final_grade": good,
                "total_score": 23,
                "enrollment_id": 1,
            ),
            ...
        ),
        assignments = OrderedDict(
            1: {
                "pk": 1,
                "title": "HW#1",
                "is_online": True,
                "passing_score": 0,
                "maximum_score": 10
            },
            ...
        ),
        submissions = [
            [
                    {
                        "id" : 1,  # student_assignment_id
                        "score": 5
                    },
                    {
                        "id" : 3,
                        "score": 2
                    },
                    None  # if student left the course or was expelled
                          # and has no record for grading
            ],
            [ ... ]
        ]
    """
    enrolled_students = OrderedDict()
    _enrollments_qs = (Enrollment.active
                       .filter(course=course)
                       .select_related("student")
                       .order_by("student__last_name", "student_id"))
    for index, e in enumerate(_enrollments_qs.iterator()):
        enrolled_students[e.student_id] = StudentMeta(e, index)

    assignments = OrderedDict()
    assignments_id_to_index = {}
    _assignments_qs = (Assignment.objects
                       .filter(course_id=course.pk)
                       .only("pk",
                             "title",
                             # Assignment constructor caches course id
                             "course_id",
                             "is_online",
                             "maximum_score",
                             "passing_score")
                       .order_by("deadline_at", "pk"))
    for index, a in enumerate(_assignments_qs.iterator()):
        assignments[a.pk] = a
        assignments_id_to_index[a.pk] = index
    submissions = np.empty((len(enrolled_students), len(assignments)),
                           dtype=object)
    _student_assignments_qs = (
        StudentAssignment.objects
        .filter(assignment__course_id=course.pk)
        .only("pk",
              "score",
              "first_student_comment_at",  # needs to calculate progress status
              "assignment_id",
              "student_id")
        .order_by("student_id", "assignment_id"))
    for sa in _student_assignments_qs.iterator():
        student_id = sa.student_id
        if student_id not in enrolled_students:
            continue
        student_index = enrolled_students[student_id].index
        assignment_index = assignments_id_to_index[sa.assignment_id]
        submissions[student_index][assignment_index] = StudentProgress(
            sa, assignments[sa.assignment_id])
    for student_id in enrolled_students:
        student_index = enrolled_students[student_id].index
        total_score = sum(s.score for s in submissions[student_index]
                          if s is not None and s.score is not None)
        setattr(enrolled_students[student_id], "total_score", total_score)

    return GradeBookData(course=course,
                         students=enrolled_students,
                         assignments=assignments,
                         submissions=submissions)
