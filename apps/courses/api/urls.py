from django.conf.urls import url

from . import views as v

urlpatterns = [
    url(r'^courses/$', v.CourseList.as_view(), name='courses'),
    url(r'^teachers/$', v.TeacherList.as_view(), name='teachers'),
]