# -*- coding: utf-8 -*-
from datetime import date
import os
import urlparse
import urllib
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from recaptcha.client import captcha
from django.contrib.auth.forms import PasswordChangeForm
from school.forms import UsernameChangeForm
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.core.urlresolvers import reverse
import django.template
from django.http import Http404
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.template import RequestContext
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from decorators import need_login, operating_permission
from app.models import SUBJECT_CHOICES as SUBJECT, UserProfile, RegisterForm,\
        KHOI_CHOICES, TINH_CHOICES, Organization, Register, ChangePasswordForm,\
        AuthenticationForm, IP, Feedback, SystemLesson, FeedbackForm, selectForm
from school.models import log_action
from school.utils import make_username, make_default_password, get_school, get_profile_form
import settings
from sms.utils import send_email, sendSMS

REGISTER = os.path.join('app', 'register.html')
MANAGE_REGISTER = os.path.join('app', 'manage_register.html')


class SchoolAdminAddForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SchoolAdminAddForm, self).__init__(*args, **kwargs)
        users = [i.user for i in UserProfile.objects.all()
                if i.organization is None or i.organization.level == 'T']

        for u in User.objects.all():
            if u in users:
                continue
            try:
                org = u.get_profile().organization
                if org is None or org.level == 'T':
                    users.append(u)
            except UserProfile.DoesNotExist:
                users.append(u)

        self.fields['full_name'].choices = [(i.id,
            i.last_name + ' ' + i.first_name) for i in users]
        self.fields['school'].choices = [(o.id,
            o.name) for o in Organization.objects.all() if o.level == 'T']

    full_name = forms.ChoiceField()
    school = forms.ChoiceField()

def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('school_index'))
    else:
        message = ''
        # test new brance
        if request.method == 'POST':
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
                data['status'] = 'CHUA_CAP'
                data['register_date'] = date.today()
                register_form = RegisterForm(data=data)
                if register_form.is_valid():
                    register_form.save()
                    message = u'Bạn đã đăng ký thành công. \
                            Tài khoản của bạn sẽ được gửi vào email sớm nhất có thể.'
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
        province_list = TINH_CHOICES
        level_list = KHOI_CHOICES
        context = RequestContext(request)
        return render_to_response(REGISTER,
                {'province_list': province_list,
                 'level_list': level_list,
                 'message': message},
                context_instance = context)

