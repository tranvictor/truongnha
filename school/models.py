# -*- coding: utf-8 -*-
from datetime import date
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.query import QuerySet
from app.models import Organization, KHOI_CHOICES,\
    SUBJECT_CHOICES, GRADES_CHOICES, TERMS
from school.templateExcel import MAX_COL, normalize,\
    convertMarkToCharacter1
from sms.utils import sendSMS, send_email
import random, string
import itertools
import urllib2
from django.contrib.auth.hashers import make_password

LOAI_CHOICES = ((0, u'Tính cả 2 kỳ'), (1, u'Chỉ tính kì 1'),
                (2, u'Chỉ tính kì 2'), (3, u'Cộng vào điểm TB(NN2)'),
                (4, u'Không tính điểm'))
SUBJECT_TYPES = ((u'Toán', u'Toán'),
                 (u'Vật lí', u'Vật lí'), (u'Hóa học', u'Hóa học'),
                 (u'Sinh học', u'Sinh học'), (u'Ngữ văn', u'Ngữ văn'),
                 (u'Lịch sử', u'Lịch sử'), (u'Địa lí', u'Địa lí'),
                 (u'Ngoại ngữ', u'Ngoại ngữ'), (u'GDCD', u'GDCD'),
                 (u'Công nghệ', u'Công nghệ'), (u'Thể dục', u'Thể dục'),
                 (u'Âm nhạc', u'Âm nhạc'), (u'Mĩ thuật', u'Mĩ thuật'),
                 (u'NN2', u'NN2'), (u'Tin học', u'Tin học'),
                 (u'GDQP-AN', u'GDQP-AN'), (u'Tự chọn', u'Tự chọn'))
COMMENT_SUBJECT_LIST = [u'Âm nhạc', u'Mĩ thuật', u'Thể dục']
SUBJECT_LIST = [u'Toán', u'Vật lí', u'Hóa học', u'Sinh học', u'Ngữ văn',
                u'Lịch sử', u'Địa lí', u'Ngoại ngữ', u'GDCD', u'Công nghệ',
                u'Thể dục', u'Âm nhạc', u'Mĩ thuật', u'NN2', u'Tin học',
                u'GDQP-AN', u'Tự chọn']
SUBJECT_LIST_ASCII = [u'toan', u'vat li', u'hoa hoc', u'sinh hoc', u'ngu van',
                      u'lich su', u'dia li', u'ngoai ngu', u'gdcd', u'cong nghe',
                      u'the duc', u'am nhac', u'mi thuat', u'nn2', u'tin hoc',
                      u'gdqp-an', u'tu chon']
GENDER_CHOICES = ((u'Nam', u'Nam'), (u'Nữ', u'Nữ'),)
TERM_CHOICES = ((1, u'1'), (2, u'2'), (3, u'3'),)
HK_CHOICES = ((u'', u'Chưa xét'), (u'T', u'Tốt'), (u'K', u'Khá'),
              (u'TB', u'TB'), (u'Y', u'Yếu'),)
HL_CHOICES = ((u'G', u'Giỏi'), (u'K', u'Khá'), (u'TB', u'Trung Bình'),
              (u'Y', u'Yếu'), (u'Kem', u'Kém'))
DH_CHOICES = ((u'XS', u'Học sinh xuất sắc'), (u'G', u'Hoc sinh giỏi'),
              (u'TT', u'Học sinh tiên tiến'), (u'K', u'Không được gì'))
KT_CHOICES = ((u'Khen trước lớp', u'Khen trước lớp'),
              (u'Khen trước toàn trường', u'Khen trước toàn trường'),
              (u'Được tặng danh hiệu học sinh khá', u'Được tặng danh hiệu học sinh khá'),
              (u'Được tặng danh hiệu học sinh giỏi', u'Được tặng danh hiệu học sinh giỏi'),
              (u'Được ghi tên vào bảng danh dự của trường',
               u'Được ghi tên vào bảng danh dự của trường'),
              (u'Được tặng danh hiệu học sinh xuất sắc',
               u'Được tặng danh hiệu học sinh xuất sắc'),
              (u'Được khen thưởng đặc biệt', u'Được khen thưởng đặc biệt'))
KL_CHOICES = ((u'Khiển trách trước lớp', u'Khiển trách trước lớp'),
              (u'Khiển trách trước hội đồng kỷ luật', u'Khiển trách trước hội đồng kỷ luật'),
              (u'Cảnh cáo trước toàn trường', u'Cảnh cáo trước toàn trường'),
              (u'Đình chỉ học', u'Đình chỉ học'))
SCHOOL_LEVEL_CHOICE = ((1, u'1'), (2, u'2'), (3, u'3'))
DIEM_DANH_TYPE = ((u'', u'Đi học'), (u'P', u'nghỉ học có phép'),
                  (u'K', u'nghỉ học không phép'), (u'M', u'đi học muộn'),)
BAN_CHOICE = ((u'KHTN', u'Ban KHTN'), (u'KHXH', u'Ban KHXH-NV'),
              (u'CBA', u'Ban Cơ bản A'), (u'CBB', u'Ban Cơ bản B'),
              (u'CBB', u'Ban Cơ bản C'), (u'CBD', u'Ban Cơ bản D'),
              (u'CB', u'Ban Cơ bản'))
KHOI_CHOICE = ((1, u'Khối 1'), (2, u'Khối 2'), (3, u'Khối 3'),
               (4, u'Khối 4'), (5, u'Khối 5'), (6, u'Khối 6'), (7, u'Khối 7'),
               (8, u'Khối 8'), (9, u'Khối 9'), (10, u'Khối 10'), (11, u'Khối 11'),
               (12, u'Khối 12'))
KV_CHOICE = ((u'1', u'KV1'), (u'2A', 'KV2'), (u'2B', 'KV2-NT'), (u'3', u'KV3'))
DT_CHOICE = ((1, u'Kinh (Việt)'), (2, u'Tày'), (3, u'Nùng'), (4, u'Hmông (Mèo)'),
             (5, u'Mường'), (6, u'Dao'), (7, u'Khmer'), (8, u'Êđê'), (9, u'CaoLan'),
             (10, u'Thái'), (11, u'Gia rai'), (12, u'La chư'), (13, u'Hà nhì'), (14, u'Giáy'),
             (15, u"M'nông"), (16, u'Cơ tu'), (17, u'Xê đăng'), (18, u"X'tiêng"),
             (19, u"Ba na"), (20, "H'rê"), (21, u'Giê-Triêng'), (22, u'Chăm'),
             (23, u'Cơ ho'), (24, u'Mạ'), (25, u'Sán Dìu'), (26, u'Thổ'),
             (27, u'Khơ mú'), (28, u'Bru - Vân Kiều'), (29, u'Tà ôi'),
             (30, u'Co'), (31, u'Lào'), (32, u'Xinh mun'), (33, u'Chu ru'),
             (35, u'Phù lá'), (36, u'La hú'), (37, u'Kháng'), (38, u'Lự'),
             (39, u'Pà Thén'), (40, u'Lô lô'), (41, u'Chứt'), (42, u'Mảng'),
             (43, u'Cơ lao'), (44, u'Bố y'), (45, u'La ha'), (46, u'Cống'),
             (47, u'Ngái'), (48, u'Si la'), (49, u'Pu Péo'), (50, u'Brâu'),
             (51, u'Rơ măm'), (52, u'Ơ đu'), (53, u'Hoa'), (54, u'Raglay'),
             (55, u'HMông'), (56, u'Pacô'), (57, u'Pahy'), (60, u'Jơ lơng'),
             (61, u'Rơ ngao'), (62, u'Ra dong'), (63, u'Sơ rá'), (64, u'Jẻ'),
             (65, u'Mơ nâm'), (66, u'Hơ lăng'), (67, u'Hoa (Hán)'), (68, u'Sán chay'),
             (69, u'CaDong'), (70, u'Chơ ro'))
