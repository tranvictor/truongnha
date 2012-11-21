# -*- coding: utf-8 -*-
import itertools, string
import random
import urllib2
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.urlresolvers import reverse

import validations
from sms.utils import sendSMS, send_email

GENDER = ((u'Nam', u'Nam'), (u'Nữ', u'Nữ'), (u'Khác', u'Khác'))

INITIAL_CONSONANTS = (set(string.ascii_lowercase)
        - set('aeiou')
        - set('qxcsjfw')
        | set('@#$%')
        | {'bl', 'br', 'cl', 'cr', 'dr', 'ch', 'gi', 'kh', 'ph',
            'pr', 'sk', 'ng', 'th', 'tr'})

FINAL_CONSONANTS = (set(string.ascii_lowercase)
        - set('aeiouxfjw')
        - set('qx')
        | set('@#$%')
        | {'ct', 'ft', 'mp', 'nd', 'ng', 'nk', 'nt', 'pt'})

VOWELS = 'aeiou' # we'll keep this simple

# each syllable is consonant-vowel-consonant "pronounceable"
syllables = map(''.join, itertools.product(INITIAL_CONSONANTS,
    VOWELS, FINAL_CONSONANTS))

class AbstractTeacherModel(models.Model):
    # Return url of an object following the RESTFUL convention
    def get_url(self, method, *args):
        return reverse('-'.join([self.__class__.__name__, method]),
                args=args)
    class Meta:
        abstract = True

REGISTER_STATUS_CHOICES = (('DA_CAP', u"Đã cấp"), ('CHUA_CAP', u"Chưa cấp"))
class Register(AbstractTeacherModel):
    name = models.CharField("Họ và tên",
            max_length=validations.FULL_NAME_MAX_LENGTH, blank=False)
    birthday = models.DateField("Ngày sinh",
            null=True, validators=[validations.birthday], blank=True)
    phone = models.CharField("Số điện thoại",
            validators=[validations.phone],
            max_length=validations.SMS_PHONE_MAX_LENGTH)
    email = models.EmailField("Email", blank=False,
            max_length=validations.USERNAME_MAX_LENGTH, unique=True)
    sex = models.CharField("Giới tính",
            max_length=validations.SEX_MAX_LENGTH,
            choices=GENDER, default='Nam')
    status = models.CharField(u"Trạng thái",
            max_length=validations.STATUS_MAX_LENGTH, default='CHUA_CAP',
            choices=REGISTER_STATUS_CHOICES)
    register_date = models.DateField(u"Ngày đăng ký", default=date.today())
    default_user_name = models.CharField(u'Tài khoản mặc định',
            max_length=validations.USERNAME_MAX_LENGTH, blank=True)
    default_password = models.CharField(u'Mật khẩu mặc định',
            max_length=validations.PASSWORD_MAX_LENGTH, blank=True)
    activation_key = models.CharField(max_length=validations.ACTIVATION_MAX_LENGTH)

    def __unicode__(self):
        return '-'.join([unicode(self.name), unicode(self.activation_key), unicode(self.email)])


class Person(AbstractTeacherModel):
    last_name = models.CharField("Họ",
            max_length=validations.LAST_NAME_MAX_LENGTH, blank=True)
    #vi phan nhap bang tay, ho ten se dc luu vao first_name
    #nen max_length phai dc tang len gap doi
    first_name = models.CharField("Tên",
            max_length=validations.FIRST_NAME_MAX_LENGTH)
    birthday = models.DateField("Ngày sinh",
            null=True, validators=[validations.birthday], blank=True)
    home_town = models.CharField("Quê quán",
            max_length=validations.HOME_TOWN_MAX_LENGTH, blank=True)
    sex = models.CharField("Giới tính",
            max_length=validations.SEX_MAX_LENGTH,
            choices=GENDER, default='Nam')
    sms_phone = models.CharField("Điện thoại",
            max_length=validations.SMS_PHONE_MAX_LENGTH, blank=True,
            validators=[validations.phone])
    current_address = models.CharField("Địa chỉ",
            max_length=validations.CURRENT_ADDRESS_MAX_LENGTH, blank=True)
    email = models.EmailField("Email",
            null=True, blank=True)
    index = models.IntegerField("Số thứ tự(*)",
            default=0)

    class Meta:
        abstract = True

    @classmethod
    def extract_fullname(cls, name):
        eles = [e.capitalize() for e in name.split(' ') if e]
        if not eles: raise Exception('BadName')
        firstname = eles[-1]
        lastname = ''
        if len(firstname) == 1 and len(eles)>=2:
            firstname = ' '.join(eles[-2:])
            lastname = ' '.join(eles[:-2])
        else:
            firstname = eles[-1]
            lastname = ' '.join(eles[:-1])
        return firstname, lastname

    def make_username(self):
        username = self.email.lower()
