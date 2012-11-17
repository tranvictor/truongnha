from django.conf.urls import patterns, url
from teacher.views import IndexView, ClassView

urlpatterns = patterns('',
        url(r'^$', IndexView.as_view(), name='teacher_index'),
        url(r'class/(?P<request_type>create)$',
            ClassView.as_view(), name='class_create'),
        url(r'class/(?P<class_id>\w+)/(?P<request_type>modify|remove|view)$',
            ClassView.as_view(), name='class_view')
)
