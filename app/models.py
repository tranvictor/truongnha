#coding: utf-8
from ConfigParser import SafeConfigParser
import os
import codecs
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from recaptcha.client import captcha
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from sms.utils import send_email
import settings


SCHOOL_SETTING_FOLDER = settings.SCHOOL_SETTING_FOLDER

ORGANIZATION_LEVEL_CHOICES = (('T', u'Trường'),
                              ('P', u'Phòng'),
                              ('S', u'Sở'))

POSITION_CHOICE = (('HOC_SINH', u'Học sinh'),
                    ('GIAO_VU', u'Giáo vụ'),
                    ('GIAO_VIEN', u'Giáo viên'),
                   ('HIEU_PHO', u'Hiệu phó'),
                   ('HIEU_TRUONG', u'Hiệu trưởng'),
                   ('GIAM_DOC_SO', u'Giám đốc sở'),
                   ('TRUONG_PHONG', u'Trưởng phòng'))

KHOI_CHOICES = (('2', u'Cấp 2'),
                ('3', u'Cấp 3'))

SCHOOL_ACTION_STATUS = ((0, u'Trường mới'),
                        (1, u'Đang học kỳ 1'),
                        (2, u'Đang học kỳ 2'),
                        (3, u'Đang nghỉ hè'))
SCHOOL_TYPES = (('0', u'Công lập'), ('1', u'Giáo dục thường xuyên'))

TINH_CHOICES = (('1',u'An Giang'),('2',u'Bà Rịa-Vũng Tàu'),('3',u'Bạc Liêu'),('4',u'Bắc Cạn'),('5',u'Bắc Giang'),
    ('6',u'Bắc Ninh'),('7',u'Bến Tre'),('8',u'Bình Dương'),('9',u'Bình Định'),('10',u'Bình Phước'),('11',u'Bình Thuận'),
    ('12',u'Cà Mau'),('13',u'Cao Bằng'),('14',u'Cần Thơ'),('15',u'Đà Nẵng'),('16',u'Đắk Lắk'),('17',u'Đắk Nông'),
    ('18',u'Điện Biên'),('19',u'Đồng Nai'),('20',u'Đồng Tháp'),('21',u'Gia Lai'),('22',u'Hà Giang'),('23',u'Hà Nam'),
    ('24',u'Hà Nội'),('25',u'Hà Tĩnh'),('26',u'Hải Dương'),('27',u'Hải Phòng'),('28',u'Hòa Bình'),('29',u'Hồ Chí Minh'),
    ('30',u'Hậu Giang'),('31',u'Hưng Yên'),('32',u'Khánh Hòa'),('33',u'Kiên Giang'),('34',u'Kom Tum'),('35',u'Lai Châu'),
    ('36',u'Lào Cai'),('37',u'Lạng Sơn'),('38',u'Lâm Đồng'),('39',u'Long An'),('40',u'Nam Định'),('41',u'Nghệ An'),
    ('42',u'Ninh Bình'),('43',u'Ninh Thuận'),('44',u'Phú Thọ'),('45',u'Phú Yên'),('46',u'Quảng Bình'),('47',u'Quảng Nam'),
    ('48',u'Quảng Ngãi'),('49',u'Quảng Ninh'),('50',u'Quảng Trị'),('51',u'Sóc Trăng'),('52',u'Sơn La'),('53',u'Tây Ninh'),
    ('54',u'Thái Bình'),('55',u'Thái Nguyên'),('56',u'Thanh Hóa'),('57',u'Thừa Thiên-Huế'),('58',u'Tiền Giang'),
    ('59',u'Trà Vinh'),('60',u'Tuyên Quang'),('61',u'Vĩnh Long'),('62',u'Vĩnh Phúc'),('63',u'Yên Bái'))

REGISTER_STATUS_CHOICES = (('DA_CAP', u"Đã cấp"), ('CHUA_CAP', u"Chưa cấp"))

