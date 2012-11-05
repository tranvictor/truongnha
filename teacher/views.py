# coding=utf-8
# Create your views here.
import os
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django import forms
from teacher import models
from sms.utils import send_email

NOT_ALLOWED_TEACHER_TEMPLATE = os.path.join('teacher', 'not-allowed.html')

class BaseTeacherView(TemplateView):
    def __init__(self, *args, **kwargs):
        super(BaseTeacherView, self).__init__(*args, **kwargs)
        # Store teacher_id for further usage and checking
        # allow_other_teacher is False means that teacher's page
        # can't be accessed by other users
        self.teacher_id = None
        self.allow_other_teacher = False
        print 'invoke constructor'
        
    def _get_teacher(self):
        return self.request.user.teachers

    def _right_teacher_id(self, teacher_id):
        return teacher_id == self.teacher.id

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        # Before calling the actual view, try to validate teacher.
        # If the page belongs to other teacher rather than user, return an
        # error by default. This default behavior can be disabled if
        # self.allow_other_teacher set to True
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(),
                    self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.teacher_id = kwargs['teacher_id']
        self.teacher = self._get_teacher()
        if (not self.allow_other_teacher
                and not self._right_teacher_id(self.teacher_id)):
            return render_to_response(NOT_ALLOWED_TEACHER_TEMPLATE,
                    {}, context_instance=RequestContext(request))
        self.args = args
        self.kwargs = kwargs
        print self.teacher_id, 'before view'
        return handler(request, *args, **kwargs)

class RegisterView(TemplateView):
    template_name = os.path.join('teacher', 'register.html')

    class RegisterForm(forms.ModelForm):
        def save(self):
            super(RegisterView.RegisterForm, self).save()
            message = u'Tên người đăng ký: %s\n\
                    Điện thoại người đăng ký: %s\n\
                    Email người đăng ký: %s\n\'' % (
                            self.cleaned_data['register_name'],
                            self.cleaned_data['register_phone'],
                            self.cleaned_data['register_email'],)
            send_email(u'Đăng kí tài khoản mới', message,
                    to_addr=['vu.tran54@gmail.com', 'truonganhhoang@gmail.com'])

        class Meta:
            model = models.Register

    def get(self, request):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('teacher_index'))
        register_form = RegisterView.form()
        return render_to_response(RegisterView.template_name,
                {'register_form': register_form},
                context_instance=RequestContext(request))

class IndexView(BaseTeacherView):
    def get(self, *args, **kwargs):
        print 'in view'
        return HttpResponse('', mimetype='json')
