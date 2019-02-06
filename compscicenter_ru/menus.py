from django.conf import settings
from django.utils.translation import pgettext_lazy
from menu import Menu

from core.menu import MenuItem
from core.urls import reverse

PRIVATE = settings.LMS_SUBDOMAIN

public_menu = [
    MenuItem(
        pgettext_lazy("menu", "О центре"),
        # FIXME: что делать с такими штуками?
        '/about/',
        weight=10,
        children=[
            MenuItem(pgettext_lazy("menu", "Цели и история"), '/about/', weight=20),
            MenuItem(pgettext_lazy("menu", "Программа"), reverse('syllabus'), weight=30),
            MenuItem(pgettext_lazy("menu", "Команда"), reverse('orgs'), weight=40),
            MenuItem(pgettext_lazy("menu", "Преподаватели"), reverse('teachers'), weight=50),
            MenuItem(pgettext_lazy("menu", "Выпускники"), reverse('alumni'), weight=60, selected_patterns=[r"^/2016/$"]),
            MenuItem(pgettext_lazy("menu", "Отзывы"), reverse('testimonials'), weight=70),
        ],
        selected_patterns=[
            r"^/events/"
        ]),
    MenuItem(
        pgettext_lazy("menu", "Курсы"),
        '/courses/',
        weight=20,
        excluded_patterns=[
            r"^/courses/.*/assignments/add$",
            r"^/courses/.*/assignments/\d+/edit$"
        ]),
    MenuItem(pgettext_lazy("menu", "Онлайн"), '/online/', weight=30, children=[
        MenuItem(pgettext_lazy("menu", "Онлайн-курсы"), '/online/', weight=10),
        MenuItem(pgettext_lazy("menu", "Онлайн-программы"), 'https://code.stepik.org/', weight=20, is_external=True),
        MenuItem(pgettext_lazy("menu", "Видео"), '/videos/', weight=30),
    ]),
    MenuItem(pgettext_lazy("menu", "Лекторий"), 'https://open.compscicenter.ru/', weight=40, is_external=True),
    MenuItem(pgettext_lazy("menu", "Поступление"), '/enrollment/', weight=50, children=[
        MenuItem(pgettext_lazy("menu", "Поступающим"), '/enrollment/', weight=10),
        MenuItem(pgettext_lazy("menu", "Подать заявку"), '/application/closed/', weight=20),
        MenuItem(pgettext_lazy("menu", "Программа для поступления"), '/enrollment/program/', weight=30),
        MenuItem(pgettext_lazy("menu", "Вопросы и ответы"), '/faq/', weight=40),
    ]),
]

common_menu = [menu_item for menu_item in public_menu if menu_item.weight < 50]
for item in common_menu:
    # This is OK that we mutate `public_menu`
    item.weight -= 500

for item in public_menu:
    Menu.add_item("menu_public", item)