LENLOP_CHOICES = ((True, u'Được lên lớp'), (False, u'Không được lên lớp'))
SCHOOL_ACTION_STATUS = ((0, u'Trường mới'), (1, u'Đang học kỳ 1'),
                        (2, u'Đang học kỳ 2'), (3, u'Đang nghỉ hè'))
CLASS_ACTION_STATUS = ((1, u'Đang học kỳ 1'), (2, u'Đang học kỳ 2'),
                       (3, u'Đang nghỉ hè'))
ACTIVE_CHOICES = ((True, u'Đang diễn ra'), (False, u'Đã kết thúc'))
LEARNING_STATUS_CHOICES = ((u'TN', u'Tốt nghiệp'), (u'LB', u'Lưu ban'),
                           (u'LL', u'Lên lớp'))

DAY_CHOICE = ((2, u'Thu 2'), (3, u'Thu 3'), (4, u'Thu 4'),
              (5, u'Thu 5'), (6, u'Thu 6'), (7, u'Thu 7'))

GRADES_CHOICES2 = ((6, u'Lớp 6'), (7, u'Lớp 7'), (8, u'Lớp 8'),
                   (9, u'Lớp 9'))

GRADES_CHOICES3 = ((10, u'Lớp 10'), (11, u'Lớp 11'), (12, u'Lớp 12'))

INITIAL_CONSONANTS = (set(string.ascii_lowercase)
                      - set('aeiou')
                      - set('qxcsjfw')
                      | set('@#$%')
                      | {'bl', 'br', 'cl', 'cr', 'dr', 'ch', 'gi', 'kh', 'ph',
                         'pr', 'sk', 'ng', 'th', 'tr'})

FINAL_CONSONANTS = (set(string.ascii_lowercase)
                    - set('aeiouxfjw')
                    | set('@#$%')
- set('qx')
                    | {'ct', 'ft', 'mp', 'nd', 'ng', 'nk', 'nt', 'pt'})

VOWELS = 'aeiou' # we'll keep this simple

# each syllable is consonant-vowel-consonant "pronounceable"
syllables = map(''.join,
    itertools.product(INITIAL_CONSONANTS,
        VOWELS,
        FINAL_CONSONANTS))

def this_year():
    return int(date.today().year)


def validate_class_label(value):
    if not value.strip():
        raise ValidationError(u'Bạn chưa nhập danh sách tên lớp.')


def validate_mark(value):
    if value < 0 or value > 10:
        raise ValidationError(u'Điểm phải nằm trong khoảng từ 0 đến 10.')

#validate the phone format
def validate_phone(value):
    if len(value) <= 5:
        raise ValidationError(u'Điện thoạt phải có trên 5 chữ số.')
    try:
        int(value)
    except ValueError:
        raise ValidationError(u'Không đúng định dạng.')

#validate birthday. set range between 1990 and current year
def validate_birthday(value):
    if value < date(1900, 1, 1) or value > date.today():
        raise ValidationError(u'Ngày nằm ngoài khoảng cho phép.')

#validate the year that pupil go to class 1. Ragne between 1990 and this year
def validate_year(value):
    if value < 1990 or value > date.today().year:
        raise ValidationError(u'Năm nằm ngoài khoảng cho phép.')

#validate the date that pupil join school
def validate_join_date(value):
    if value < date(1990, 1, 1) or value > date.today():
        raise ValidationError(u'Ngày nằm ngoài khoảng cho phép.')


def validate_dd_date(value):
    if value > date.today():
        raise ValidationError(u'Ngày nẳm ngoài khoảng cho phép.')

#validate he so diem cua mon
def validate_hs(value):
    #he so bang 0 la cho nhung mon cham diem bang nhan xet
    if value < 0:
        raise ValidationError(u'Hệ số không được nhỏ hơn 0.')
    if value > 3:
        raise ValidationError(u'Hệ số không được lớn hơn 3.')


def validate_numberLesson(value):
    #he so bang 0 la cho nhung mon cham diem bang nhan xet
    if value < 0:
        raise ValidationError(u'Số tiết trong một tuần không được nhỏ hơn 0.')
    if value > 10:
        raise ValidationError(u'Số tiết trong một tuần không được lớn hơn 10.')


def validate_join_mark(value):
    if value <= 0:
        raise ValidationError(u'Điểm nhập trường phải lớn hơn 0.')
    if value >= 55:
        raise ValidationError(u'Điểm nhập trường phải nhỏ hơn 55.')


def validate_hs_luong(value):
    if value <= 0 or value > 13:
        raise ValidationError(u'Hệ số nằm ngoài khoảng cho phép.')


def validate_muc_luong(value):
    if value <= 0:
        raise ValidationError(u'Mức lương phải lớn hơn 0.')


def validate_num(value):
    try:
        int(value)
    except:
        raise ValidationError(u'Định dạng không đúng.')


def log_action(request, object, change_message):
    """
    Log an entry to Django admin's log
    """
    from django.contrib.admin.models import LogEntry
    from django.contrib.contenttypes.models import ContentType

    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get_for_model(object).pk,
        object_id=object.pk,
        # Message you want to show in admin action list
        object_repr=change_message,
        # I used same
        change_message="app-log",
        action_flag=4
    )


class DanhSachLoaiLop(models.Model):
    loai = models.CharField("Loại", max_length=15)
    school_id = models.ForeignKey(Organization, verbose_name="Trường")

    class Meta:
        verbose_name = "Danh sách loại lớp"
        verbose_name_plural = "Danh sách loại lớp"

    def __unicode__(self):
        return self.loai

        #cac khoi trong 1 truong


class Block(models.Model):
    number = models.SmallIntegerField("Khối(*)",
        max_length=2, choices=KHOI_CHOICES)
    school_id = models.ForeignKey(Organization, verbose_name="Trường(*)")

    class Meta:
        verbose_name = "Khối"
        verbose_name_plural = "Khối"

    def __unicode__(self):
        return str(self.number)


class Team(models.Model):
    name = models.CharField("Tổ",
        max_length=30)
    school_id = models.ForeignKey(Organization, verbose_name="Trường(*)")

    class Meta:
        verbose_name = "Tổ"
        verbose_name_plural = "Tổ"

    def number_of_group(self):
        return len(self.group_set.all())

    def __unicode__(self):
        return unicode(self.name)


class Group(models.Model):
    name = models.CharField("Nhóm", max_length=30)
    team_id = models.ForeignKey(Team, verbose_name="Tổ(*)")

    class Meta:
        verbose_name = "Nhóm"
        verbose_name_plural = "Nhóm"

    def __unicode__(self):
        return unicode(self.name)


