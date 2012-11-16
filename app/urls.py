from django.conf.urls import patterns, url
from app.views import feedback, system_subject_agenda, profile_detail, create_profile
from school.excel_interaction import import_system_agenda, export_system_agenda

urlpatterns = patterns('',
     url(r'feedback/$', feedback, name = "feedback"),
     url(r'manage_agenda/(?P<subject>\w+)/(?P<grade>\w+)/(?P<term>\w+)$', system_subject_agenda, name="system_subject_agenda"),
     url(r'manage_agenda/$', system_subject_agenda, name="system_subject_agenda"),
     url(r'import/systemAgenda/(?P<subject>\w+)/(?P<grade>\w+)/(?P<term>\w+)$', import_system_agenda, name="import_system_agenda"),
     url(r'export_system_agenda/(?P<subject>\w+)/(?P<grade>\w+)/(?P<term>\w+)$', export_system_agenda, name="export_system_agenda"),
     url(r'^(?P<username>[A-Za-z0-9@._]+)/$',profile_detail, name='profile_detail'),
     url(r'^create/$',create_profile,name='create_profile'),
)