#        username = re.compile(r'\W+').sub('', username)
#        username = unicodedata.normalize('NFKD',
#                unicode(username)).encode('ascii','ignore').lower()
#        if len(username) > 28: username = username[:28]
        i = 0
        username1 = username
        while User.objects.filter(username__exact=username1):
            i += 1
            username1 = username + str(i)
        return username1

    def make_password(self, words=3, digits=2):
        max_number = 10 ** digits
        raw_password = ''.join(random.sample(syllables, words))
        if digits > 0:
            raw_password += str(int(random.random() * max_number))
        return raw_password

    def activate_account(self, words=3, digits=2):
        self.user.is_active = True
        raw_password = self.make_password()
        self.user.password = make_password(raw_password)
        if self.email or self.sms_phone:
            #Send Email
            email_sent = False
            sms_sent = False
            try:
                subject = u'Kích hoạt tài khoản Trường Nhà'
                message = u'Thông tin tài khoản tại: https://www.truongnha.com của bạn:\nTên đăng nhập: %s\nMật khẩu: %s\nXin cảm ơn.' % (unicode(self.user.username),
                                unicode(raw_password))
                send_email(subject, message, to_addr=[self.email])
                email_sent = True
            except Exception as e:
                print e
            try:
                content = 'Tai khoan Truongnha.com:\n\
                        Ten: %s\n\
                        Mat khau: %s\n\
                        Xin cam on.' % (self.user.username,
                                raw_password)
                sendSMS(self.sms_phone, content,
                        self.user, self.user,
                        save_to_db=False)
                sms_sent = True
            except Exception as e:
                print e
            if not email_sent and not sms_sent:
                raise Exception("NoWayToContact")
                #Send an SMS
        else:
            raise Exception("NoWayToContact")
        self.user.save()
        return raw_password

    def deactive_account(self):
        if self.user.is_active:
            self.user.is_active = False
            self.user.save()
        else:
            raise Exception("Already deactive")

    def full_name(self):
        return ' '.join([self.last_name, self.first_name])

    #This method return a short name to present a person's name
    #eg: Tran Huy Vu -> TH Vu
    def short_name(self):
        l = [''.join([w[0] for w in self.last_name.split(' ')]),
             self.first_name]
        return ' '.join(l)

    def __unicode__(self):
        return self.full_name()

class Teacher(Person):
    user = models.OneToOneField(User, verbose_name="Tài khoản",
            related_name='teachers')

    class Meta:
        verbose_name = "Giáo viên"
        verbose_name_plural = "Giáo viên"

class Class(AbstractTeacherModel):
    name = models.CharField("Tên lớp",
            max_length=validations.CLASS_NAME_MAX_LENGTH)
    index = models.IntegerField("Số thứ tự", default=0)
    created = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    cl_note = models.TextField("Ghi chú", blank=True)
    teacher_id = models.ForeignKey(Teacher, verbose_name="Giáo viên",
            null=True, blank=True)

    def teacher(self):
        if self.teacher_id:
            return unicode(self.teacher_id)
        else:
            return None

    def strip_name(self):
        return self.name.lower().replace(' ', '')

    def __unicode__(self):
        return self.name

    def quote_name(self):
        return urllib2.quote(self.name)

    def attended_student(self):
        students = self.student_set.all()
        return students

    #this function will return list of students those are studying in this class
    def students(self):
        return self.student_set.filter(attend__is_member=True)\
                .order_by('index').distinct()

    #this method return number of students those are studying in this class
    #Note: not include students those moved to other classes
    def number_of_students(self):
        try:
            return self.student_set.filter(attend__is_member=True)\
                    .order_by('index').distinct().count()
        except Exception:
            return 0

    #This function count number of students those didn't leave this class
    #because of course repetition or uncategorized.
    def number_of_staying_students(self):
        try:
            return self.student_set.filter(attend__leave_time=None).count()
        except Exception:
            return 0

    class Meta:
        verbose_name = "Lớp"
        verbose_name_plural = "Lớp"

