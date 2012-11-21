# coding=utf-8
# Create your views here.
import os
import simplejson
import random
import string
from datetime import date, datetime
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
from teacher.models import Person, Teacher, Register, Class,\
        Attend, Student, Mark
from sms.utils import send_email
from teacher.base import BaseTeacherView, RestfulView
import settings

class IndexView(BaseTeacherView):
    template_name = os.path.join('teacher', 'index.html')

    def _get(*args, **kwargs):
        return {}
    
# The order RestfulView -> BaseTeacherView here is important
class ClassView(RestfulView, BaseTeacherView):
    request_type = ['view', 'create', 'remove', 'modify']

    class ClassForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(ClassView.ClassForm, self).__init__(*args, **kwargs)
        
        def save(self, teacher, commit=True, *args, **kwargs):
            cl = super(ClassView.ClassForm, self).save(commit=False,
                    *args, **kwargs)
            cl.index = teacher.class_set.count()
            cl.teacher_id = teacher
            if not cl.id:
                cl.created = datetime.now()
            if commit:
                cl.save()
            return cl

        class Meta:
            model = Class
            exclude = ('index', 'created', 'teacher_id')

    def _get_create(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'class_create.html')
        create_form = self.ClassForm()
        return {'form': create_form,
                'create_url': self.reverse('class_create',
                    kwargs={'request_type': 'create'})}

    def _post_create(self, *args, **kwargs):
        create_form = self.ClassForm(self.request.POST.copy())
        if create_form.is_valid():
            cl = create_form.save(self.teacher)
            return {'message': u'Bạn vừa tạo thành công lớp học',
                    'success': True,
                    'class_name': cl.name,
                    'class_url': self.reverse('class_view',
                        kwargs={'class_id': cl.id, 'request_type': 'view'}),
                    'class_modify': self.reverse('class_view',
                        kwargs={'class_id': cl.id, 'request_type': 'modify'}),
                    'class_remove': self.reverse('class_view',
                        kwargs={'class_id': cl.id, 'request_type': 'remove'})}
        else:
            error = {}
            for k, v in create_form.errors.items():
                error[create_form[k].auto_id] = create_form.error_class.as_text(v)
            return {'success': False,
                    'error': error,
                    'message': u'Có lỗi ở dữ liệu nhập vào'}
    
    def _get_modify(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'class_create.html')
        cl_id = kwargs['class_id']
        try:
            cl = self.teacher.class_set.get(id=cl_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp không tồn tại'}
        modify_form = self.ClassForm(instance=cl)
        return {'form': modify_form,
                'modify_url': self.reverse('class_view',
                    kwargs={'class_id': cl_id, 'request_type': 'modify'})}

    def _post_modify(self, *args, **kwargs):
        cl_id = kwargs['class_id']
        try:
            cl = self.teacher.class_set.get(id=cl_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp không tồn tại'}
        modify_form = self.ClassForm(self.request.POST.copy(),
                instance=cl)
        if modify_form.is_valid():
            cl = modify_form.save(self.teacher)
            return {'message': u'Bạn vừa cập nhật thành công lớp học',
                    'success': True,
                    'class_name': cl.name,
                    'class_url': self.reverse('class_view',
                        kwargs={'class_id': cl.id, 'request_type': 'view'}),
                    'class_modify': self.reverse('class_view',
                        kwargs={'class_id': cl.id, 'request_type': 'modify'}),
                    'class_remove': self.reverse('class_view',
                        kwargs={'class_id': cl.id, 'request_type': 'remove'})}
        else:
            error = {}
            for k, v in modify_form.errors.items():
                error[modify_form[k].auto_id] = modify_form.error_class.as_text(v)
            return {'success': False,
                    'error': error,
                    'message': u'Có lỗi ở dữ liệu nhập vào'}

    def _post_remove(self, *args, **kwargs):
        cl_id = kwargs['class_id']
        try:
            cl = self.teacher.class_set.get(id=cl_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp không tồn tại'}
        cl.delete()
        return {'success': True,
                'message': u'Bạn đã xóa lớp %s' % cl.name}

    def _get_view(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'class_view.html')
        cl_id = kwargs['class_id']
        try:
            cl = self.teacher.class_set.get(id=cl_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp không tồn tại'}
        students = cl.students()
        print students
        return {'cl': cl,
                'students': students}

class StudentView(RestfulView, BaseTeacherView):
    request_type = ['view', 'modify', 'create', 'remove']

    class StudentForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(StudentView.StudentForm, self).__init__(*args, **kwargs)
            self.fields['birthday'].widget.attrs.update({'class' : 'datepicker'})
        
        def save(self, cl, commit=True, *args, **kwargs):
            st = super(StudentView.StudentForm, self).save(commit=False,
                    *args, **kwargs)
            st.index = cl.number_of_students()
            if commit:
                st.save()
                if st.id:
                    tmp = Attend.objects.create(
                            pupil=st, _class=cl,
                            attend_time=datetime.now(),
                            leave_time=None)
            return st

        class Meta:
            model = Student
            exclude = ('index', 'current_status', 'user', 'classes')
    
    def _get_create(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'student_create.html')
        create_form = self.StudentForm()
        print create_form
        return {'form': create_form,
                'create_url': self.reverse('student_create',
                    kwargs={'class_id': kwargs['class_id'],
                        'request_type': 'create'})}

    def _post_create(self, *args, **kwargs):
        cl_id = kwargs['class_id']
        try:
            cl = self.teacher.class_set.get(id=cl_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp không tồn tại'}

        create_form = self.StudentForm(self.request.POST.copy())
        if create_form.is_valid():
            st = create_form.save(cl)
            return {'message': u'Bạn vừa tạo thành công học sinh',
                    'success': True,
                    'student': st,
                    'student_url': self.reverse('student_view',
                        kwargs={'class_id': cl.id,
                            'student_id': st.id,
                            'request_type': 'view'}),
                    'student_modify': self.reverse('student_view',
                        kwargs={'class_id': cl.id,
                            'student_id': st.id,
                            'request_type': 'modify'}),
                    'student_remove': self.reverse('student_view',
                        kwargs={'class_id': cl.id,
                            'student_id': st.id,
                            'request_type': 'remove'})}
        else:
            error = {}
            for k, v in create_form.errors.items():
                error[create_form[k].auto_id] = create_form.error_class.as_text(v)
            return {'success': False,
                    'error': error,
                    'message': u'Có lỗi ở dữ liệu nhập vào'}

    def _get_modify(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'student_create.html')
        try:
            cl = self.teacher.class_set.get(id=kwargs['class_id'])
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp không tồn tại'}
        try:
            st = cl.student_set.get(id=kwargs['student_id'])
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Học sinh không tồn tại'}
        create_form = self.StudentForm(instance=st)
        return {'form': create_form,
                'create_url': self.reverse('student_create',
                    kwargs={'class_id': kwargs['class_id'],
                        'request_type': 'create'})}
    
    def _post_modify(self, *args, **kwargs):
        try:
            cl = self.teacher.class_set.get(id=kwargs['class_id'])
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp không tồn tại'}
        try:
            st = cl.student_set.get(id=kwargs['student_id'])
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Học sinh không tồn tại'}
        modify_form = self.StudentForm(self.request.POST.copy(),
                instance=st)
        if modify_form.is_valid():
            st = modify_form.save(cl)
            return {'message': u'Bạn vừa cập nhật thành công học sinh',
                    'success': True,
                    'student': st,
                    'student_url': self.reverse('student_view',
                        kwargs={'class_id': cl.id,
                            'student_id': st.id,
                            'request_type': 'view'}),
                    'student_modify': self.reverse('student_view',
                        kwargs={'class_id': cl.id,
                            'student_id': st.id,
                            'request_type': 'modify'}),
                    'student_remove': self.reverse('student_view',
                        kwargs={'class_id': cl.id,
                            'student_id': st.id,
                            'request_type': 'remove'})}
        else:
            error = {}
            for k, v in modify_form.errors.items():
                error[modify_form[k].auto_id] = modify_form.error_class.as_text(v)
            return {'success': False,
                    'error': error,
                    'message': u'Có lỗi ở dữ liệu nhập vào'}

    def _post_remove(self, *args, **kwargs):
        try:
            cl = self.teacher.class_set.get(id=kwargs['class_id'])
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp không tồn tại'}
        try:
            st = cl.student_set.get(id=kwargs['student_id'])
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Học sinh không tồn tại'}
        st.delete()
        return {'success': True,
                'message': u'Bạn đã xóa học sinh %s' % st.full_name()}

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
                new_register = register_form.save(commit=False)
                new_register.activation_key = activation_key
                new_register.save()


                message = u'Bạn đã đăng ký thành công. \
                        Vui lòng kiểm tra email để kích hoạt tài khoản.'
                site = request.get_host()
                if site != 'localhost:8000':
                    site = 'https://' + site
                mail_message = u'Vui lòng truy cập vào địa chỉ %s/teacher/activate/%s/ để hoàn tất đăng kí và kích hoạt tài khoản của bạn.' % (site, data['activation_key'])
                send_email(u'Hoàn tất đăng kí tại ' + unicode(site), mail_message,
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
                    teacher = Teacher.objects.select_related().get(user__username=account)
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

class MarkView(RestfulView, BaseTeacherView):
    request_type = ['modify', 'create', 'remove']

    class MarkForm(forms.ModelForm):
#        def __init__(self, *args, **kwargs):
#            super(MarkView.MarkForm, self).__init__(*args, **kwargs)
        def save(self, cl, student, commit=True, *args, **kwargs):
            mark = super(MarkView.MarkForm, self).save(commit=False,
                *args, **kwargs)
            mark.class_id = cl
            mark.student_id = student
            if commit:
                mark.save()
            return mark
        class Meta:
            model = Mark
            exclude = ('created', 'modified', 'class_id', 'student_id')

    def _get_create(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'mark_create.html')
        cl_id = kwargs['class_id']
        student_id = kwargs['student_id']
        cl = self.teacher.class_set.get(id=cl_id)
        student = Student.objects.get(id = student_id)
        if cl.id == student.current_class().id:
            create_form = self.MarkForm()
            print create_form
            return {'form': create_form,
                    'class' : cl,
                    'success' : True,
                    'student' : student,
                    'create_url': self.reverse('mark_create',
                        kwargs={'class_id': kwargs['class_id'],
                                'student_id': kwargs['student_id'],
                                'request_type': 'create'})}
        else:
            return {'success': False,
                    'message': u'Học sinh không nằm trong lớp'}

    def _post_create(self, *args, **kwargs):
        cl_id = kwargs['class_id']
        student_id = kwargs['student_id']
        try:
            cl = self.teacher.class_set.get(id=cl_id)
            student = Student.objects.get(id = student_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp hoặc học sinh không tồn tại'}
        if cl.id != student.current_class().id:
            return {'success': False,
                    'message': u'Học sinh không nằm trong lớp'}
        create_form = self.MarkForm(self.request.POST.copy())
        if create_form.is_valid():
            mark = create_form.save(cl, student)
            return {'message': u'Bạn vừa thêm thành công điểm',
                    'success': True,
                    'student': student,
                    'class' : cl,
                    'mark' : mark,
                    'student_modify': self.reverse('mark_view',
                        kwargs={'class_id': cl.id,
                                'student_id': student.id,
                                'mark_id':mark.id,
                                'request_type': 'modify'}),

                    'student_remove': self.reverse('mark_view',
                        kwargs={'class_id': cl.id,
                                'student_id': student.id,
                                'mark_id':mark.id,
                                'request_type': 'remove'})}
        else:
            error = {}
            for k, v in create_form.errors.items():
                error[create_form[k].auto_id] = create_form.error_class.as_text(v)
            return {'success': False,
                    'error': error,
                    'message': u'Có lỗi ở dữ liệu nhập vào'}