SUBJECT_CHOICES = ((1,u'Toán'),
                 (2, u'Vật lí'),
                 (3, u'Hóa học'),
                 (4, u'Sinh học'),
                 (5, u'Ngữ văn'),
                 (6, u'Lịch sử'),
                 (7, u'Địa lí'),
                 (8, u'Ngoại ngữ'),
                 (9, u'GDCD'),
                 (10, u'Công nghệ'),
                 (11, u'Thể dục'),
                 (12, u'Âm nhạc'),
                 (13, u'Mĩ thuật'),
                 (14, u'NN2'),
                 (15, u'Tin học'),
                 (16, u'GDQP-AN'))

GRADES_CHOICES = ((6, u'Lớp 6'),
                  (7, u'Lớp 7'),
                  (8, u'Lớp 8'),
                  (9, u'Lớp 9'),
                  (10, u'Lớp 10'),
                  (11, u'Lớp 11'),
                  (12, u'Lớp 12'))
TERMS=((1, u'Kì 1'),
        (2, u'Kì 2'))


class MyConfigParser(SafeConfigParser):
    def write(self, fp):
        for section in self._sections:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key == "__name__":
                    continue
                if (value is not None) or (self._optcre == self.OPTCRE):
                    key = " = ".join((key, unicode(value).replace('\n', '\n\t')))
                fp.write("%s\n" % key)
            fp.write("\n")