class Student(Person):
    #thong tin gia dinh
    father_name = models.CharField("Họ và tên bố",
            max_length=validations.FULL_NAME_MAX_LENGTH, blank=True)
    father_phone = models.CharField("Điện thoại của bố",
            max_length=validations.SMS_PHONE_MAX_LENGTH,
            null=True, blank=True,
            validators=[validations.phone])
    mother_name = models.CharField("Họ và tên mẹ",
            max_length=validations.FULL_NAME_MAX_LENGTH, blank=True)
    mother_phone = models.CharField("Điện thoại của mẹ", max_length=15,
            null=True, blank=True,
            validators=[validations.phone])
    current_status = models.CharField("Tình trạng",
            max_length=200, blank=True, null=True, default='OK')

    user = models.OneToOneField(User, verbose_name="tài khoản",
            null=True, blank=True) 
    classes = models.ManyToManyField(Class,
            through="Attend", related_name='student_set')

    def get_attended_classes(self):
        classes = Class.objects.filter(pupil__id=self.id)
        return classes

    def get_attended(self):
        attended = Attend.objects.filter(pupil__id=self.id)
        return attended

    def first_class(self):
        attends = Attend.objects.filter(pupil=self).order_by('attend_time')
        if not attends:
            raise Exception('IllegalStudent')
        else:
            return attends[0]._class

    def current_class(self):
        attends = Attend.objects.filter(pupil=self, leave_time=None)
        if not attends:
            raise Exception('IllegalStudent')
        else:
            return attends[0]._class

    def disable_account(self):
        self.user.is_active = False
        self.user.save()

    class Meta:
        verbose_name = "Học sinh"
        verbose_name_plural = "Học sinh"

class Attend(AbstractTeacherModel):
    pupil = models.ForeignKey(Student, verbose_name=u"Học sinh")
    _class = models.ForeignKey(Class, verbose_name=u"Lớp")
    attend_time = models.DateTimeField("Thời gian nhập lớp")
    leave_time = models.DateTimeField("Thời gian rời lớp", null=True)
    is_member = models.BooleanField("Học xong lớp", default=True)
    #this field take value True when student is
    #member of this class that attend class till the end
    def get_class(self):
        return self._class

    def get_class_id(self):
        return self._class_id

    def history_check(self):
        mark = self.pupil.mark_set.all()
        for m in mark:
            if not m.current:
                if m.subject_id.class_id == self._class:
                    return True
        return False

    def __unicode__(self):
        return unicode(self.pupil) + '_' + unicode(self._class)

class Mark(AbstractTeacherModel):
    created = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    modified = models.DateTimeField("Thời gian sửa", auto_now=True)
    
    diem = models.FloatField("Điểm", null=True, blank=True,
            validators=[validations.mark])
    hs = models.FloatField("Hệ số",
            validators=[validations.hs])
    note = models.TextField("Ghi chú", blank=True)

    class_id = models.ForeignKey(Class, verbose_name="Lớp")
    student_id = models.ForeignKey(Student, verbose_name="Học sinh")

    class Meta:
        verbose_name = "Điểm"
        verbose_name_plural = "Điểm"
    def __unicode__(self):
        return unicode(self.diem) + u"_" + unicode(self.student_id) + u'_' + unicode(self.class_id)

class Note(AbstractTeacherModel):
    created = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    modified = models.DateTimeField("Thời gian sửa", auto_now=True)
    
    note = models.TextField("Ghi chú", blank=True)

    class_id = models.ForeignKey(Class, verbose_name="Lớp")
    student_id = models.ForeignKey(Student, verbose_name="Học sinh")

    class Meta:
        verbose_name = "Ghi chú"
        verbose_name_plural = "Ghi chú"

class Receivables(AbstractTeacherModel):
    name = models.CharField("Tên khoản thu",
            max_length=validations.RECEIVABLES_NAME_MAX_LENGTH)
    amount = models.FloatField("Số tiền", null=True, blank=True,
            validators=[validations.amount])
    deadline = models.DateField("Hạn", null=True, blank=True,
            validators=[validations.deadline])
    note = models.TextField("Ghi chú", blank=True)
    
    class_id = models.ForeignKey(Class, verbose_name="Lớp")

    class Meta:
        verbose_name = "Khoản thu"
        verbose_name_plural = "Khoản thu"

class Payment(AbstractTeacherModel):
    amount = models.FloatField("Số tiền", null=True, blank=True,
            validators=[validations.amount])
    note = models.TextField("Ghi chú", blank=True)
    receivables_id = models.ForeignKey(Class, verbose_name="Khoản thu")
    student_id = models.ForeignKey(Student, verbose_name="Học sinh")
    
    class Meta:
        verbose_name = "Khoản nộp"
        verbose_name_plural = "Khoản nộp"
