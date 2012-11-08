from django.conf.urls import patterns, url
from teacher.views import IndexView, RegisterView

urlpatterns = patterns('',
        url(r'^$', IndexView.as_view(), name='teacher_index'),
        url(r'register$', RegisterView.as_view(), name='teacher_register'),
)
