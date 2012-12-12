__author__ = 'vutran'

from django.conf.urls import patterns, url
from views import ApiLogin, ApiLogout, Attendance, SchoolSetting, ApiGetStudentList
from views import SmsStatus, SmsSummary, hanhkiem, StudentProfile,\
        MarkForASubject, MarkForAStudent, Schedule, FailedSms
from views import GetListTerm, GetAttendanceForStudent, GetSubjectOfHomeroomTeacher

urlpatterns = patterns('',
    url(r'login/$', ApiLogin.as_view(), name='api_login'),
    url(r'logout/$', ApiLogout.as_view(), name='api_logout'),
    url(r'getStudentList/(?P<class_id>\d+)/$', ApiGetStudentList.as_view(),
        name='api_get_student_list'),
    url(r'attendance/$', Attendance.as_view(), name='api_post_attendance'),
    url(r'attendance/(?P<class_id>\d+)/(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)/$',
        Attendance.as_view(), name='api_get_attendance'),
    url(r'setting/$', SchoolSetting.as_view(), name='api_setting'),
    url(r'sms/(?P<ids>\w+)/$', SmsStatus.as_view(), name='api_sms'),
    url(r'failed-sms/(?P<from_date>\d{2}-\d{2}-\d{4})/$',
        FailedSms.as_view(), name='failed_sms'),
    url(r'sms_summary/(?P<class_id>\d+)/$', SmsSummary.as_view(),
        name='api_sms_summary'),
    url(r'hanhkiem/$', hanhkiem.as_view(), name='api_post_hanhkiem'),
    url(r'hanhkiem/(?P<class_id>\d+)/$',
        hanhkiem.as_view(), name='api_get_hanhkiem'),
    url(r'schedule/$', Schedule.as_view(), name='api_get_schedule'),
    url(r'profile/(?P<student_id>\d+)/$', StudentProfile.as_view(),
        name='api_get_student_profile'),

    url(r'markForASubject/$', MarkForASubject.as_view(),
        name='api_post_mark_for_a_subject'),
    url(r'markForASubject/(?P<subject_id>\d+)/(?P<term_number>\w+)$',
        MarkForASubject.as_view(), name='api_get_mark_for_a_subject'),
    url(r'markForASubject/(?P<subject_id>\d+)$',
        MarkForASubject.as_view(), name='api_get_mark_for_a_subject'),

    url(r'markForAStudent/(?P<student_id>\d+)/(?P<term_id>\d+)$',
        MarkForAStudent.as_view(), name='api_get_mark_for_a_student'),
    url(r'markForAStudent/(?P<student_id>\d+)$',
        MarkForAStudent.as_view(), name='api_get_mark_for_a_student'),
    url(r'getListTerm$', GetListTerm.as_view(), name='api_get_list_term'),
    url(
        r'getAttendanceForStudent/(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)/(?P<day1>\d+)/(?P<month1>\d+)/(?P<year1>\d+)$'
        , GetAttendanceForStudent.as_view(), name='api_get_attendance_for_student'),
    url(r'getAttendanceForStudent/(?P<all>[\w\-]*)$'
        , GetAttendanceForStudent.as_view(), name='api_get_attendance_for_student'),

    url(r'getSubjectOfHomeroomTeacher$'
        , GetSubjectOfHomeroomTeacher.as_view(), name='api_get_subject_homeroom_teacher'),
)