class Organization(models.Model):
    SEMESTER_STATUS = [u'Chưa thiết lập', u'Học kỳ I',
                       u'Học kỳ II', u'Học kỳ hè']
    name = models.CharField(u'Tên tổ chức', max_length=100)
    level = models.CharField(u"cấp", max_length=2,
                                choices=ORGANIZATION_LEVEL_CHOICES) 
    #------- those attributes is used for School only -------------------------
    school_level = models.CharField(u"Khối học", max_length=6, blank=True,
                                    null=True, choices=KHOI_CHOICES)
    status = models.SmallIntegerField(max_length=3, blank=True, null=True,
                                    choices=SCHOOL_ACTION_STATUS)
    school_type = models.CharField(u'Loại trường', max_length=30, blank=True,
                                    choices=SCHOOL_TYPES)
    #--------------------------------------------------------------------------
    upper_organization = models.ForeignKey('self', blank=True, null=True,
                                            verbose_name='Trực thuộc')
    manager_name = models.CharField("Tên thủ trưởng", max_length=100, null=True)
    address = models.CharField("Địa chỉ", max_length=255, blank=True, null=True)
    phone = models.CharField("Điện thoại", max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    district = models.CharField(u'Huyện',max_length = 100,blank=True,null=True,
                                default='')

    class Meta:
        verbose_name_plural = "Tổ chức"

    def get_current_year(self):
        return self.year_set.latest('time')

    def get_status(self):
        if self.level == 'T':
            try:
                year = self.year_set.latest('time')
                return Organization.SEMESTER_STATUS[self.status]\
                       + u' năm ' + year.__unicode__()
            except Exception:
                return Organization.SEMESTER_STATUS[0]
        else:
            return ''

    def get_active_students(self):
        return self.pupil_set.filter(unc_class_id=None,
                disable=False).distinct()

    def save_settings(self, attribute, value):
        if type(attribute) != str or (type(value) != str
            and type(value) != unicode and type(value) != int):
            raise Exception('InvalidArgumentType')
        try:
            setting_file_name = str(self.id)
            setting_file_name = os.path.join(SCHOOL_SETTING_FOLDER,
                                             setting_file_name)
        except Exception as e:
            print e
            raise Exception('OrganizationNotSaved')

        setting = MyConfigParser()
        try:
            file = codecs.open(setting_file_name, 'r', 'utf-8')
        except IOError:
            file = codecs.open(setting_file_name, 'wb', 'utf-8')
            file.close()
            file = codecs.open(setting_file_name, 'r', 'utf-8')
        setting.readfp(file)
        file.close()
        if not setting.has_section('school'):
            setting.add_section('school')
        setting.set('school', attribute, unicode(value))
        file = codecs.open(setting_file_name, 'wb', 'utf-8')
        setting.write(file)
        file.close()

    def get_setting(self, attribute):
        if type(attribute) != str:
            raise Exception('InvalidArgumentType')

        if self.id:
            setting_file_name = str(self.id)
            setting_file_name = os.path.join(SCHOOL_SETTING_FOLDER,
                                            setting_file_name)
        else:
            raise Exception('OrganizationNotSaved')

        setting = MyConfigParser()
        try:
            file = codecs.open(setting_file_name, 'r', 'utf-8')
            setting.readfp(file)
            result = setting.get('school', attribute)
        except  Exception as e:
            print e
            if attribute == 'lock_time':
                self.save_settings(attribute, 24)
                return 24
            else:
                self.save_settings(attribute, '')
                return ''
        try:
            if len(result) > 1 and result[0] == '[' and result[-1] == ']':
                return eval(result)
            else:
                if attribute == 'lock_time' and not result:
                    self.save_settings('lock_time', 24)
                    result = 24
                return result
        except Exception as e:
            print e
            return ''

    def __unicode__(self):
        return self.name

class OrganizationForm(forms.Form):
    name = forms.CharField(max_length=100) #tên đơn vị. tổ chức
    level = forms.CharField(max_length=2,
                            widget=forms.RadioSelect(
                            choices=ORGANIZATION_LEVEL_CHOICES)) #Cấp
    upper_organization = forms.ModelChoiceField(queryset=Organization.objects.all())
    address = forms.CharField(max_length=255) #
    phone = forms.CharField(max_length=20)
    email = forms.EmailField(max_length=50)

#class TruongnhaUser(User):
#    organization = models.ForeignKey(Organization, verbose_name='Đơn vị')
#    position = models.CharField(choices=POSITION_CHOICE, null=True, blank=True, max_length=15)
#    phone = models.CharField('Điện thoại di động', max_length=20, blank=True) #để gửi tin nhắn.
#    notes = models.CharField('Ghi chú', max_length=255, blank=True)
#    username_change = models.IntegerField(default=0)
#
#    @classmethod
#    def __init__(self, *args, **kw):
#        if 'user_profile' in kw: #this is for converting from UserProfile model
#            user_profile = kw.pop('user_profile')
#            self.organization = user_profile.organization
#            self.position = user_profile.position
#            self.phone = user_profile.phone
#            self.notes = user_profile.notes
#            self.username_change = user_profile.username_change
#        super(TruongnhaUser,self).__init__(*args, **kw)
#
#
#    @classmethod
#    def make_username(cls, first_name = None, last_name = None, full_name = None, start_year = None):
#        if full_name:
#            names = full_name.split(" ")
#            last_name = ' '.join(names[:len(names)-1])
#            #noinspection PyRedeclaration
#            first_name = names[len(names)-1]
#        last_name = unicodedata.normalize('NFKD', unicode(last_name)).encode('ascii','ignore').lower()
#        if first_name:
#            first_name = unicodedata.normalize('NFKD', unicode(first_name)).encode('ascii','ignore').lower()
#        else: raise Exception('FirstNameEmpty')
#        username = first_name
#        if last_name and last_name.strip() != '':
#            for word in last_name.split(" "):
#                if word: username += word[0]
#        if start_year:
#            username += '_' + str(start_year.time)
#        if len(username) > 28: username = username[:28]
#        i = 0
#        result = username
#        while User.objects.filter( username__exact = result):
#            i += 1
#            result = username + '_' + str(i)
#        return result
#
#    @classmethod
#    def make_default_password(cls, raw_password = None):
#        if not raw_password: raise Exception('BadParameter')
#        import random
#        algo = 'sha1'
#        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
#        hsh = get_hexdigest(algo, salt, raw_password)
#        password = '%s$%s$%s' % (algo, salt, hsh)
#        return password

class UserProfile(models.Model):
    """
    Thông tin về người sủ dụng hệ thống, mở rộng User của Django.
    """
    user = models.OneToOneField(User, null=True)
    organization = models.ForeignKey(Organization, verbose_name='Đơn vị')
    position = models.CharField(choices=POSITION_CHOICE, null=True,
                                blank=True, max_length=15)
    phone = models.CharField('Điện thoại di động', max_length=20,
                                blank=True) #để gửi tin nhắn.
    notes = models.CharField('Ghi chú', max_length=255, blank=True)
    username_change = models.IntegerField(default=0)

    def __unicode__(self):
        return self.user.__unicode__()
    def isSchool(self):
        if self.position =='GIAM_DOC_SO' or self.position=='TRUONG_PHONG':
            return False
        else:
            return True
class IP(models.Model):
    user = models.ForeignKey(User, null=True)
    ip = models.CharField('IP', max_length=20, unique=True, blank=False)
    failed_login = models.IntegerField('Số lần đăng nhập thất bại',
                                        default=0)

    @classmethod
    def recognize(cls, ip, user = None):
        try:
            instance = IP.objects.get(ip = ip)
            if user.is_anonymous():
                instance.failed_login += 1
                instance.save()
                if instance.failed_login > settings.LOGIN_FAILURE_LIMIT:
                    raise Exception('LoginFailureExceed')
        except ObjectDoesNotExist:
            IP.objects.create(ip = ip, user = user)
            return None

    @classmethod
    def reset(cls, ip):
        try:
            instance = IP.objects.get(ip = ip)
            instance.failed_login = 0
            instance.save()
        except ObjectDoesNotExist:
            IP.objects.create(ip = ip)

    @classmethod
    def exceed_failure_limit(cls, ip):
        try:
            instance = IP.objects.get(ip = ip)
            return instance.failed_login > settings.LOGIN_FAILURE_LIMIT
        except ObjectDoesNotExist:
            return False
    def __unicode__(self):
        return self.ip

class UserForm(forms.ModelForm):
    class Meta:
        model = UserProfile


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='Mật khẩu cũ',
                                    widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='Mật khẩu mới',
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Nhập lại mật khẩu mới',
                                    widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Xác nhận mật khẩu mới không \
                        chính xác. Hãy nhập lại.")
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Mật khẩu cũ không đúng.\
                    Hãy nhập lại.")
        return old_password

#ChangePasswordForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']

# quyendt
class AuthenticationForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30)
    password = forms.CharField(label="Password",
                               widget=forms.PasswordInput)
    login_type = forms.CharField(label="Login type",
                                 required=False, max_length=30)

    def __init__(self, request=None, api_called=False, *args, **kwargs):
        self.request = request
        self.api_called = api_called
        self.user_cache = None
        self.errors_type = None
        self.exceed_failure_limit = IP.exceed_failure_limit(request.META['REMOTE_ADDR'])
        if self.request.method == 'POST' and self.exceed_failure_limit and not api_called:
            self.recaptcha_challenge_field = self.request.POST['recaptcha_challenge_field']
            self.recaptcha_response_field = self.request.POST['recaptcha_response_field']
        super(AuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.exceed_failure_limit and not self.api_called:
            captcha_check = captcha.submit(
                self.recaptcha_challenge_field,
                self.recaptcha_response_field,
                settings.CAPTCHA_PRIVATE_KEY,
                self.request.META['REMOTE_ADDR']
            )
            if not captcha_check.is_valid:
                raise forms.ValidationError("Hai từ bạn điền không đúng.")
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        login_type = self.cleaned_data.get('login_type')
        if login_type in ['DEMO_LOGIN_SCHOOL', 'DEMO_LOGIN_TEACHER', 'DEMO_LOGIN_UPPER']:
            try:
                exec('self.user_cache = User.objects.get(username=settings.'+
                        login_type + ')')
                self.user_cache.backend = 'django.contrib.auth.backends.ModelBackend'
            except User.DoesNotExist:
                self.errors_type = 'wrong_demo_account'
                raise forms.ValidationError("Tài khoản dùng thử chưa được tạo.")
        else:
            if username and password:
                self.user_cache = authenticate(username=username, password=password)
                if self.user_cache is None:
                    self.errors_type = 'wrong_password'
                    raise forms.ValidationError("Hãy nhập đúng tên và mật khẩu và phân biệt chữ hoa, chữ thường.")
                elif not self.user_cache.is_active:
                    self.errors_type = 'deactivated'
                    raise forms.ValidationError("Tài khoản này đang bị khóa. Hãy liên hệ quản trị hệ thống.")
        self.check_for_test_cookie()

    def check_for_test_cookie(self):
        if self.user_cache and not self.user_cache.username in [settings.DEMO_LOGIN_SCHOOL,
                                                                settings.DEMO_LOGIN_TEACHER,
                                                                settings.DEMO_LOGIN_UPPER]:
            if self.request  and not self.request.session.test_cookie_worked():
                raise forms.ValidationError(
                    "Cookies của trình duyệt chưa được bật. Bạn cần phải bật cookies thì mới sử dụng được.")

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class Feedback(models.Model):
    """
    Thông tin về các bản báo cáo lỗi hay liên hệ từ khách hàng
    """
    fullname = models.CharField('Họ tên', blank=True, null=True, max_length=100)
    phone = models.CharField('Điện thoại', max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    title = models.CharField('Tiêu đề', blank=True, null=True, max_length=250)
    content = models.TextField('Nội dung', max_length=3000, blank=True)

    class Meta:
        verbose_name_plural = "Phản hồi"

    def __unicode__(self):
        return self.fullname


class FeedbackForm(forms.Form):
    #Hainhh    
    title = forms.CharField(label='Tiêu đề', max_length=250, required=True)
    content = forms.CharField(label='Nội dung', widget=forms.Textarea, required=False)
    fullname = forms.CharField(label='Họ tên', max_length=100, required=False)
    phone = forms.CharField(label='Điện thoại', max_length=15, required=False)
    email = forms.EmailField(label='Email', min_length=0, required=False)
    #    type = forms.CharField(label = 'Phân loại', widget = forms.RadioSelect(choices = CONTACT_CHOICES))

class Register(models.Model):
    register_name = models.CharField("Họ và tên", max_length=250, blank=False)
    register_phone= models.CharField("Số điện thoại", max_length=15, blank=True)
    register_email= models.CharField("Email", max_length=250, blank=False)
    school_name = models.CharField("Tên trường", max_length=250, blank=False)
    school_level = models.CharField(u"Khối học", max_length=6, blank=False, choices=KHOI_CHOICES)
    school_address = models.CharField(u"Địa chỉ", max_length=250, blank=True)
    school_province = models.CharField(u"Tỉnh/Thành phố", max_length=150, choices=TINH_CHOICES)
    status = models.CharField(u"Trạng thái", max_length=150, default='CHUA_CAP', choices=REGISTER_STATUS_CHOICES)
    register_date = models.DateField(u"Ngày đăng ký", default=date.today() )
    default_user_name = models.CharField(u'Tài khoản mặc định', max_length=250, blank=True)
    default_password = models.CharField(u'Mật khẩu mặc định', max_length=250, blank=True)
    def __unicode__(self):
        return '-'.join([unicode(self.register_name), unicode(self.school_name)])

class RegisterForm(forms.ModelForm):
    def save(self):
        super(RegisterForm, self).save()
        message = u'New Register:\nname:%s' % self.cleaned_data['register_name']
        send_email('New Register', message,
                to_addr=['vu.tran54@gmail.com', 'truonganhhoang@gmail.com'])
    class Meta:
        model = Register

class ResetPassword(models.Model):
    username = models.CharField(max_length=50)
    code = models.CharField(max_length=15)


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(label='Email của bạn', max_length=255)

class SystemLesson(models.Model):
    subject = models.IntegerField("Môn học", choices=SUBJECT_CHOICES, default=1)
    grade = models.IntegerField("Khối", choices=GRADES_CHOICES, default=6)
    term = models.IntegerField("Kì", choices=TERMS, default=1)
    index = models.IntegerField("Thứ tự", default = 0)
    title = models.TextField("Tên bài học", blank = True, null = True)
    note = models.TextField("Ghi chú", blank = True, null = True)
    ngay_day = models.DateField("Ngày dạy", blank = True, null = True)
    def __unicode__(self):
        return u' Môn ' + unicode(SUBJECT_CHOICES[int(self.subject)-1][1]) + u' khối ' + unicode(self.grade) + u' kì ' + unicode(self.term) + u' tiết ' + unicode(self.term)
class selectForm(forms.Form):
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES, label="Môn học", initial=1)
    grade = forms.ChoiceField(choices=GRADES_CHOICES, label ="Khối", initial=6)
    term = forms.ChoiceField(choices=TERMS, label ="Kì", initial=1)

