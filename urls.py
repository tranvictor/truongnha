from django.conf.urls import patterns, include, url
from django.views.static import serve
import os
import settings
import app.views as app_views
import app.urls as app_urls
import teacher.views as teacher_views
import school.urls as school_urls
import api.urls as api_urls
import teacher.urls as teacher_urls
import views
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name="index"),
    # the built-in sign-in/out module
    url(r'^login/$', app_views.login , name="login"),
    url(r'^login/(?P<redirect_after>[/%a-zA-Z0-9_]+)/$',
        app_views.login, name="login_redirect"),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
            {'template_name': os.path.join(settings.TEMPLATE_DIRS[0],
                'app/logout.html'), 'next_page': '/'}, name="logout"),
    url(r'^register/$', app_views.register, name='register'),
    url(r'^teacher/register/$', teacher_views.RegisterView.as_view(),
        name='teacher_register'),
    url(r'^manageRegister/$', app_views.manage_register,
        name='manage_register'),
    url(r'^manageRegister/(?P<sort_by_date>\w+)/$', app_views.manage_register,
        name="manage_register"),
    url(r'^manageRegister/(?P<sort_by_date>\w+)/(?P<sort_by_status>\w+)/$',
        app_views.manage_register, name="manage_register"),
    url(r'^manageSchool/$', app_views.manage_school,
        name='manage_school'),
    url(r'^manageSchool/(?P<sort_by_balance>\w+)/$', app_views.manage_school,
        name="manage_school"),
    url(r'^manageSchool/(?P<sort_by_balance>\w+)/(?P<sort_by_status>\w+)/$',
        app_views.manage_school, name="manage_school"),


    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sms-manager/$', app_views.admin_sms_manager,
        name='admin_sms_manager'),
    #object comments
    #url(r'^comments/', include(comment_urls)),
    
    # urls for app app
    url(r'^app/', include(app_urls)),
    # url for school app
    #url(r'^school/(?P<school_id>\d+)/', include(school_urls)),
    url(r'^school/', include(school_urls)),
    url(r'^teacher/(?P<teacher_id>\d*)/', include(teacher_urls)),
    url(r'^api/', include(api_urls)),

    url(r'^about/$', views.about, name="about"),
    url(r'help/(?P<page>[\w\-]*)$', views.help, name="help"),

#    url(r'^profile/', 'views.get_absolute_url'),

    #url for help app

    (r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    (r'^(?P<path>robots.txt)$', serve, {'document_root': settings.STATIC_ROOT}),
    url(r'^user_uploaded/(?P<path>.*)$', serve,
        {'document_root': settings.TEMP_FILE_LOCATION}, name='user_upload'),
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to',
        {'url': '/static/images/favicon.ico'}),
)
