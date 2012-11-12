# coding=utf-8
# Create your views here.
import os
import simplejson
import random
import string
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
from django.core.exceptions import ObjectDoesNotExist
import validations
from teacher.models import Person, Teacher, Register
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
        
    def _get_teacher(self):
        return self.request.user.teachers

    def _right_teacher_id(self, teacher_id):
        return teacher_id == unicode(self.teacher.id)

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
        return handler(request, *args, **kwargs)

class IndexView(BaseTeacherView):
    def get(self, *args, **kwargs):
        print 'in view'
        return HttpResponse('', mimetype='json')

class RegisterView(TemplateView):
    template_name = os.path.join('teacher', 'register.html')

    class RegisterForm(forms.ModelForm):

        def __init__(self, *args, **kwargs):
            super(RegisterView.RegisterForm, self).__init__(*args, **kwargs)
            self.fields['birthday'].widget.attrs.update({'class' : 'datepicker'})

        class Meta:
            model = Register
            exclude = ('status', 'register_date', 'default_user_name',
                    'default_password', 'activation_key')

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
            activation_key = ''.join(random.choice(string.ascii_uppercase
                + string.digits) for n in range(20))
            data['activation_key'] = activation_key
            register_form = RegisterView.form(data=data)
            if register_form.is_valid():
                new_register = register_form.save(commit = False)
                new_register.activation_key = activation_key
                new_register.save()


                message = u'Bạn đã đăng ký thành công. \
                        Vui lòng kiểm tra email để kích hoạt tài khoản.'
                mail_message = u'Vui lòng truy cập vào địa chỉ http://truongnha.com/teacher/activate/%s/ để hoàn tất đăng kí và kích hoạt tài khoản của bạn.' % (data['activation_key'])
                send_email(u'Hoàn tất đăng kí tại TruongNha.com', mail_message,
                    to_addr=[data['email']])

                success = True
                if request.is_ajax():
                    response = simplejson.dumps({
                        'success': success,
                        'message': message,
                        'redirect': reverse('index')
                    })
                    return HttpResponse(response, mimetype='json')
            else:
                message = u"Có lỗi ở thông tin nhập vào"
                try:
                    old_register = Register.objects.get(email=data['email'])
                    if old_register:
                        message += u': Email đã tồn tại.'
                except ObjectDoesNotExist:
                    pass
                success = False
                if request.is_ajax():
                    response = simplejson.dumps({
                        'success': success,
                        'message': message
                    })
                    return HttpResponse(response, mimetype='json')


class ActivateView(TemplateView):
    template_name = os.path.join('teacher', 'activate.html')
    def get(self, *args, **kwargs):
        key = self.kwargs['activation_key']
        try:
            register = Register.objects.get(activation_key=key,
                    status__exact='CHUA_CAP')
        except Exception as e:
            print e
            message = u'Địa chỉ kích hoạt không tồn tại. Tài khoản của bạn đã được kích hoạt hoặc không hợp lệ.'
            success = False
            return render_to_response(ActivateView.template_name,
                    {'message': message, 'success' : success})


        register.status='DA_CAP'
        register.save()
        message = u'Tên người đăng ký: %s\nNgày sinh: %s\nĐiện thoại người đăng ký: %s\nEmail người đăng ký: %s\n' % (register.name,
                register.birthday,
                register.phone,
                register.email,)
        send_email(u'Đăng kí tài khoản mới', message,
                to_addr=['vu.tran54@gmail.com', 'loi.luuthe@gmail.com'])
        first_name, last_name = Person.extract_fullname(
                register.name)

        teacher = Teacher(
                first_name=first_name,
                last_name=last_name,
                sms_phone=register.phone,
                email=register.email,
                birthday=register.birthday,
                sex=register.sex)
        username = teacher.make_username()
        raw_password = teacher.make_password()
        user = User.objects.create(
                username=username,
                password=make_password(raw_password),
                first_name=first_name,
                last_name=last_name)
        teacher.user = user
        teacher.save()
        teacher.activate_account()
        message = u'Chúc mừng bạn đã kích hoạt thành công tài khoản. Vui lòng kiểm tra email để biết được thông tin đăng nhập.'
        success = True
        return render_to_response(ActivateView.template_name,
                {'message': message, 'success' : success})

class ForgetPasswordView(TemplateView):
    template_name = os.path.join('teacher','forget_password.html')

    class ForgetPasswordForm(forms.Form):
        account = forms.CharField(required=True, label='Tài khoản')
        email = forms.EmailField(required=True, label='Email')
        phone = forms.CharField(required=True,
                validators=[validations.phone], label='Số điện thoại')

        def clean(self):
            cleaned_data = super(ForgetPasswordView.ForgetPasswordForm, self).clean()
            account = cleaned_data.get("account")
            phone = cleaned_data.get("phone")
            email = cleaned_data.get("email")
            if account:
                try:
                    user = User.objects.select_related().get(username=account)
                    teacher = user.teacher
                    if phone and email:
                        if teacher.sms_phone != phone:
                            self._errors["phone"] = self.error_class(
                                    [u'Số điện thoại không trùng với tài khoản.'])
                            del cleaned_data["phone"]
                        if teacher.email != email:
                            self._errors["email"] = self.error_class(
                                    [u'Email không trùng với tài khoản.'])
                            del cleaned_data["email"]
                except:
                    self._errors["account"] = self.error_class(
                            [u'Tài khoản không tồn tại.'])
                    del cleaned_data["account"]
            return cleaned_data

    form = ForgetPasswordForm

    def get(self,request):
        fpwd_form = ForgetPasswordView.form
        return render_to_response(ForgetPasswordView.template_name,
                {'form':fpwd_form},
                context_instance=RequestContext(request))

    def post(self,request):
        data = request.POST.copy()
        fpwd_form = ForgetPasswordView.form(data=data)
        if fpwd_form.is_valid():
            email = data['email']
            phone = data['phone']
            teacher = Teacher.objects.get(email=email,sms_phone=phone)
            teacher.activate_account()
            response = simplejson.dumps({
                'success': True,
                'message': u'Mật khẩu đang được gửi lại vào email hoặc điện thoại của bạn. Xin bạn vui lòng chờ trong ít phút.',
                })
            return HttpResponse(response, mimetype='json')
        else:
            error = {}
            for k, v in fpwd_form.errors.items():
                error[fpwd_form[k].auto_id] = fpwd_form.error_class.as_text(v)
            response = simplejson.dumps({
                'success': False,
                'err': error,
                'message': u'Có lỗi ở dữ liệu nhập vào'})
            return HttpResponse(response, mimetype='json')

