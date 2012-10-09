__author__ = 'vutran'

from django.conf.urls import patterns, url
from views import ApiLogin, ApiLogout, Attendance, SchoolSetting, ApiGetStudentList
from views import SmsStatus, SmsSummary, hanhkiem, Schedule

urlpatterns = patterns('',
    url(r'login/$', ApiLogin.as_view(), name='api_login'),
    url(r'logout/$', ApiLogout.as_view(), name='api_logout'),
    url(r'getStudentList/(?P<class_id>\w+)/$', ApiGetStudentList.as_view(),
        name='api_get_student_list'),
    url(r'attendance/$', Attendance.as_view(), name='api_post_attendance'),
    url(r'attendance/(?P<class_id>\w+)/(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)/$',
        Attendance.as_view(), name='api_get_attendance'),
    url(r'setting/$', SchoolSetting.as_view(), name='api_setting'),
    url(r'sms/(?P<ids>\w+)/$', SmsStatus.as_view(), name='api_sms'),
    url(r'sms_summary/(?P<class_id>\w+)/$', SmsSummary.as_view(),
        name='api_sms_summary'),
    url(r'hanhkiem/$', hanhkiem.as_view(), name='api_post_hanhkiem'),
    url(r'hanhkiem/(?P<class_id>\w+)/$',
        hanhkiem.as_view(), name='api_get_hanhkiem'),
    url(r'schedule/$', Schedule.as_view(), name='api_get_schedule'),

)