@need_login
@operating_permission(['SUPER_USER'])
def manage_register(request, sort_by_date=0, sort_by_status=0):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('school_index'))
    if request.method == 'POST':
        if request.is_ajax():
            request_type = request.POST['request_type']
            if request_type == 'del':
                ids = request.POST['data'].split('-')
                try:
                    for id in ids:
                        if id:
                            reg = Register.objects.get(id=int(id))
                            reg.delete()
                    message = u'Xóa thành công'
                    success = True
                    data = simplejson.dumps({
                        'message': message,
                        'success': success
                    })
                    return HttpResponse(data, mimetype='json')
                except Exception as e:
                    print e
                    message = u'Không thể xóa đăng ký'
                    success = False
                    data = simplejson.dumps({
                        'message': message,
                        'success': success
                    })
                    return HttpResponse(data, mimetype='json')
            elif request_type == 'create_acc':
                ids = request.POST['data'].split('-')
                try:
                    account_info = ''
                    for id in ids:
                        if id:
                            reg = Register.objects.get(id=int(id))
                            if reg.status == 'CHUA_CAP':
                                org_name = reg.school_name
                                org_level = 'T'
                                org_school_level = reg.school_level
                                org_status = 0
                                org_manager_name = reg.register_name
                                org_address = reg.school_address
                                phone = reg.register_phone
                                email = reg.register_email
                                school = Organization.objects.create(
                                            name= org_name,
                                            level= org_level,
                                            school_level= org_school_level,
                                            status= org_status,
                                            manager_name= org_manager_name,
                                            address= org_address,
                                            phone= phone,
                                            email= email)
                                user = User()
                                user.username = make_username(
                                        full_name=org_manager_name)
                                user.password, raw_password = make_default_password()
                                if reg.register_name:
                                    temp = reg.register_name.split(' ')
                                    user.first_name = temp[-1]
                                    user.last_name = ' '.join(temp[:-1])
                                user.save()
                                userprofile = UserProfile()
                                userprofile.user = user
                                userprofile.organization = school
                                userprofile.position = 'HIEU_TRUONG'
                                userprofile.save()
                                reg.status = 'DA_CAP'
                                reg.default_user_name = user.username
                                reg.default_password = raw_password
                                reg.save()
                                #notify users about their account via email
                                if school.phone:
                                    sms_msg = 'Tai khoan truongnha.com:\n\
                                            Ten dang nhap:%s\nMat khau:%s\n\
                                            Cam on ban da su dung dich vu!'\
                                            % (unicode(user.username),
                                                    unicode(raw_password))
                                    try:
                                        sendSMS(school.phone, sms_msg, request.user)
                                    except Exception:
                                        pass
                                send_email(u'Tài khoản Trường Nhà',
                                        u'Cảm ơn bạn đã đăng ký để sử dụng dịch vụ Trường Nhà.\nTài khoản của bạn như sau:\n'+ u'Tên đăng nhập:' + unicode(user.username) + u'\n' + u'Mật khẩu:' + unicode(raw_password),
                                        to_addr=[reg.register_email])
                                account_info += str(id) + '-' + user.username + '-' + raw_password + ','
                            else:
                                if reg.register_phone:
                                    sms_msg = 'Tai khoan truongnha.com:\nTen dang nhap:%s\nMat khau:%s\nCam on ban da su dung dich vu!' % (unicode(reg.default_user_name),
                                                 unicode(reg.default_password))
                                    try:
                                        sendSMS(reg.register_phone, sms_msg, request.user)
                                    except Exception:
                                        pass
                                send_email(u'Tài khoản Trường Nhà',
                                        u'Cảm ơn bạn đã đăng ký để sử dụng dịch' +
                                        u'vụ Trường Nhà.\nTài khoản của bạn như' +
                                        u'sau:\n'+ u'Tên đăng nhập:' +
                                        unicode(reg.default_user_name) + u'\n'
                                        + u'Mật khẩu:' +
                                        unicode(reg.default_password),
                                        to_addr=[reg.register_email])
                                account_info += str(id) + '-' + reg.default_user_name + '-' + reg.default_password + ','

                    message = u'Tạo tài khoản thành công'
                    success = True
                    data = simplejson.dumps({
                        'message': message,
                        'account_info': account_info,
                        'success': success
                    })
                    return HttpResponse(data, mimetype='json')
                except Exception as e:
                    print e
                    message = u'Tạo tài khoản không thành công'
                    success = False
                    data = simplejson.dumps({
                        'message': message,
                        'success': success
                    })
                    return HttpResponse(data, mimetype='json')
            else:
                raise Exception("BadRequest")
    if sort_by_date: sort_by_date = '-'
    else: sort_by_date = ''
    if sort_by_status: sort_by_status = '-'
    else: sort_by_status = ''

    registers = Register.objects.order_by(sort_by_date+'register_date',
            sort_by_status+'status')
    if sort_by_date == '-': sort_by_date = 0
    else: sort_by_date = 1
    if sort_by_status == '-': sort_by_status = 0
    else: sort_by_status = 1
    context = RequestContext(request)
    return render_to_response(MANAGE_REGISTER, {
        'registers': registers,
        'short_by_date': sort_by_date,
        'short_by_status': sort_by_status },
        context_instance=context)