class BasicPersonInfo(models.Model):
    # tach ra first_name and last_name de sort va import from excel file
    last_name = models.CharField("Họ",
        max_length=35, blank=True)
    #vi phan nhap bang tay, ho ten se dc luu vao first_name
    #nen max_length phai dc tang len gap doi
    first_name = models.CharField("Tên(*)",
        max_length=55)
    birthday = models.DateField("Ngày sinh(*)",
        null=True, validators=[validate_birthday])
    birth_place = models.CharField("Nơi sinh",
        max_length=200, blank=True)
    dan_toc = models.CharField("Dân tộc",
        max_length=15, blank=True, default='Kinh')
    ton_giao = models.CharField("Tôn giáo",
        max_length=20, blank=True)
    quoc_tich = models.CharField("Quốc tịch",
        max_length=20, blank=True, default='Việt Nam')
    home_town = models.CharField("Quê quán",
        max_length=100, blank=True)
    sex = models.CharField("Giới tính(*)",
        max_length=3, choices=GENDER_CHOICES, default='Nam')
    phone = models.CharField("Điện thoại",
        max_length=15, blank=True, validators=[validate_phone])
    sms_phone = models.CharField("Điện thoại nhận tin nhắn",
        max_length=15, blank=True, validators=[validate_phone])
    current_address = models.CharField("Địa chỉ",
        max_length=200, blank=True)
    email = models.EmailField("Email",
        null=True, blank=True)
    index = models.IntegerField("Số thứ tự(*)",
        default=0)
    note = models.TextField("Ghi chú",
        blank=True)

    class Meta:
        abstract = True

    def activate_account(self, words=3, digits=2):
        self.user_id.is_active = True
        max_number = 10 ** digits
        raw_password = ''.join(random.sample(syllables, words))
        if digits > 0:
            raw_password += str(int(random.random() * max_number))
        self.user_id.password = make_password(raw_password)
        if self.email or self.sms_phone:
            #Send Email
            email_sent = False
            sms_sent = False
            try:
                subject = u'Kích hoạt tài khoản Trường Nhà'
                message = u'''Tài khoản trường %s tại địa chỉ: \
                        https://www.truongnha.com của bạn là:\n\
                        Tên đăng nhập: %s\n Mật khẩu: %s\n\
                        Xin cảm ơn.''' % (unicode(self.school_id),
                        unicode(self.user_id.username),
                        unicode(raw_password))
                send_email(subject, message, to_addr=[self.email])
                email_sent = True
            except Exception as e:
                print e
            try:
                content = '''Tai khoan Truongnha.com:\n\
                        Ten: %s\n\
                        Mat khau: %s\n\
                        Xin cam on.''' % (self.user_id.username,
                                raw_password)
                sendSMS(self.sms_phone, content,
                        self.user_id, self.user_id,
                        save_to_db=False,
                        school=self.school_id)
                sms_sent = True
            except Exception as e:
                print e
            if not email_sent and not sms_sent:
                raise Exception("NoWayToContact")
                #Send an SMS
        else:
            raise Exception("NoWayToContact")
        self.user_id.save()
        return raw_password

    def deactive_account(self):
        if self.user_id.is_active:
            self.user_id.is_active = False
            self.user_id.save()
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
        return self.last_name + " " + self.first_name

        #class Admin: pass


class Teacher(BasicPersonInfo):
    major = models.CharField("Dạy môn(*)",
        max_length=45, default='', blank=True,
        choices=SUBJECT_TYPES)
    cmt = models.CharField("Chứng minh thư",
        null=True, blank=True, max_length=10,
        validators=[validate_num])
    ngay_cap = models.DateField("Ngày cấp",
        null=True, blank=True,
        validators=[validate_dd_date])
    noi_cap = models.CharField("Nơi cấp",
        null=True, blank=True, max_length=30)
    ngay_vao_doan = models.DateField("Ngày vào đoàn",
        null=True, blank=True,
        validators=[validate_dd_date])
    ngay_vao_dang = models.DateField("Ngày vào đảng",
        null=True, blank=True,
        validators=[validate_dd_date])
    muc_luong = models.IntegerField("Mức lương",
        null=True, blank=True,
        validators=[validate_muc_luong])
    hs_luong = models.FloatField("Hệ số lương",
        null=True, blank=True,
        validators=[validate_hs_luong])
    bhxh = models.CharField("Số bảo hiểm xã hội",
        null=True, blank=True,
        max_length=10, validators=[validate_num])

    user_id = models.OneToOneField(User, verbose_name="Tài khoản")
    school_id = models.ForeignKey(Organization, verbose_name="Trường")
    group_id = models.ForeignKey(Group, verbose_name="Nhóm",
        null=True, blank=True, on_delete=models.SET_NULL)
    team_id = models.ForeignKey(Team, verbose_name="Tổ",
        null=True, blank=True, on_delete=models.SET_NULL)

    def homeroom_class(self):
        _class = Class.objects.filter(teacher_id=self).order_by('-year_id__time')
        if _class: return _class
        else: return None

    def lastest_homeroom_class(self):
        classes = Class.objects.filter(teacher_id=self).order_by('-year_id__time')
        if classes:
            return classes[0]
        else:
            return None

    def current_homeroom_class(self):
        current_year = self.school_id.get_current_year()
        classes = Class.objects.filter(
            teacher_id=self,
            year_id=current_year).order_by('-year_id__time')
        if classes:
            return classes[0]
        else:
            return None

    def current_teaching_class(self):
        year = Year.objects.filter(school_id=self.school_id).latest('time')
        if not year: raise Exception("SchoolNotStarted")
        subjects = Subject.objects.filter(teacher_id=self)\
        .filter(class_id__year_id=year, class_id__school_id=self.school_id)
        return [subject.class_id for subject in subjects]

    def teaching_subject(self, year=None):
        if year: subjects = Subject.objects.filter(teacher_id=self,
            class_id__year_id=year)
        else: subjects = Subject.objects.filter(teacher_id=self)
        return subjects

    def disable_account(self):
        self.user_id.is_active = False
        self.user_id.save()
        try:
            subject = u'Vô hiệu hóa tài khoản Trường Nhà'
            message = u'Tài khoản tại dịch vụ Trường nhà (www.truongnha.com) đã bị vô hiệu hóa bởi nhân viên quản trị\
            trường' + unicode(self.school_id) + u'\n' + u'\n' + u'Xin cảm ơn.'
            send_email(subject, message, to_addr=[self.email])
        except Exception as e:
            print e
        try:
            content = 'Tai khoan Truongnha.com cua ban da vi vo hieu hoa.'
            sendSMS(self.sms_phone, content, self.user_id)
        except Exception as e:
            print e
            #Send an SMS

    class Meta:
        verbose_name = "Giáo viên"
        verbose_name_plural = "Giáo viên"
        unique_together = ("school_id", "first_name", "last_name", "birthday",)


class Year(models.Model):
    # date field but just use Year
    time = models.IntegerField("Năm",
        max_length=4, validators=[validate_year])
    school_id = models.ForeignKey(Organization, verbose_name="Trường")

    class Meta:
        verbose_name = "Năm học"
        verbose_name_plural = "Năm học"

    def __unicode__(self):
        return str(self.time) + "-" + str(self.time + 1)


class StartYear(models.Model):
    # date field but just use Year
    time = models.IntegerField("Năm",
        max_length=4, validators=[validate_year])
    school_id = models.ForeignKey(Organization)

    class Meta:
        verbose_name = "Khóa"
        verbose_name_plural = "Khóa"

    def __unicode__(self):
        return str(self.time)


