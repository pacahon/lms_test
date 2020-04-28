from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.core.exceptions import ValidationError
from django.db import models as db_models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportMixin

from core.admin import meta
from core.filters import AdminRelatedDropdownFilter
from core.widgets import AdminRichTextAreaWidget
from users.constants import Roles
from users.forms import UserCreationForm, UserChangeForm
from .import_export import UserRecordResource
from .models import User, EnrollmentCertificate, \
    OnlineCourseRecord, SHADCourseRecord, UserStatusLog, UserGroup


class UserStatusLogAdmin(admin.TabularInline):
    list_select_related = ['student']
    model = UserStatusLog
    extra = 0
    show_change_link = True
    readonly_fields = ('get_semester', 'status')

    def has_add_permission(self, request, obj=None):
        return False

    @meta(_("Semester"))
    def get_semester(self, obj):
        from courses.utils import get_terms_in_range
        term = next(get_terms_in_range(obj.created, obj.created), None)
        return term.label if term else '-'


class OnlineCourseRecordAdmin(admin.StackedInline):
    model = OnlineCourseRecord
    extra = 0


class SHADCourseRecordInlineAdmin(admin.StackedInline):
    model = SHADCourseRecord
    extra = 0


class UserGroupForm(forms.ModelForm):
    """Form for adding new Course Access Roles view the Django Admin Panel."""

    class Meta:
        model = UserGroup
        fields = '__all__'

    # ACCESS_ROLES = [(role_name, _(cls.verbose_name)) for role_name, cls
    #                 in REGISTERED_ACCESS_ROLES.items()]
    # FIXME: Use registred roles
    ACCESS_ROLES = Roles.choices
    role = forms.ChoiceField(choices=ACCESS_ROLES)

    def clean(self):
        cleaned_data = super().clean()
        role = int(cleaned_data['role'])
        user = cleaned_data['user']
        if role == Roles.STUDENT:
            if user.enrollment_year is None:
                msg = _("Enrollment year should be provided for students")
                self.add_error(None, ValidationError(msg))
        if role == Roles.VOLUNTEER:
            if user.enrollment_year is None:
                msg = _("CSCUser|enrollment year should be provided for "
                        "volunteers")
                self.add_error(None, ValidationError(msg))


class UserGroupInlineAdmin(admin.TabularInline):
    form = UserGroupForm
    model = UserGroup
    extra = 0
    # XXX: fieldset name should be unique and not None
    insert_after_fieldset = _('Permissions')


class UserAdmin(_UserAdmin):
    add_form = UserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2',
                       'gender', 'branch'),
        }),
    )
    form = UserChangeForm
    change_form_template = 'admin/user_change_form.html'
    ordering = ['last_name', 'first_name']
    inlines = [OnlineCourseRecordAdmin, SHADCourseRecordInlineAdmin,
               UserStatusLogAdmin, UserGroupInlineAdmin]
    readonly_fields = ['comment_changed_at', 'comment_last_author',
                       'last_login', 'date_joined']
    list_display = ['id', 'username', 'email', 'first_name', 'last_name',
                    'is_staff']
    list_filter = ['is_active', 'branch', 'group__site', 'group__role',
                   'is_staff', 'is_superuser']
    filter_horizontal = []

    formfield_overrides = {
        db_models.TextField: {'widget': AdminRichTextAreaWidget},
    }

    fieldsets = [
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {
            'fields': ['gender', 'branch',
                       'last_name', 'first_name', 'patronymic', 'phone',
                       'workplace', 'photo', 'bio', 'private_contacts', 'social_networks']}),
        (_('Permissions'), {'fields': ['is_active', 'is_staff', 'is_superuser',
                                       ]}),
        (_('External services'), {'fields': ['yandex_login', 'stepic_id',
                                             'github_login', 'anytask_url']}),
        (_('Student info record'),
         {'fields': ['status', 'enrollment_year', 'curriculum_year',
                     'university', 'uni_year_at_enrollment',
                     'official_student', 'diploma_number',
                     'academic_disciplines']}),
        (_("Curator's note"),
         {'fields': ['comment', 'comment_changed_at', 'comment_last_author']}),
        (_('Important dates'), {'fields': ['last_login', 'date_joined']})]

    def get_formsets_with_inlines(self, request, obj=None):
        """
        Yield formsets and the corresponding inlines.
        """
        if obj is None:
            return None
        for inline in self.get_inline_instances(request, obj):
            yield inline.get_formset(request, obj), inline

    def save_model(self, request, obj, form, change):
        if "comment" in form.changed_data:
            obj.comment_last_author = request.user
        super().save_model(request, obj, form, change)


class SHADCourseRecordAdmin(admin.ModelAdmin):
    list_display = ["name", "student", "grade"]
    list_filter = [
        "student__branch",
        ("semester", AdminRelatedDropdownFilter)
    ]
    raw_id_fields = ('student',)

    def get_readonly_fields(self, request, obj=None):
        return ('anytask_url',) if obj else []

    @meta(_("Anytask"))
    def anytask_url(self, obj):
        if obj.student_id and obj.student.anytask_url:
            url = obj.student.anytask_url
            return mark_safe(f"<a target='_blank' href='{url}'>Открыть профиль в новом окне</a>")
        return "-"


class UserRecordResourceAdmin(ImportMixin, UserAdmin):
    resource_class = UserRecordResource
    import_template_name = 'admin/import_export/import_users.html'


class EnrollmentCertificateAdmin(admin.ModelAdmin):
    list_display = ["student", "created"]
    raw_id_fields = ["student"]


admin.site.register(User, UserRecordResourceAdmin)
admin.site.register(EnrollmentCertificate, EnrollmentCertificateAdmin)
admin.site.register(SHADCourseRecord, SHADCourseRecordAdmin)
