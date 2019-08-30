from django.utils.translation import pgettext_lazy
from menu import Menu

from core.menu import MenuItem
from core.urls import reverse, reverse_lazy

compsciclub_ru_menu = [
    MenuItem(
        "О клубе",
        "/about/",
        weight=10
    ),
    MenuItem(
        "Расписание",
        "/schedule/",
        weight=20
    ),
    MenuItem(
        "Курсы",
        reverse_lazy('course_list'),
        weight=30
    ),
    MenuItem(
        "Преподаватели",
        reverse_lazy('teachers'),
        weight=40
    ),
    MenuItem(
        "Международные школы",
        "/schools/",
        weight=50
    ),
    MenuItem(
        pgettext_lazy("menu", "Обучение"),
        reverse_lazy('study:assignment_list'),
        weight=60,
        children=[
            MenuItem(pgettext_lazy("menu", "Задания"), '/learning/assignments/', weight=10, budge='assignments_student'),
            MenuItem(pgettext_lazy("menu", "Моё расписание"), '/learning/timetable/', weight=20, selected_patterns=[r"^/learning/calendar/"]),
            MenuItem(pgettext_lazy("menu", "Календарь"), '/learning/full-calendar/', weight=30),
            MenuItem(pgettext_lazy("menu", "Мои курсы"), '/learning/courses/', weight=40),
        ],
        permissions=(
            "learning.view_study_menu",
        ),
        css_classes='for-students'
    ),
    MenuItem(
        pgettext_lazy("menu", "Преподавание"),
        reverse_lazy('teaching:assignment_list'),
        weight=60,
        children=[
            MenuItem(
                pgettext_lazy("menu", "Задания"),
                reverse_lazy('teaching:assignment_list'),
                weight=10,
                budge='assignments_teacher',
                selected_patterns=[
                    r"^/courses/.*/assignments/add$",
                    r"^/courses/.*/assignments/\d+/edit$"
                ]),
            MenuItem(
                pgettext_lazy("menu", "Расписание"),
                reverse_lazy('teaching:timetable'),
                weight=20,
                selected_patterns=[r"^/teaching/calendar/"]),
            MenuItem(
                pgettext_lazy("menu", "Календарь"),
                reverse_lazy('teaching:calendar_full'),
                weight=30),
            MenuItem(
                pgettext_lazy("menu", "Мои курсы"),
                reverse_lazy("teaching:course_list"),
                weight=40,
                budge='courseoffering_news'),
            MenuItem(
                pgettext_lazy("menu", "Ведомости"),
                reverse_lazy('teaching:gradebook_list'),
                weight=50),
        ],
        permissions=(
            "learning.view_teaching_menu",
        ),
        css_classes='for-teachers'
    ),
]

compsciclub_en_menu = [
    MenuItem(
        "About CS Club",
        "/en/about/",
        weight=10
    ),
    MenuItem(
        "Courses",
        reverse_lazy('course_list'),
        weight=20
    ),
    MenuItem(
        "Lecturers",
        reverse_lazy('teachers'),
        weight=30
    ),
    MenuItem(
        "Schools",
        "/en/schools/",
        weight=40
    ),
]

for item in compsciclub_ru_menu:
    Menu.add_item("compsciclub_ru", item)

for item in compsciclub_en_menu:
    Menu.add_item("compsciclub_en", item)