class Term(models.Model):
    number = models.IntegerField("Kì",
        max_length=1, choices=TERM_CHOICES)
    # neu active =false thi khong cho phep sua diem nua
    year_id = models.ForeignKey(Year, verbose_name="Năm học")

    class Meta:
        verbose_name = "Kì"
        verbose_name_plural = "Kì"

    def __unicode__(self):
        return str(self.number) + " " + str(self.year_id)
        #class Admin: pass

#Lop chua cac hoc sinh chua dc phan lop.
class UncategorizedClass(models.Model):
    name = models.CharField("Tên lớp(*)", max_length=50)
    year_id = models.ForeignKey(Year, verbose_name="Năm học(*)")
    #lop nay thuoc khoi nao
    block_id = models.ForeignKey(Block, verbose_name="Khối(*)")

    def number_of_students(self):
        return self.pupil_set.count()

    def students(self):
        return self.pupil_set.all()

    def __unicode__(self):
        return self.name


class Class(models.Model):
    name = models.CharField("Tên lớp(*)", max_length=20)
    index = models.IntegerField("Số thứ tự", default=0)
    phan_ban = models.CharField("Phân ban", max_length=5,
        choices=BAN_CHOICE, default=u'CB', null=True)
    max = models.IntegerField("Max student index", default=0, null=True)
    status = models.SmallIntegerField("Tình trạng",
        max_length=3, null=True, blank=True, choices=CLASS_ACTION_STATUS)

    year_id = models.ForeignKey(Year, verbose_name="Năm học(*)")
    block_id = models.ForeignKey(Block, verbose_name="Khối(*)")
    teacher_id = models.ForeignKey(Teacher, verbose_name="Giáo viên chủ nhiệm",
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

    #this method return pair dict {id:  [mark, mark, ...]}, student query set
    #Return: {id: [mark, mark, ...]}, student query set
    def _mark_for_students(self, subject, term, student_query=None):
        # if query set is fetched or defined (will be cached)
        # use it instead of making another query that hits db one more time
        if student_query: sts = student_query
        else: sts = self.students()
        #if a queryset of Subject is provided
        if isinstance(subject, QuerySet):
        # get list of marks of all provided subjects
            marks = Mark.objects.filter(subject_id__in=subject, term_id=term,
                student_id__in=sts)
        else:
            marks = Mark.objects.filter(subject_id=subject, term_id=term,
                student_id__in=sts)
            # use dictionary for attaching marks to student to get
        # benefits of dictionary low searching average complexity O(1).
        # Overal match complexity: O(n)
        result = {}
        for m in marks:
            sid = m.student_id_id
            if sid in result: result[sid].append(m)
            else: result[sid] = [m]
        return result, sts

    #this method return pair dict {id:  [tkmon, tkmon, ...]}, student query set
    #Return: {id: [tkmon, tkmon, ...]}, student query set
    def _tkmon_for_students(self, subject, student_query=None):
        # if query set is fetched or defined (will be cached)
        # use it instead of making another query that hits db one more time
        if student_query: sts = student_query
        else: sts = self.students()
        #if a queryset of Subject is provided
        if isinstance(subject, QuerySet):
        # get list of tkmons of all provided subjects
            tkmons = TKMon.objects.filter(subject_id__in=subject,
                student_id__in=sts)
        else:
            tkmons = TKMon.objects.filter(subject_id=subject,
                student_id__in=sts)
            # use dictionary for attaching marks to student to get
        # benefits of dictionary low searching average complexity O(1).
        # Overal match complexity: O(n)
        result = {}
        for tk in tkmons:
            sid = tk.student_id_id
            result[sid] = tk if sid in result else [tk]
        return result, sts

    #this method return a pair of list of string that contain all the new
    #information about marks of students in the class, student query set and
    #subject query set
    #Note: new information means that the information hasn't been sent to
    #user
    #Return: {student_id: str}, student query set, subjects
    #TODO: Consider the case to promote TKMON
    def _generate_mark_summary(self, term, student_query=None):
        # if query set is fetched or defined (will be cached)
        # use it instead of making another query that hits db one more time
        if student_query: sts = student_query
        else: sts = self.students()
        #fectch subjects
        subjects = self.subject_set.all()
        subject_dict = {}
        for s in subjects:
            subject_dict[s.id] = s
        marks, temp = self._mark_for_students(subjects,
            term,
            student_query=sts)
        result = {}
        for ele in marks.items():
            sid = ele[0]
            m_list = ele[1]
            content = [u'Điểm mới:']
            for m in m_list:
                #get subject from subject list that already fetched
                #instead of making new query that hit db in this way:
                #subject = m.subject_id
                subject = subject_dict[m.subject_id_id]
                summ_m = m.new_summary(subject=subject)
                if summ_m:
                    content.append(u'%s:%s' % (subject.short_name(),
                                               summ_m))
            if len(content) == 1: result[sid] = u'Không có điểm mới'
            else: result[sid] = '\n'.join(content)
        return result, sts, marks

    #this method return number of students those are studying in this class
    #Note: not include students those moved to other classes
    def number_of_pupils(self):
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

    def associated_teacher(self):
        subjects = Subject.objects.filter(class_id=self)
        result = [subject.teacher_id for subject in subjects]
        result.append(self.teacher_id)
        return result

    class Meta:
        verbose_name = "Lớp"
        verbose_name_plural = "Lớp"
        unique_together = ("year_id", "name")
        #class Admin: pass


class Pupil(BasicPersonInfo):
    year = models.IntegerField("Năm học lớp 1",
        validators=[validate_year], blank=True, null=True)
    #year that pupil go to class 1

    school_join_date = models.DateField("Ngày nhập trường(*)",
        default=date.today(),
        validators=[validate_join_date])
    ban_dk = models.CharField("Ban đăng kí(*)", max_length=5,
        choices=BAN_CHOICE, default=u'CB')
    school_join_mark = models.IntegerField("Điểm tuyển sinh",
        null=True, blank=True,
        validators=[validate_join_mark])
    learning_status = models.CharField("Tình trạng học tập",
        max_length=20, blank=True,
        choices=LEARNING_STATUS_CHOICES)

    #thong tin ca nhan
    khu_vuc = models.CharField("Khu vực", max_length=3,
        choices=KV_CHOICE, blank=True)
    doi = models.BooleanField("Là đội viên", blank=True,
        default=False)
    ngay_vao_doi = models.DateField("Ngày vào đội", blank=True,
        null=True, validators=[validate_dd_date])
    doan = models.BooleanField("Là đoàn viên", blank=True, default=False)
    ngay_vao_doan = models.DateField("Ngày vào đoàn", blank=True,
        null=True, validators=[validate_dd_date])
    dang = models.BooleanField("Là đảng viên", blank=True, default=False)
    ngay_vao_dang = models.DateField("Ngày vào đảng", blank=True, null=True,
        validators=[validate_dd_date])
    uu_tien = models.CharField("Ưu tiên", blank=True, max_length=100)

    #thong tin gia dinh
    father_name = models.CharField("Họ và tên bố", max_length=45, blank=True)
    father_birthday = models.DateField("Ngày sinh của bố", null=True,
        blank=True, validators=[validate_birthday])
    father_phone = models.CharField("Điện thoại của bố", max_length=15,
        null=True, blank=True,
        validators=[validate_phone])
    father_job = models.CharField("Nghê nghiệp của bố",
        max_length=100, blank=True)
    mother_name = models.CharField("Họ và tên mẹ",
        max_length=45, blank=True)
    mother_birthday = models.DateField("Ngày sinh của mẹ",
        null=True, blank=True, validators=[validate_birthday])
    mother_job = models.CharField("Nghê nghiệp của mẹ", max_length=100,
        blank=True)
    mother_phone = models.CharField("Điện thoại của mẹ", max_length=15,
        null=True, blank=True, validators=[validate_phone])

    current_status = models.CharField("Tình trạng",
        max_length=200, blank=True, null=True, default='OK')
    disable = models.BooleanField("Không còn trong trường", default=False)

    user_id = models.OneToOneField(User, verbose_name="tài khoản",
        null=True, blank=True) # nullable is temporary

    start_year_id = models.ForeignKey(StartYear, verbose_name="khóa")
    class_id = models.ForeignKey(Class, verbose_name="lớp",
        null=True, blank=True)
    school_id = models.ForeignKey(Organization, verbose_name="trường",
        null=True, blank=True)
    classes = models.ManyToManyField(Class,
        through="Attend", related_name='student_set')
    unc_class_id = models.ForeignKey(UncategorizedClass,
        verbose_name=u'Chưa phân lớp', null=True, blank=True)

    def get_attended_classes(self):
        classes = Class.objects.filter(pupil__id=self.id)
        return classes

    def get_attended(self):
        attended = Attend.objects.filter(pupil__id=self.id)
        return attended

    def first_class(self):
        attends = Attend.objects.filter(pupil=self).order_by('attend_time')
        if not attends:
            pass
        else:
            return attends[0]._class

    def current_class(self):
        attends = Attend.objects.filter(pupil=self, leave_time=None)
        if not attends:
            #print classes
            #raise Exception('InvalidClassSet_%s' % self.id)
            pass
        else:
            return attends[0]._class

    def graduate(self):
        attends = Attend.objects.filter(pupil=self, leave_time=None)
        if not attends:
            #print classes
            #raise Exception('InvalidClassSet_%s' % self.id)
            pass
        else:
            self.unc_class_id = None
            self.save()
            attends[0].leave_time = date.today()
            attends[0].save()
            self.disable = True
            self.save()

    def join_class(self, _class, time=None):
        if not time:
            time = date.today()
        current = self.current_class()
        try:
            if current:
                relationship = Attend.objects.filter(pupil=self,
                    _class=current,
                    leave_time=None)
                if len(relationship) == 1:
                    if current != _class:
                        relationship[0].leave_time = date.today()
                        if current.year_id == _class.year_id:
                            relationship[0].is_member = False
                        relationship[0].save()
                        Attend.objects.create(pupil=self,
                            _class=_class,
                            attend_time=time,
                            leave_time=None)
                        self.index = _class.max + 1
                        _class.max += 1
                        _class.save()
                        self.class_id = _class
                        self.learning_status = ''
                        self.unc_class_id = None
                        self.save()
                elif not relationship:
                    Attend.objects.create(pupil=self,
                        _class=_class,
                        attend_time=time,
                        leave_time=None)
                    self.class_id = _class
                    self.index = _class.max + 1
                    self.learning_status = ''
                    self.unc_class_id = None
                    _class.max += 1
                    _class.save()
                    self.save()
                else:
                    raise Exception(u'InvalidClassSet_%s' % self.id)
            else:
                #this only use for converting from 1n to nm
                #TODO delete this section after removing class_id
                Attend.objects.create(pupil=self,
                    _class=_class,
                    attend_time=time,
                    leave_time=None)
                self.class_id = _class
                self.index = _class.max + 1
                _class.max += 1
                _class.save()
                self.save()
            return self
        except Exception as e:
            print e
            raise e

    def _move_to_class(self, _class):
        year = _class.year_id
        TBNam.objects.get_or_create(student_id=self,
            year_id=year)
        subjects = _class.subject_set.all()
        number_subject = 0
        number_subject += _class.subject_set.filter(primary=0).count()
        number_subject += _class.subject_set.filter(primary=3).count()

        for t in year.term_set.all():
            if t.number == 1:
                number_subject = _class.subject_set.filter(primary=1).count()
            elif t.number == 2:
                number_subject = _class.subject_set.filter(primary=2).count()
            TBHocKy.objects.get_or_create(student_id=self,
                term_id=t,
                number_subject=number_subject)
            TKDiemDanh.objects.get_or_create(student_id=self, term_id=t)
        for subject in subjects:
            for i in range(1, 3):
                term1 = year.term_set.get(number__exact=i)
                Mark.objects.get_or_create(student_id=self,
                    subject_id=subject,
                    term_id=term1)

            TKMon.objects.get_or_create(student_id=self,
                subject_id=subject)
        self.join_class(_class)
        return self

    def move_to_new_class(self, _class):
        return self._move_to_class(_class)

        # This method is rarely used, it moves a student to an upper class
    # in the same year, this short of action usually illegal
    def _move_to_upper_class(self, _class):
        cur_cl = self.current_class()
        Mark.objects.filter(subject_id__class_id=cur_cl, student_id=self)\
        .update(current=False)
        self.tkmon_set.filter(subject_id__class_id=cur_cl)\
        .update(current=False)
        return self._move_to_class(_class)

    def get_school(self):
        return self.school_id

    def disable_account(self):
        self.user_id.is_active = False
        self.user_id.save()

    class Meta:
        verbose_name = "Học sinh"
        verbose_name_plural = "Học sinh"
        unique_together = ("class_id", "first_name", "last_name", "birthday",)


class Attend(models.Model):
    pupil = models.ForeignKey(Pupil, verbose_name=u"Học sinh")
    _class = models.ForeignKey(Class, verbose_name=u"Lớp")
    attend_time = models.DateTimeField("Thời gian nhập lớp")
    leave_time = models.DateTimeField("Thời gian rời lớp", null=True)
    is_member = models.BooleanField("Học xong lớp", default=True)
    #this field take value True when student is
    #member of this class that attend class till the end
    def get_class(self):
        return self._class

    def get_class_id(self):
        return self._class.id

    def history_check(self):
        mark = self.pupil.mark_set.all()
        for m in mark:
            if not m.current:
                if m.subject_id.class_id == self._class:
                    return True
        return False

    def __unicode__(self):
        return unicode(self.pupil) + '_' + unicode(self._class)


class Subject(models.Model):
    name = models.CharField("Tên môn học(*)", max_length=45) # can't be null
    type = models.CharField("Môn(*)", max_length=45, default='', choices=SUBJECT_TYPES)
    hs = models.FloatField("Hệ số(*)", validators=[validate_hs], default=1)
    nx = models.BooleanField("Là môn nhận xét", default=False)

    primary = models.SmallIntegerField("Tính điểm(*)", default=0, choices=LOAI_CHOICES)
    index = models.IntegerField("Số thứ tự(*)", default=0)
    number_lesson = models.IntegerField("Số tiết một tuần",
        validators=[validate_numberLesson], default=0)
    max = models.IntegerField("Số tiết", default=0)
    class_id = models.ForeignKey(Class, verbose_name="Lớp(*)")
    teacher_id = models.ForeignKey(Teacher, verbose_name="Giáo viên",
        null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Môn"
        verbose_name_plural = "Môn"
        unique_together = ("name", "class_id")

    def __unicode__(self):
        return self.name

    def strip_name(self):
        return self.name.lower().replace(' ', '')

    def get_primary(self):
        return LOAI_CHOICES[self.primary][1].encode("UTF-8")

    def short_name(self):
        name_dict = {
            u'Toán': 'Toan',
            u'Vật lí': 'Ly',
            u'Hóa học': 'Hoa',
            u'Sinh học': 'Sinh',
            u'Ngữ văn': 'Van',
            u'Lịch sử': 'Su',
            u'Địa lí': 'Dia',
            u'Ngoại ngữ': 'NNgu',
            u'GDCD': 'GDCD',
            u'Công nghệ': 'CNghe',
            u'Thể dục': 'TDuc',
            u'Âm nhạc': 'Nhac',
            u'Mĩ thuật': 'MThuat',
            u'NN2': 'NNgu2',
            u'Tin học': 'Tin',
            u'Tự chọn': 'TC',
            u'GDQP-AN': 'QPhong'}
        if self.type in name_dict: return name_dict[self.type]
        else: return 'TC'

    def get_mark_list(self, term_id):
        return Mark.objects.filter(term_id=term_id,
            subject_id=self,
            current=True).order_by('student_id__index',
            'student_id__first_name', 'student_id__last_name',
            'student_id__birthday')
        #class Admin: pass


class Mark(models.Model):
    diem = models.CharField("điểm", null=True, blank=True,
        default='||', max_length=100)
    sent = models.CharField("Đã gửi", null=True, blank=True,
        default='||||', max_length=50)
    time = models.CharField("Thời gian tạo", null=True, blank=True,
        default='||||', max_length=200)
    ck = models.FloatField("Điểm thi cuối kì", null=True, blank=True,
        validators=[validate_mark])
    mg = models.BooleanField("Miễn giảm", default=False)
    tb = models.FloatField("Điểm trung bình", null=True, blank=True,
        validators=[validate_mark])
    note = models.TextField("Ghi chú", blank=True)

    current = models.BooleanField("Thuộc lớp hiện tại", default=True)

    subject_id = models.ForeignKey(Subject, verbose_name="Môn")
    student_id = models.ForeignKey(Pupil, verbose_name="Học sinh", null=True,
        blank=True)
    term_id = models.ForeignKey(Term, verbose_name="Kì")

    class Meta:
        verbose_name = "Bảng điểm"
        verbose_name_plural = "Bảng điểm"


    def save(self, force_insert=False, force_update=False, using=None):
        # If this variable is never used, delete it.
        super(Mark, self).save(force_insert=force_insert,
            force_update=force_update,
            using=using)

    def __unicode__(self):
        return u"%s %s%s" % (self.subject_id.name,
                             unicode(self.term_id.number),
                             unicode(self.student_id.first_name))

    def convertToList(self):
        list = []
        strss = self.diem.split('|')
        for i, strs in enumerate(strss):
            str = strs.split('*')
            length = len(str)
            aList = []
            for s in str:
                aList.append(s)
            list.append((length, aList))
        return list

    def toArrayMark(self, has_final=False ):
        if not has_final:
            arrMark = [''] * (3 * MAX_COL + 1)
        else:
            arrMark = [''] * (3 * MAX_COL + 3)

        diems = self.diem.split('|')
        for (i, d) in enumerate(diems):
            ds = d.split('*')
            for (j, a) in enumerate(ds):
                arrMark[i * MAX_COL + j + 1] = a
        if has_final:
            if self.ck == None:
                arrMark[3 * MAX_COL + 1] = ''
            else:
                arrMark[3 * MAX_COL + 1] = normalize(self.ck)

            if self.tb == None:
                arrMark[3 * MAX_COL + 2] = ''
            else:
                arrMark[3 * MAX_COL + 2] = normalize(self.tb)

        return arrMark

    def toArrayTime(self):
        arrTime = [''] * ( 3 * MAX_COL + 3)
        times = self.time.split('|')
        for (i, t) in enumerate(times):
            ts = t.split('*')
            for (j, a) in enumerate(ts):
                if i < 3:
                    arrTime[i * MAX_COL + j + 1] = a
                else:
                    arrTime[3 * MAX_COL + i - 2] = a
        return  arrTime

    def to_array_sent(self):
        arr_sent = [''] * ( 3 * MAX_COL + 3)
        sents = self.sent.split('|')
        for (i, t) in enumerate(sents):
            ts = t.split('*')
            for (j, a) in enumerate(ts):
                if i < 3:
                    arr_sent[i * MAX_COL + j + 1] = a
                else:
                    arr_sent[3 * MAX_COL + i - 2] = a
        return  arr_sent

    def saveSent(self, arrSent):
        sent = ''
        for i in range(3):
            tempSent = ''
            pre = 1
            for j in range(1, MAX_COL + 1):
                if arrSent[i * MAX_COL + j] != '':
                    tempSent += (j - pre) * '*' + arrSent[i * MAX_COL + j]
                    pre = j
            sent += tempSent + '|'
        sent += arrSent[3 * MAX_COL + 1] + '|' + arrSent[3 * MAX_COL + 2]
        self.sent = sent
        self.save()

    def saveMark(self, arrMark, is_save=False):
        diem = ''
        for i in range(3):
            tempDiem = ''
            pre = 1
            for j in range(1, MAX_COL + 1):
                if arrMark[i * MAX_COL + j] != '':
                    #noinspection PyTypeChecker
                    tempDiem += (j - pre) * '*' + normalize(arrMark[i * MAX_COL + j])
                    pre = j
            if i != 2:
                diem += tempDiem + '|'
            else:
                diem += tempDiem
        self.diem = diem
        if is_save:
            self.save()

    def saveTime(self, arrTime):
        time = ''
        for i in range(3):
            tempTime = ''
            pre = 1
            for j in range(1, MAX_COL + 1):
                if arrTime[i * MAX_COL + j] != '':
                    tempTime += (j - pre) * '*' + arrTime[i * MAX_COL + j]
                    pre = j
            time += tempTime + '|'
        time += arrTime[3 * MAX_COL + 1] + '|' + arrTime[3 * MAX_COL + 2]
        self.time = time

    def toString(self, x, isNormalize=True, isComment=False, space=" "):
        scores = self.diem.split('|')[x].split('*')
        if not isComment:
            if isNormalize:
                result = ""
                for s in scores:
                    if s != "":
                        result += normalize(s) + space
            else:
                result = ""
                for s in scores:
                    if s != "":
                        result += str(float(s)) + space
        else:
            result = ""
            for s in scores:
                if s != "":
                    result += convertMarkToCharacter1(float(s)) + space
        return result

    #this method returns a string containing all new information of
    #the marks
    #Paras:
    #   subject: Subject object for query avoidance 
    def new_summary(self, subject=None):
        if not subject: subject = self.subject_id
        is_comment = subject.nx
        arr_mark = self.toArrayMark()
        arr_sent = self.to_array_sent()
        result = []
        for i in range(3):
            temp = ''
            for j in range(MAX_COL):
                if ((arr_mark[i * MAX_COL + j + 1] != '')
                    & (arr_sent[i * MAX_COL + j + 1] == '')):
                    if is_comment:
                        temp += convertMarkToCharacter1(
                            float(arr_mark[i * MAX_COL + j + 1]),
                            False) + ' '
                    else:
                        temp += arr_mark[i * MAX_COL + j + 1] + ' '
            if temp != '':
                if  i == 0:
                    result.append(u' m %s' % temp.replace('.', ',').strip())
                elif i == 1:
                    result.append(" 15p %s" % temp.replace('.', ',').strip())
                elif i == 2:
                    result.append(" 45p %s" % temp.replace('.', ',').strip())
                    #so on i=3,4
        result = ';'.join(result)
        return result + '.' if result else result

    def update_mark(self, m, index):
        if index <= 0:
            raise Exception('IndexOutOfRange')
        arr_mark = self.toArrayMark()
        arr_mark[index] = str(m)
        self.saveMark(arr_mark, True)

    def update_sent(self, index=None):
        if index and index <= 0:
            raise Exception('IndexOutOfRange')
        arr_diem = self.toArrayMark()
        arr_sent = self.to_array_sent()
        if (len(arr_diem) != len(arr_sent) - 2
            or index >= len(arr_sent)):
            raise Exception('BadMarkStructure')
        if not index:
            for i in range(0, len(arr_diem)):
                if arr_diem[i]: arr_sent[i] = '1'
        else:
            if arr_diem[index]: arr_sent[index] = '1'
        self.saveSent(arr_sent)

    def length(self, x=3):
        return x


class HistoryMark(models.Model):
    date = models.DateTimeField("Thời gian sửa điểm", auto_now=True)
    old_mark = models.FloatField("điểm cũ trước khi sửa", null=True, blank=True)
    number = models.SmallIntegerField("thứ tự của điểm bị sửa")

    term_id = models.ForeignKey(Term, verbose_name="Kì")
    mark_id = models.ForeignKey(Mark, verbose_name="Điểm")
    user_id = models.ForeignKey(User, verbose_name="Tài khoản")
    subject_id = models.ForeignKey(Subject, verbose_name="Môn")


class TKMon(models.Model):
    mg = models.BooleanField("Miễn giảm",
        default=False)
    tb_nam = models.FloatField("Trung bình năm",
        null=True, blank=True, validators=[validate_mark])
    time = models.IntegerField("Thời gian cập nhật điểm tổng kết",
        null=True, blank=True)
    sent = models.BooleanField("Đã gửi", default=False)
    #danh dau xem mon nay co dc phep thi lai hay ko
    thi_lai = models.BooleanField("Có thi lại", blank=True,
        default=False)
    diem_thi_lai = models.FloatField("Điểm thi lại", null=True,
        blank=True, validators=[validate_mark])
    # all fields can be null
    current = models.BooleanField("Thuộc lớp hiện tại",
        default=True)

    subject_id = models.ForeignKey(Subject, verbose_name="Môn")
    student_id = models.ForeignKey(Pupil, verbose_name="Học sinh")

    class Meta:
        verbose_name = "Trung bình môn"
        verbose_name_plural = "Trung bình môn"
        #class Admin: pass

    def __unicode__(self):
        return self.subject_id.name + " " + self.student_id.first_name


class KhenThuong(models.Model):
    student_id = models.ForeignKey(Pupil, verbose_name="Học sinh",
        null=True)
    term_id = models.ForeignKey(Term, verbose_name="Kì",
        null=True)
    time = models.DateField("Thời gian(*)",
        blank=True, default=date.today())
    hinh_thuc = models.CharField("Hình thức(*)",
        max_length=100, choices=KT_CHOICES)
    dia_diem = models.CharField("Địa điểm",
        max_length=100, blank=True, null=True)
    noi_dung = models.CharField("Nội dung",
        max_length=400, blank=True, null=True) # description
    luu_hoc_ba = models.BooleanField("Lưu học bạ",
        blank=True, default=False)

    class Meta:
        verbose_name = "Khen thưởng"
        verbose_name_plural = "Khen thưởng"

    def __unicode__(self):
        return self.hinh_thuc


class KiLuat(models.Model):
    student_id = models.ForeignKey(Pupil, verbose_name="Học sinh")
    term_id = models.ForeignKey(Term, verbose_name="Kì")

    time = models.DateField("Thời gian(*)",
        blank=True, default=date.today())
    hinh_thuc = models.CharField("Hình thức(*)",
        max_length=35, choices=KL_CHOICES)
    dia_diem = models.CharField("Địa điểm",
        max_length=100, blank=True, null=True)
    noi_dung = models.CharField("Nội dung",
        max_length=400, blank=True, null=True) # description
    luu_hoc_ba = models.BooleanField("Lưu học bạ",
        blank=True, default=False)

    class Meta:
        verbose_name = "Kỉ luật"
        verbose_name_plural = "Kỉ luật"

    def __unicode__(self):
        return self.hinh_thuc


class TBHocKy(models.Model):
    student_id = models.ForeignKey(Pupil, verbose_name="Học sinh")
    term_id = models.ForeignKey(Term, verbose_name="Kì")

    number_subject = models.SmallIntegerField("số lượng môn",
        null=True, blank=True, default=0)
    number_finish = models.SmallIntegerField("số lượng môn đã tổng kết xong",
        default=0)
    sent = models.BooleanField("Sent",
        default=False)

    tb_hk = models.FloatField("Trung bình học kỳ",
        validators=[validate_mark], null=True, blank=True)
    hl_hk = models.CharField("Học lực",
        max_length=3, choices=HL_CHOICES, null=True, blank=True)
    danh_hieu_hk = models.CharField("Danh hiệu",
        max_length=2, choices=DH_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name = "Trung bình học kỳ"
        verbose_name_plural = "Trung bình học kỳ"

    def __unicode__(self):
        return u"%s %s%s" % (str(self.tb_hk),
                             unicode(self.term_id), unicode(self.student_id))


class TBNam(models.Model):
    student_id = models.ForeignKey(Pupil, verbose_name="Học sinh")
    year_id = models.ForeignKey(Year, verbose_name="Năm học")

    number_subject = models.SmallIntegerField("số lượng môn",
        null=True, blank=True, default=0)
    number_finish = models.SmallIntegerField("số lượng môn chưa tổng kết xong",
        default=0)

    tb_nam = models.FloatField("Trung bình năm",
        validators=[validate_mark], null=True, blank=True)
    hl_nam = models.CharField("Học lực",
        max_length=3, choices=HL_CHOICES, null=True, blank=True)
    #hanh kiem nam
    term1 = models.CharField("Kì 1",
        max_length=2, choices=HK_CHOICES, null=True, blank=True)
    term2 = models.CharField("Kì 2", max_length=2,
        choices=HK_CHOICES, null=True, blank=True)
    year = models.CharField("Cả năm",
        max_length=2, choices=HK_CHOICES, null=True, blank=True)
    #danh dau ren luyen lai trong giai doan he
    ren_luyen_lai = models.NullBooleanField("Rèn luyện lại",
        blank=True, null=True)
    hk_ren_luyen_lai = models.CharField("Hạnh kiểm rèn luyện lại",
        null=True, blank=True, max_length=2, choices=HK_CHOICES)

    tong_so_ngay_nghi = models.SmallIntegerField("Số ngày nghỉ",
        null=True, blank=True)
    #ghi danh hieu ma hoc sinh dat dc trong hoc ky    
    danh_hieu_nam = models.CharField("Danh hiệu",
        max_length=2, choices=DH_CHOICES, null=True, blank=True)
    len_lop = models.NullBooleanField("Lên lớp",
        choices=LENLOP_CHOICES, null=True, blank=True)
    #danh dau thi lai

    thi_lai = models.NullBooleanField("Thi lại",
        null=True, blank=True)
    tb_thi_lai = models.FloatField("Trung bình thi lại",
        null=True, blank=True, validators=[validate_mark])
    hl_thi_lai = models.CharField("Học lực thi lại",
        null=True, blank=True, max_length=3, choices=HL_CHOICES)
    sent = models.BooleanField("Sent", default=False)

    #hanh kiem cho cac thang
    hk_thang_9 = models.CharField("Tháng 9",
        max_length=2, choices=HK_CHOICES, blank=True)
    hk_thang_10 = models.CharField("Tháng 10",
        max_length=2, choices=HK_CHOICES, blank=True)
    hk_thang_11 = models.CharField("Tháng 11",
        max_length=2, choices=HK_CHOICES, blank=True)
    hk_thang_12 = models.CharField("Tháng 12",
        max_length=2, choices=HK_CHOICES, blank=True)
    hk_thang_1 = models.CharField("Tháng 1",
        max_length=2, choices=HK_CHOICES, blank=True)
    hk_thang_2 = models.CharField("Tháng 2",
        max_length=2, choices=HK_CHOICES, blank=True)
    hk_thang_3 = models.CharField("Tháng 3",
        max_length=2, choices=HK_CHOICES, blank=True)
    hk_thang_4 = models.CharField("Tháng 4",
        max_length=2, choices=HK_CHOICES, blank=True)
    hk_thang_5 = models.CharField("Tháng 5",
        max_length=2, choices=HK_CHOICES, blank=True)

    class Meta:
        verbose_name = "Trung bình năm"
        verbose_name_plural = "Trung bình năm"

    def __unicode__(self):
        return u"%s %s%s" % (unicode(self.student_id),
                             unicode(self.year_id), unicode(self.tb_nam))

    def convertHk(self, x):
        if x == 'T': return u'Tốt'
        elif x == 'K': return u'Khá'
        elif x == 'TB': return u'TB'
        elif x == 'Y': return u'Yếu'

    def get_hk_term1(self):
        if self.term1: return self.convertHk(self.term1)
        else: return u"Chưa xét"

    def get_hk_term2(self):
        if self.term2: return self.convertHk(self.term2)
        else: return u"Chưa xét"

    def get_list_month(self):
        return [self.hk_thang_9, self.hk_thang_10,
                self.hk_thang_11, self.hk_thang_12,
                self.hk_thang_1, self.hk_thang_2,
                self.hk_thang_3, self.hk_thang_4,
                self.hk_thang_5]

    def get_hk_year(self):
        if self.year: return self.convertHk(self.year)
        else: return u"Chưa xét"


class DiemDanh(models.Model):
    student_id = models.ForeignKey(Pupil, verbose_name="Học sinh")
    term_id = models.ForeignKey(Term, verbose_name="Kì")

    time = models.DateField("Ngày")
    loai = models.CharField("Tình trạng",
        max_length=10, choices=DIEM_DANH_TYPE)

    class Meta:
        verbose_name = "Điểm danh"
        verbose_name_plural = "Điểm danh"
        unique_together = ("student_id", "time", "term_id")

    def __unicode__(self):
        return u"%s %s" % (unicode(self.student_id), unicode(self.time))


class TKDiemDanh(models.Model):
    student_id = models.ForeignKey(Pupil, verbose_name="Học sinh")
    term_id = models.ForeignKey(Term, verbose_name="Kì")

    tong_so = models.IntegerField(u"Số buổi nghỉ",
        blank=True, null=True, default=0)
    co_phep = models.IntegerField(u"Số buổi có phép",
        blank=True, null=True, default=0)
    khong_phep = models.IntegerField(u"Số buổi không phép",
        blank=True, null=True, default=0)
    muon = models.IntegerField(u"Số buổi muộn",
        blank=True, null=True, default=0)

    class Meta:
        verbose_name = "Tổng kết điểm danh"
        verbose_name_plural = "Tổng kết điểm danh"

    def __unicode__(self):
        return self.student_id.__unicode__()


class TKB(models.Model):
    class_id = models.ForeignKey(Class, verbose_name="Lớp")
    day = models.SmallIntegerField("Thứ", choices=DAY_CHOICE)
    period_1 = models.ForeignKey(Subject, related_name="Tiet_1",
        null=True)
    period_2 = models.ForeignKey(Subject, related_name="Tiet_2",
        null=True)
    period_3 = models.ForeignKey(Subject, related_name="Tiet_3",
        null=True)
    period_4 = models.ForeignKey(Subject, related_name="Tiet_4",
        null=True)
    period_5 = models.ForeignKey(Subject, related_name="Tiet_5",
        null=True)
    period_6 = models.ForeignKey(Subject, related_name="Tiet_6",
        null=True)
    period_7 = models.ForeignKey(Subject, related_name="Tiet_7",
        null=True)
    period_8 = models.ForeignKey(Subject, related_name="Tiet_8",
        null=True)
    period_9 = models.ForeignKey(Subject, related_name="Tiet_9",
        null=True)
    period_10 = models.ForeignKey(Subject, related_name="Tiet_10",
        null=True)
    chaoco = models.IntegerField("Tiết chào cơ",
        null=True)
    sinhhoat = models.IntegerField("Tiết sinh hoạt",
        null=True)

    def get_numbers(self, subject):
        numbers = []
        for i in range(1, 11):
            if getattr(self, 'period_' + str(i)) == subject:
                numbers.append(i)
        return numbers


class Lesson(models.Model):
    subject_id = models.ForeignKey(Subject, verbose_name="Môn")
    index = models.IntegerField("Thứ tự",
        default=0)
    title = models.TextField("Tên bài học",
        blank=True, null=True)
    note = models.TextField("Ghi chú",
        blank=True, null=True)
    ngay_day = models.DateField("Ngày dạy",
        blank=True, null=True)

    def __unicode__(self):
        return u"%s Tiết %s" % (unicode(self.subject_id),
                                unicode(self.index))


class SchoolLesson(models.Model):
    school = models.ForeignKey(Organization, verbose_name="Trường")
    subject = models.IntegerField("Môn học",
        choices=SUBJECT_CHOICES, default=1)
    grade = models.IntegerField("Khối",
        choices=GRADES_CHOICES, default=6)
    term = models.IntegerField("Kì",
        choices=TERMS, default=1)
    index = models.IntegerField("Thứ tự",
        default=0)
    title = models.TextField("Tên bài học",
        blank=True, null=True)
    note = models.TextField("Ghi chú",
        blank=True, null=True)
    ngay_day = models.DateField("Ngày dạy",
        blank=True, null=True)

    def __unicode__(self):
        return unicode(self.school) + u' Môn ' + unicode(
            SUBJECT_CHOICES[int(self.subject) - 1][1]) + u' khối ' + unicode(self.grade) + u' kì ' + unicode(
            self.term) + u' tiết ' + unicode(self.term)
