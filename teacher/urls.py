from django.conf.urls import patterns, url
from teacher.views import IndexView, ClassView, StudentView, MarkView

urlpatterns = patterns('',
        url(r'^$', IndexView.as_view(), name='teacher_index'),
        url(r'class/(?P<request_type>create)$',
            ClassView.as_view(), name='class_create'),
        url(r'class/(?P<class_id>\d+)/(?P<request_type>modify|remove|view)$',
            ClassView.as_view(), name='class_view'),
        url(r'class/(?P<class_id>\d+?)/student/(?P<request_type>create)$',
            StudentView.as_view(), name='student_create'),
        url(r'class/(?P<class_id>\d+?)/student/(?P<student_id>\d+)/(?P<request_type>modify|remove|view)$',
            StudentView.as_view(), name='student_view'),
        url(r'class/(?P<class_id>\d+?)/student/(?P<student_id>\d+)/mark/(?P<request_type>create)$',
            MarkView.as_view(), name='mark_create'),
        url(r'class/(?P<class_id>\d+?)/student/(?P<student_id>\d+)/mark/(?P<mark_id>\d+)/(?P<request_type>modify|remove)$',
            MarkView.as_view(), name='mark_view'),
)
