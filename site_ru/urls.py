from django.urls import include, path

from application.views import ApplicationFormView
from site_ru.apps.application.api.views import (
    ApplicationFormCreateTaskView, ApplicantCreateFromYDSFormAPIView
)
from lms.urls import urlpatterns

urlpatterns += [
    path('admission/applications/', ApplicationFormCreateTaskView.as_view(), name='admission_application_form_new_task'),
    path('applicant_create', ApplicantCreateFromYDSFormAPIView.as_view(), name='applicant_create'),
    path('admission2024', ApplicationFormView.as_view(), name='application_form'),
    path('', include('admission.urls_appointment')),
]
