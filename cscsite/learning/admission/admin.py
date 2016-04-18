from __future__ import unicode_literals, absolute_import

import simplejson
from django.contrib import admin
from django.forms import TextInput
from django.utils.encoding import smart_text
from import_export.admin import ExportActionModelAdmin, ExportMixin
from jsonfield.fields import JSONField

from learning.admission.import_export import ApplicantRecordResource, \
    OnlineTestRecordResource, ExamRecordResource
from learning.admission.models import Campaign, Interview, Applicant, Test, Exam, \
    Interviewer, Comment


class OnlineTestAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = OnlineTestRecordResource
    list_display = ['__str__', 'score']
    list_filter = ['applicant__campaign']
    search_fields = ['applicant__yandex_id', 'applicant__second_name', 'applicant__first_name']

    def get_queryset(self, request):
        qs = super(OnlineTestAdmin, self).get_queryset(request)
        return qs.select_related('applicant')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'applicant':
            kwargs['queryset'] = (Applicant.objects.select_related("campaign", ).order_by("second_name"))
        return (super(OnlineTestAdmin, self)
                .formfield_for_foreignkey(db_field, request, **kwargs))


class ExamAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ExamRecordResource
    list_display = ['__str__', 'score']

    def get_queryset(self, request):
        qs = super(ExamAdmin, self).get_queryset(request)
        return qs.select_related('applicant')


class ApplicantRecordResourceAdmin(ExportActionModelAdmin):
    resource_class = ApplicantRecordResource
    list_display = ['id', 'yandex_id', 'second_name', 'first_name', 'last_name', 'campaign']
    list_filter = ['campaign',]
    search_fields = ['yandex_id', 'stepic_id', 'first_name', 'second_name', 'email']

class InterviewerAdmin(admin.ModelAdmin):
    list_display = ['user', 'campaign']
    list_filter = ['campaign']


class InterviewAdmin(admin.ModelAdmin):
    list_display = ['date', 'applicant']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'applicant':
            kwargs['queryset'] = (Applicant.objects.select_related("campaign",))
        return (super(InterviewAdmin, self)
                .formfield_for_foreignkey(db_field, request, **kwargs))



admin.site.register(Campaign)
admin.site.register(Applicant, ApplicantRecordResourceAdmin)
admin.site.register(Test, OnlineTestAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Interviewer, InterviewerAdmin)
admin.site.register(Interview, InterviewAdmin)
admin.site.register(Comment)