@csrf_protect
@never_cache
@need_login
def change_password(request,
        template_name='app/change_password.html',
        post_change_redirect=None,
        password_change_form=ChangePasswordForm,
        current_app=None, extra_context=None):
    if not post_change_redirect:
        redirect = reverse('app.views.change_password_done')
    else: redirect = post_change_redirect
    if request.method == "POST":
        form = password_change_form(
                user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(redirect)
    else:
        form = password_change_form(user=request.user)
    context = {'form': form, }
    context.update(extra_context or {})
    return render_to_response(template_name,
            context,
            context_instance=django.template.RequestContext(request,
                current_app=current_app))

def change_password_done(request):
    t = django.template.loader.get_template(os.path.join('app',
        'change_password_done.html'))
    c = django.template.RequestContext(request)
    return HttpResponse(t.render(c))

@csrf_protect
@never_cache
def login(request, template_name='app/login.html',
          redirect_after=None,
          demo_account=None,
          redirect_field_name=REDIRECT_FIELD_NAME,
          api_called=False):

    """
    login the system
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    error = None
    error_type = None
    login_failure_exceed = False
    if request.method == "POST":
        if api_called:
            form = AuthenticationForm(data=request.POST,
                    request=request,
                    api_called=True)
        else:
            if demo_account: request.POST['login_type'] = demo_account
            form = AuthenticationForm(data=request.POST, request=request)

        if form.is_valid():
            netloc = urlparse.urlparse(redirect_to)[1]
            # Use default setting if redirect_to is empty
            if not redirect_to:
                if not redirect_after:
                    redirect_to = settings.LOGIN_REDIRECT_URL
                else: redirect_to = urllib.unquote(urllib.unquote(redirect_after))

            # Security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())
            #TODO: notice IP and tell user if the IP is stranger
            if not request.user.is_anonymous():
                IP.reset(request.META['REMOTE_ADDR'])
                request.session.set_expiry(0)
                log_action(request, form.get_user(), "logged in")
            elif api_called: return HttpResponse(status=401)
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            if api_called: return HttpResponse(status=200)
            return HttpResponseRedirect(redirect_to)
        else:
            error = form._errors
            error_type = form.errors_type
            try:
                IP.recognize(request.META['REMOTE_ADDR'], request.user)
            except Exception as e:
                if e.message == 'LoginFailureExceed': login_failure_exceed = True
            if api_called: return HttpResponse(status=401)
    else:
        if IP.exceed_failure_limit(request.META['REMOTE_ADDR']):
            login_failure_exceed = True
        form = AuthenticationForm(request)
        if api_called:
            request.session.set_test_cookie()
            return HttpResponse(content=simplejson.dumps({
            'csrf_token':get_token(request)}), mimetype='json')

    request.session.set_test_cookie()

    context = {
        'form': form,
        'error': error,
        'error_type': error_type,
        'login_failure_exceed': login_failure_exceed,
        redirect_field_name: redirect_to
    }
    return render_to_response(template_name, context,
            context_instance=django.template.RequestContext(request))

def feedback(request):
    if request.method == 'POST': # If the form has been submitted...
        if request.is_ajax():
            user = request.user
            if (request.user.is_anonymous()
                    or request.user.username in [settings.DEMO_LOGIN_SCHOOL,
                        settings.DEMO_LOGIN_TEACHER,
                        settings.DEMO_LOGIN_UPPER,
                        settings.DEMO_LOGIN_STUDENT]):
                url = 'url: ' + request.POST['feedback_url']
                user_name = 'name: ' + unicode(request.POST['username'])
                email = 'email: ' + unicode(request.POST['userEmail'])
                content = 'content: ' + unicode(request.POST['content'])
                if 'subject' in request.POST:
                    subject= unicode(request.POST['subject'])
                else: subject = u'[www.truongnha.com] Users\' feedback'
                message = '\n'.join([url, user_name, email, content])
                Feedback.objects.create(
                    content = content,
                    title = url,
                    email = email,
                    fullname = user)
                print message
                send_email(subject, message, None,
                        [ 'vu.tran54@gmail.com',
                            'truonganhhoang@gmail.com',
                            'luulethe@gmail.com',])
                return HttpResponse(simplejson.dumps({'success': True}),
                        mimetype='json')
            else:
                url = 'url: ' + request.POST['feedback_url']
                user_name = 'user: ' + unicode(request.user)
                profile = user.userprofile
                if profile.position in ['HIEU_TRUONG', 'HIEU_PHO',
                        'GIAM_DOC_SO', 'TRUONG_PHONG']:
                    email = profile.organization.email
                    phone = profile.organization.phone
                else:
                    if profile.position == 'HOC_SINH':
                        email = user.pupil.email
                        phone = user.pupil.sms_phone
                    elif profile.position == 'GIAO_VIEN':
                        email = user.teacher.email
                        phone = user.teacher.sms_phone
                user_email = 'email: ' + unicode(email)
                user_phone = 'phone: ' + unicode(phone)
                school = 'school: ' + unicode(get_school(request))
                content = request.POST['content']
                subject = u'[www.truongnha.com] Users\' feedback'
                message = '\n'.join([url, user_name, user_email,
                    user_phone, school, content])
                Feedback.objects.create(
                    content = content,
                    title = url,
                    email = school,
                    fullname = user
                )
                print message
                send_email(subject, message, '',
                        ['vu.tran54@gmail.com',
                            'truonganhhoang@gmail.com',
                            'luulethe@gmail.com',
                            'testEmail@truongnha.com'])
                return HttpResponse(simplejson.dumps({'success': True}),
                        mimetype='json')
        else:
            form = FeedbackForm(request.POST) # A form bound to the POST data
            if form.is_valid():
                c = Feedback(fullname = form.cleaned_data['fullname'] ,
                             phone = form.cleaned_data['phone'],
                             email = form.cleaned_data['email'],
                             title = form.cleaned_data['title'],
                             content = form.cleaned_data['content'],
                             )
                c.save()
                return HttpResponseRedirect('/app/contact') # Redirect after POST
    else:
        form = FeedbackForm() # An unbound form
    return render_to_response('contact.html', {'form': form}, django.template.RequestContext(request))

@need_login
@operating_permission(['SUPER_USER'])
def system_subject_agenda(request, subject = 1, grade = 6, term = 1):
    lessons = ''
    data = {'subject' : subject, 'grade' : grade, 'term' : term}
    form = selectForm(data)
    if request.method == 'POST':
        form = selectForm(request.POST)
        try:
            lessons = SystemLesson.objects.filter(subject = request.POST['subject'], grade = int(request.POST['grade']), term = int(request.POST['term']))
        except  Exception:
            pass
        c = RequestContext(request,{'list': lessons, 'id': subject, 'subject' : SUBJECT[int(request.POST['subject'])-1][1], 'grade' : int(request.POST['grade']), 'term' : request.POST['term'], 'form':form})
    else:
        try:
            lessons = SystemLesson.objects.filter(subject = subject, grade = grade, term = term)
        except  Exception:
            lessons = None
        c = RequestContext(request,{'list': lessons, 'id': subject, 'subject' : SUBJECT[int(subject)-1][1], 'grade' : grade, 'term' : term, 'form':form})
    t = loader.get_template(os.path.join('app', 'manage_system_agenda.html'))
    return HttpResponse(t.render(c))

def profile_detail(request, username, public_profile_field=None,
                   template_name='app/profile_detail.html'):
    user = get_object_or_404(User, username=username)
    try:
        profile_obj = user.get_profile()
        passwordform = PasswordChangeForm(user)
        accountform = UsernameChangeForm(user)
    except ObjectDoesNotExist:
        raise Http404
    message = ''
    if request.method == 'POST':
        try:
            d = request.POST['new_username']
            accountform = UsernameChangeForm(user, request.POST)
            if accountform.is_valid() and user.userprofile.username_change == 0:
                accountform.save()
                return HttpResponseRedirect(reverse('change_success'))
        except Exception as e:
            accountform = UsernameChangeForm(user)
            print e

        try:
            d = request.POST['new_password1']
            passwordform = PasswordChangeForm(user, request.POST)
            if passwordform.is_valid():
                passwordform.save()
                return HttpResponseRedirect(reverse('change_success'))
        except Exception as e:
            passwordform = PasswordChangeForm(user)
            print e

        try:
#            profile_obj.phone = request.POST['phone']
            profile_obj.notes = request.POST['notes']
            profile_obj.save()
            message = u'Đã lưu'
            data = simplejson.dumps({'message': message})
            return HttpResponse(data, mimetype='json')
        except Exception as e:
            print e

    if public_profile_field is not None and \
       not getattr(profile_obj, public_profile_field):
        profile_obj = None
    return render_to_response(template_name,
                              { 'profile': profile_obj,
                                'password' : passwordform,
                                'username': accountform,
                                'message' : message},
                              context_instance=RequestContext(request))

@need_login
def create_profile(request, form_class=None, success_url=None,
                   template_name='profiles/create_profile.html'):
    try:
        profile_obj = request.user.get_profile()
        return HttpResponseRedirect(reverse('profile_detail'))
    except ObjectDoesNotExist:
        pass


    if success_url is None:
        success_url = reverse('profiles_profile_detail',
                              kwargs={ 'username': request.user.username })
    if form_class is None:
        form_class = get_profile_form()
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            profile_obj = form.save(commit=False)
            profile_obj.user = request.user
            profile_obj.save()
            if hasattr(form, 'save_m2m'):
                form.save_m2m()
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=RequestContext(request))
