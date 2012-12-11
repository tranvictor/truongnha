# coding=utf-8
# Create your views here.
import os
import simplejson
from datetime import date
from recaptcha.client import captcha
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from teacher import models
from teacher.models import Person, Teacher
from sms.utils import send_email
import settings

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

    # Do the same work with Django reverse method but add
    # valid teacher_id to **kwargs as an extra work
    def reverse(self, *args, **kwargs):
        kwargs['teacher_id'] = self.teacher_id
        return reverse(*args, **kwargs)

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
        if not self.teacher_id:
            self.teacher_id = self.teacher.id
            return HttpResponseRedirect(self.reserve('teacher_index'))
        else:
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

        def __init__(self, *args, **kwargs):
            super(RegisterView.RegisterForm, self).__init__(*args, **kwargs)
            self.fields['birthday'].widget.attrs.update({'class' : 'datepicker'})

        def save(self):
            super(RegisterView.RegisterForm, self).save()
            message = u'Tên người đăng ký: %s\nNgày sinh: %s\nĐiện thoại người đăng ký: %s\nEmail người đăng ký: %s\n' % (self.cleaned_data['name'],
                    self.cleaned_data['birthday'],
                    self.cleaned_data['phone'],
                    self.cleaned_data['email'],)
            send_email(u'Đăng kí tài khoản mới', message,
                    to_addr=['vu.tran54@gmail.com'])
            first_name, last_name = Person.extract_fullname(
                    self.cleaned_data['name'])

            teacher = Teacher(
                    first_name=first_name,
                    last_name=last_name,
                    sms_phone=self.cleaned_data['phone'],
                    email=self.cleaned_data['email'],
                    birthday=self.cleaned_data['birthday'],
                    sex=self.cleaned_data['sex'])
            username = teacher.make_username()
            raw_password = teacher.make_password()
            user = User.objects.create(
                    username=username,
                    password=make_password(raw_password),
                    first_name=first_name,
                    last_name=last_name)
            teacher.user = user
            teacher.save()
            return teacher

        class Meta:
            model = models.Register
            exclude = ('status', 'register_date', 'default_user_name',
                    'default_password')

    form = RegisterForm

    def get(self, request):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('teacher_index',
                kwargs={'teacher_id':''}))
        register_form = RegisterView.form()
        return render_to_response(RegisterView.template_name,
                {'register_form': register_form},
                context_instance=RequestContext(request))

    def post(self, request):
        if not settings.IS_TESTING:
            captchar_check = captcha.submit(
                request.POST['recaptcha_challenge_field'],
                request.POST['recaptcha_response_field'],
                settings.CAPTCHA_PRIVATE_KEY,
                request.META['REMOTE_ADDR']
            )
        if not (settings.IS_TESTING or captchar_check.is_valid):
            message = u'2 từ bạn điền không đúng'
            success = False
            if request.is_ajax():
                response = simplejson.dumps({
                    'success': success,
                    'message': message
                })
                return HttpResponse(response, mimetype='json')
        else:
            data = request.POST.copy()
            data['register_date'] = date.today()
            register_form = RegisterView.form(data=data)
            if register_form.is_valid():
                teacher = register_form.save()
                teacher.activate_account()
                message = u'Bạn đã đăng ký thành công. Tài khoản của bạn sẽ được gửi vào email sớm nhất có thể.'
                success = True
                if request.is_ajax():
                    response = simplejson.dumps({
                        'success': success,
                        'message': message,
                        'redirect': reverse('login')
                    })
                    return HttpResponse(response, mimetype='json')
            else:
                message = u"Có lỗi ở thông tin nhập vào"
                success = False
                if request.is_ajax():
                    response = simplejson.dumps({
                        'success': success,
                        'message': message
                    })
                    return HttpResponse(response, mimetype='json')

class IndexView(BaseTeacherView):
    def get(self, *args, **kwargs):
        print 'in view'
        return HttpResponse('', mimetype='json')
