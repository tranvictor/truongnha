# coding=utf-8
# Create your views here.
import os
import simplejson
import random
import string
from datetime import date, datetime
from recaptcha.client import captcha
from django.db.models import Count
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
import validations
from teacher.models import Person, Teacher, Register, Class,\
        Attend, Student, Mark, Note
from sms.utils import send_email
from teacher.base import BaseTeacherView, RestfulView
import settings
from teacher.utils import to_en1, add_many_students
from teacher.excel_interaction import save_file, process_file, student_export

class IndexView(BaseTeacherView):
    template_name = os.path.join('teacher', 'index.html')

    def _get(*args, **kwargs):
        return {}
    
# The order RestfulView -> BaseTeacherView here is important
class ClassView(RestfulView, BaseTeacherView):
    request_type = ['view', 'create', 'remove', 'modify', 'import', 'export', 'update']


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
                    'class_id': cl.id,
                    'class_note': cl.cl_note,
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
        cl = kwargs['cleaned_params']['class']
        modify_form = self.ClassForm(instance=cl)
        return {'form': modify_form,
                'modify_url': self.reverse('class_view',
                    kwargs={'class_id': cl.id, 'request_type': 'modify'})}

    def _post_modify(self, *args, **kwargs):
        cl = kwargs['cleaned_params']['class']
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
        cl = kwargs['cleaned_params']['class']
        cl.delete()
        return {'success': True,
                'message': u'Bạn đã xóa lớp %s' % cl.name}

    def _get_view(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'class_view.html')
        cl = kwargs['cleaned_params']['class']
        students = cl.students()
        print students
        return {'cl': cl,
                'students': students}


    def _get_export(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'class_view.html')
        cl = kwargs['cleaned_params']['class']
        book = student_export(cl)
        response = HttpResponse(mimetype='application/ms-excel')
        strstr = to_en1(unicode(cl))
        strstr1 = strstr.replace(' ', '_')
        response['Content-Disposition'] = u'attachment; filename=ds_hoc_sinh_%s.xls' % strstr1
        book.save(response)
        return response

    def _post_update(self, *args, **kwargs):
        cl = kwargs['cleaned_params']['class']
        if self.request.is_ajax():
            saving_import_student = self.request.session.pop('saving_import_student')
            number_of_change = add_many_students(student_list=saving_import_student,
                _class = cl,
                force_update=True)
            if number_of_change:
                data = simplejson.dumps(
                    {'success': True,
                     'message': u'Đã cập nhật %s học sinh.' % number_of_change})
            else:
                data = simplejson.dumps(
                    {'success': True,
                     'message': u'Thông tin không thay đổi'})
            return HttpResponse(data, mimetype='json')
            # AJAX Upload will pass the filename in the querystring if it is the "advanced" ajax upload
        try:
            file = self.request.FILES.get('files[]')
        except KeyError:
            return HttpResponseBadRequest("AJAX request not valid")
            # not an ajax upload, so it was the "basic" iframe version with submission via form

    def _post_import(self, *args, **kwargs):
        cl = kwargs['cleaned_params']['class']
        if len(self.request.FILES) == 1:
        # FILES is a dictionary in Django but Ajax Upload gives the uploaded file an
        # ID based on a random number, so it cannot be guessed here in the code.
        # Rather than editing Ajax Upload to pass the ID in the querystring,
        # observer that each upload is a separate request,
        # so FILES should only have one entry.
        # Thus, we can just grab the first (and only) value in the dict.
            file = self.request.FILES.values()[0]
        else:
            raise Exception('BadUpload')

        filename = save_file(self.request.FILES.get('files[]'), self.request.session)
        result, process_file_message, number, number_ok = process_file(filename,
            "import_student")

        if 'error' in result:
            success = False
            message = result['error']
            data = [{'name': file.name,
                     'url': reverse('user_upload', args=[filename]),
                     'sizef': file.size,
                     'success': success,
                     'message': message,
                     'process_message': process_file_message,
                     'error': u'File excel không đúng định dạng'}]
        else:
            existing_student = add_many_students(student_list=result, _class=cl)
            student_confliction = ''
            if existing_student:
                student_confliction = u'Có %s học sinh không được nhập do đã tồn tại trong hệ thống' % len(existing_student)
                self.request.session['saving_import_student'] = existing_student
            data = [{'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'process_message': process_file_message,
                 'student_confliction': student_confliction,
                 'number': number,
                 'number_ok': number_ok - len(existing_student),
                 'message': u'Nhập dữ liệu thành công'}]

        return HttpResponse(simplejson.dumps(data), mimetype='json')


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
                if not st.id:
                    st.save()
                    Attend.objects.create(
                            pupil=st, _class=cl,
                            attend_time=datetime.now(),
                            leave_time=None)
                else:
                    st.save()
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
        cl = kwargs['cleaned_params']['class']
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
        st = kwargs['cleaned_params']['student']
        create_form = self.StudentForm(instance=st)
        return {'form': create_form,
                'create_url': self.reverse('student_create',
                    kwargs={'class_id': kwargs['class_id'],
                        'request_type': 'create'})}
    
    def _post_modify(self, *args, **kwargs):
        cl = kwargs['cleaned_params']['class']
        st = kwargs['cleaned_params']['student']
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
                try:
                    new_register = register_form.save(commit=False)
                    new_register.activation_key = activation_key
                    new_register.save()
                except Exception as e:
                    print e
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
        print self.request.POST
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
                    'student': student.id,
                    'class' : cl.id,
                    'mark' : mark.id,
                    'mark_modify': self.reverse('mark_view',
                        kwargs={'class_id': cl.id,
                                'student_id': student.id,
                                'mark_id':mark.id,
                                'request_type': 'modify'}),

                    'mark_remove': self.reverse('mark_view',
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
    def _get_modify(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'mark_create.html')
        cl_id = kwargs['class_id']
        student_id = kwargs['student_id']
        mark_id = kwargs['mark_id']
        try:
            cl = self.teacher.class_set.get(id=cl_id)
            student = Student.objects.get(id = student_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp hoặc học sinh không tồn tại'}
        if cl.id != student.current_class().id:
            return {'success': False,
                    'message': u'Học sinh không nằm trong lớp'}
        try:
            mark = student.mark_set.get(id = mark_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Điểm không tồn tại'}

        if mark.class_id.id != int(cl_id):
            return {'success': False,
                    'message': u'Điểm không nằm trong lớp'}

        create_form = self.MarkForm(instance=mark)
        return {'form': create_form,
                'class' : cl,
                'success' : True,
                'student' : student,
                'create_url': self.reverse('mark_create',
                    kwargs={'class_id': kwargs['class_id'],
                            'student_id': kwargs['student_id'],
                            'request_type': 'create'})}

    def _post_modify(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'mark_create.html')
        cl_id = kwargs['class_id']
        student_id = kwargs['student_id']
        mark_id = kwargs['mark_id']
        try:
            cl = self.teacher.class_set.get(id=cl_id)
            student = Student.objects.get(id = student_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp hoặc học sinh không tồn tại'}
        if cl.id != student.current_class().id:
            return {'success': False,
                    'message': u'Học sinh không nằm trong lớp'}
        try:
            mark = student.mark_set.get(id = mark_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Điểm không tồn tại'}

        if mark.class_id.id != int(cl_id):
            return {'success': False,
                    'message': u'Điểm không nằm trong lớp'}

        modify_form = self.MarkForm(self.request.POST.copy(),
            instance=mark)
        if modify_form.is_valid():
            mark = modify_form.save(cl, student)
            return {'message': u'Bạn vừa cập nhật thành công điểm',
                    'success': True,
                    'student': student.id,
                    'class' : cl.id,
                    'mark' : mark.id,
                    'mark_modify': self.reverse('mark_view',
                        kwargs={'class_id': cl.id,
                                'student_id': student.id,
                                'mark_id':mark.id,
                                'request_type': 'modify'}),

                    'mark_remove': self.reverse('mark_view',
                        kwargs={'class_id': cl.id,
                                'student_id': student.id,
                                'mark_id':mark.id,
                                'request_type': 'remove'})}
        else:
            error = {}
            for k, v in modify_form.errors.items():
                error[modify_form[k].auto_id] = modify_form.error_class.as_text(v)
            return {'success': False,
                    'error': error,
                    'message': u'Có lỗi ở dữ liệu nhập vào'}

    def _post_remove(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'mark_create.html')
        cl_id = kwargs['class_id']
        student_id = kwargs['student_id']
        mark_id = kwargs['mark_id']
        try:
            cl = self.teacher.class_set.get(id=cl_id)
            student = Student.objects.get(id = student_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp hoặc học sinh không tồn tại'}
        if cl.id != student.current_class().id:
            return {'success': False,
                    'message': u'Học sinh không nằm trong lớp'}
        try:
            mark = student.mark_set.get(id = mark_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Điểm không tồn tại'}

        if mark.class_id.id != int(cl_id):
            return {'success': False,
                    'message': u'Điểm không nằm trong lớp'}
        mark.delete()
        return {'success': True,
                'message': u'Bạn đã xóa điểm %s' % mark}

class ClassMarkView(RestfulView, BaseTeacherView):
    request_type = ['view','modify']

    class HSForm(forms.Form):
        hs = forms.FloatField(label='Hệ số')

    def _get_view(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'mark.html')
        cl = kwargs['cleaned_params']['class']
        students = cl.students()
        marks = cl.mark_set.all()
        hs_list = []
        std_mark = {}
        marks_set = {}
        hs_number_max = {}
        for mark in marks:
            if mark.hs not in hs_list:
                hs_list.append(mark.hs)
        for student in students:
            std_mark[student.id] = marks.filter(student_id = student.id)
            marks_set[student.id] = {}
        for hs in hs_list:
            hs_number_max[hs] = 1
        for hs in hs_list:
            for student in students:
                temp = std_mark[student.id].filter(hs = hs)
                marks_set[student.id][hs] = []
                for m in temp:
                    marks_set[student.id][hs].append(m)
                count = temp.count()
                if count > hs_number_max[hs]:
                    hs_number_max[hs] = count
        total_column = 0
        for hs in hs_number_max:
            total_column += hs_number_max[hs]
        add_column_form = ClassMarkView.HSForm()
        return {'class': cl,
                'students': students,
                'hs_number_max':hs_number_max,
                'total_column':total_column,
                'marks_set':marks_set,
                'add_column_form':add_column_form}

    def _post_modify(self, *args, **kwargs):
        cl_id = kwargs['class_id']
        data = self.request.POST.copy()
        marks_id = data['id_list'].split('-')
        try:
            cl = self.teacher.class_set.get(id=cl_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp học không tồn tại'}
        form = ClassMarkView.HSForm(data)
        if form.is_valid():
            if marks_id != [u'']:
                marks = cl.mark_set.filter(id__in = marks_id)
                for mark in marks:
                    mark.hs = data['hs']
                    mark.save()
            return {'success': True,
                    'message': u'Đã sửa xong hệ số'}
        else:
            error = {}
            for k, v in form.errors.items():
                error[form[k].auto_id] = form.error_class.as_text(v)
            return {'success': False,
                    'error': error,
                    'message': u'Có lỗi ở dữ liệu nhập vào'}
class NoteView(RestfulView, BaseTeacherView):
    request_type = ['modify', 'create', 'remove']

    class NoteForm(forms.ModelForm):
    #        def __init__(self, *args, **kwargs):
    #            super(NoteView.NoteForm, self).__init__(*args, **kwargs)
        def save(self, cl, student, commit=True, *args, **kwargs):
            note = super(NoteView.NoteForm, self).save(commit=False,
                *args, **kwargs)
            note.class_id = cl
            note.student_id = student
            if commit:
                note.save()
            return note
        class Meta:
            model = Note
            exclude = ('created', 'modified', 'class_id', 'student_id')

    def _get_create(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'note_create.html')
        cl_id = kwargs['class_id']
        student_id = kwargs['student_id']
        cl = self.teacher.class_set.get(id=cl_id)
        student = Student.objects.get(id = student_id)
        if cl.id == student.current_class().id:
            create_form = self.NoteForm()
            print create_form
            return {'form': create_form,
                    'class' : cl,
                    'success' : True,
                    'student' : student,
                    'create_url': self.reverse('note_create',
                        kwargs={'class_id': kwargs['class_id'],
                                'student_id': kwargs['student_id'],
                                'request_type': 'create'})}
        else:
            return {'success': False,
                    'message': u'Học sinh không nằm trong lớp'}

    def _post_create(self, *args, **kwargs):
        cl_id = kwargs['class_id']
        print self.request.POST
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
        create_form = self.NoteForm(self.request.POST.copy())
        if create_form.is_valid():
            note = create_form.save(cl, student)
            return {'message': u'Bạn vừa thêm thành công nhận xét',
                    'success': True,
                    'student': student.id,
                    'class' : cl.id,
                    'note' : note.id,
                    'note_modify': self.reverse('note_view',
                        kwargs={'class_id': cl.id,
                                'student_id': student.id,
                                'note_id':note.id,
                                'request_type': 'modify'}),

                    'note_remove': self.reverse('note_view',
                        kwargs={'class_id': cl.id,
                                'student_id': student.id,
                                'note_id':note.id,
                                'request_type': 'remove'})}
        else:
            error = {}
            for k, v in create_form.errors.items():
                error[create_form[k].auto_id] = create_form.error_class.as_text(v)
            return {'success': False,
                    'error': error,
                    'message': u'Có lỗi ở dữ liệu nhập vào'}
    def _get_modify(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'note_create.html')
        cl_id = kwargs['class_id']
        student_id = kwargs['student_id']
        note_id = kwargs['note_id']
        try:
            cl = self.teacher.class_set.get(id=cl_id)
            student = Student.objects.get(id = student_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp hoặc học sinh không tồn tại'}
        if cl.id != student.current_class().id:
            return {'success': False,
                    'message': u'Học sinh không nằm trong lớp'}
        try:
            note = student.note_set.get(id = note_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Nhận xét không tồn tại'}

        if note.class_id.id != int(cl_id):
            return {'success': False,
                    'message': u'Nhận xét không nằm trong lớp'}

        create_form = self.NoteForm(instance=note)
        return {'form': create_form,
                'class' : cl,
                'success' : True,
                'student' : student,
                'create_url': self.reverse('note_create',
                    kwargs={'class_id': kwargs['class_id'],
                            'student_id': kwargs['student_id'],
                            'request_type': 'create'})}

    def _post_modify(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'note_create.html')
        cl_id = kwargs['class_id']
        student_id = kwargs['student_id']
        note_id = kwargs['note_id']
        try:
            cl = self.teacher.class_set.get(id=cl_id)
            student = Student.objects.get(id = student_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp hoặc học sinh không tồn tại'}
        if cl.id != student.current_class().id:
            return {'success': False,
                    'message': u'Học sinh không nằm trong lớp'}
        try:
            note = student.note_set.get(id = note_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Nhận xét không tồn tại'}

        if note.class_id.id != int(cl_id):
            return {'success': False,
                    'message': u'Nhận xét không nằm trong lớp'}

        modify_form = self.NoteForm(self.request.POST.copy(),
            instance=note)
        if modify_form.is_valid():
            note = modify_form.save(cl, student)
            return {'message': u'Bạn vừa cập nhật thành công nhận xét',
                    'success': True,
                    'student': student.id,
                    'class' : cl.id,
                    'note' : note.id,
                    'note_modify': self.reverse('note_view',
                        kwargs={'class_id': cl.id,
                                'student_id': student.id,
                                'note_id':note.id,
                                'request_type': 'modify'}),

                    'note_remove': self.reverse('note_view',
                        kwargs={'class_id': cl.id,
                                'student_id': student.id,
                                'note_id':note.id,
                                'request_type': 'remove'})}
        else:
            error = {}
            for k, v in modify_form.errors.items():
                error[modify_form[k].auto_id] = modify_form.error_class.as_text(v)
            return {'success': False,
                    'error': error,
                    'message': u'Có lỗi ở dữ liệu nhập vào'}

    def _post_remove(self, *args, **kwargs):
        self.template_name = os.path.join('teacher', 'note_create.html')
        cl_id = kwargs['class_id']
        student_id = kwargs['student_id']
        note_id = kwargs['note_id']
        try:
            cl = self.teacher.class_set.get(id=cl_id)
            student = Student.objects.get(id = student_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Lớp hoặc học sinh không tồn tại'}
        if cl.id != student.current_class().id:
            return {'success': False,
                    'message': u'Học sinh không nằm trong lớp'}
        try:
            note = student.note_set.get(id = note_id)
        except ObjectDoesNotExist:
            return {'success': False,
                    'message': u'Nhận xét không tồn tại'}

        if note.class_id.id != int(cl_id):
            return {'success': False,
                    'message': u'Nhận xét không nằm trong lớp'}
        note.delete()
        return {'success': True,
                'message': u'Bạn đã xóa nhận xét %s' % note}
