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

class IndexView(TemplateView):
    def get(self, request):
        return HttpResponse('')
