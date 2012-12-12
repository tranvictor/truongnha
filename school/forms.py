# -*- coding: utf-8 -*-
import os
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from django.forms.widgets import  DateInput, TextInput
from datetime import timedelta, date
import xlrd
import datetime
from django.conf import settings
from app.models import Organization, TERMS, SUBJECT_CHOICES, KHOI_CHOICES
from school.models import Teacher, Block, Group, Team, GRADES_CHOICES3, Pupil, Class, StartYear, validate_phone, validate_class_label, TBNam, Subject, KhenThuong, DiemDanh, KiLuat, TKDiemDanh, DIEM_DANH_TYPE, Mark, Term, TKB, Lesson, GRADES_CHOICES2
from school.utils import get_school, get_permission, save_file

EXPORTED_FILE_LOCATION = settings.EXPORTED_FILE_LOCATION
class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
    
class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        exclude = ('school_id', 'user_id', 'index', 'balance')
        widgets = {
            'birthday' : DateInput(attrs = {'class':'datepicker input-small'}),
            'sms_phone': TextInput(attrs={'class':'input-medium'}),
        }
    def __init__(self,school_id, *args, **kwargs):
        def validate_teacher_birthday(value):
            if value > date.today()-timedelta(days=3650) or value < date(1900,1,1):
                raise ValidationError(u'Ngày nằm ngoài khoảng cho phép')
        super(TeacherForm,self).__init__(*args, **kwargs)
        school = Organization.objects.get(id=school_id)
        self.fields['birthday'] = forms.DateField(required=True,
                    label=u'Ngày sinh', validators=[validate_teacher_birthday],
                widget=forms.DateInput(attrs={'class':'datepicker input-small'}))
        self.fields['team_id'] = forms.ModelChoiceField(queryset=school.team_set.all(),
                required=False, label=u'Tổ')
        self.fields['group_id'] = forms.ModelChoiceField(
                 queryset=Group.objects.filter(team_id__school_id=school),
                 required=False, label=u'Nhóm')

class TeacherITForm(forms.ModelForm):
    class Meta:
        model = Teacher
        exclude = ('school_id', 'user_id')
        widgets = {
            'birthday' : DateInput(attrs = {'class':'datepicker'}),
        }
    def __init__(self,team_id, *args, **kwargs):
        super(TeacherITForm,self).__init__(*args, **kwargs)
        team = Team.objects.get(id = team_id)
        school = team.school_id
        self.fields['team_id'] = forms.ModelChoiceField(
                queryset=school.team_set.all(), required=False, label=u'Tổ')
        self.fields['group_id'] = forms.ModelChoiceField(
                queryset=team.group_set.all(), required=False, label=u'Nhóm')

class TeacherGroupForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = {'group_id'}
    def __init__(self,team_id, *args, **kwargs):
        super(TeacherGroupForm,self).__init__(*args, **kwargs)
        if not team_id:
            self.fields['group_id'] = forms.ChoiceField(label=u'Nhóm')
        else:
            team = Team.objects.get(id = team_id)
            self.fields['group_id'] = forms.ModelChoiceField(
                    queryset=team.group_set.all(), required=False, label=u'Nhóm')
        for field in self.fields:
            self.fields[field].widget.attrs['disabled'] = 'disabled'

class TeacherTTCNForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('last_name','first_name','birthday','sex','major','team_id')
        widgets = {
            'birthday' : DateInput(attrs = {'class':'datepicker'}),
        }

    def __init__(self, school_id, *args, **kwargs):
        super(TeacherTTCNForm, self).__init__(*args, **kwargs)
        school = Organization.objects.get(id = school_id)
        self.fields['team_id'] = forms.ModelChoiceField(
                queryset=school.team_set.all(), required=False, label=u'Tổ')
        for field in self.fields:
            self.fields[field].widget.attrs['disabled'] = 'disabled'

class TeacherTTCNForm2(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('birth_place','dan_toc','ton_giao','quoc_tich','home_town')

    def __init__(self, *args, **kwargs):
        super(TeacherTTCNForm2, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['disabled'] = 'disabled'
            self.fields[field].widget.attrs['class'] = 'tea'

class TeacherTTLLForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('current_address','phone','email','sms_phone')

    def __init__(self, *args, **kwargs):
        super(TeacherTTLLForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['disabled'] = 'disabled'
            self.fields[field].widget.attrs['class'] = 'tea'

class TeacherTTCBForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('cmt','ngay_cap','noi_cap','ngay_vao_doan',
                'ngay_vao_dang','muc_luong','hs_luong','bhxh')
        widgets = {
            'ngay_vao_doan' : DateInput(attrs={'class': 'datepicker'}),
            'ngay_vao_dang' : DateInput(attrs={'class': 'datepicker'})
        }

    def __init__(self, *args, **kwargs):
        super(TeacherTTCBForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['disabled'] = 'disabled'
            
class PupilForm(forms.ModelForm):
    class Meta:
        model = Pupil
        exclude = ('school_id','user_id','index', 'classes')
        widgets = {
            'birthday' : DateInput(attrs = {'class':'datepicker'}),
            'school_join_date' : DateInput(attrs = {'class':'datepicker'}),
            'ngay_vao_doan': DateInput(attrs = {'class':'datepicker'}),
            'ngay_vao_doi': DateInput(attrs = {'class':'datepicker'}),
            'ngay_vao_dang': DateInput(attrs = {'class':'datepicker'}),
            'father_birthday': DateInput(attrs = {'class':'datepicker'}),
            'mother_birthday': DateInput(attrs = {'class':'datepicker'}),
        }
    def __init__(self, school_id, *args, **kwargs):
        super(PupilForm, self).__init__(*args, **kwargs)
        school = Organization.objects.get(id = school_id)
        year_id = school.year_set.latest('time').id
        self.fields['start_year_id'] = forms.ModelChoiceField(
                queryset=StartYear.objects.filter(school_id=school_id),label='Khóa')
        self.fields['class_id'] = forms.ModelChoiceField(
                queryset=Class.objects.filter(year_id=year_id),label='Lớp')

class ThongTinCaNhanForm(forms.ModelForm):
    class Meta:
        model = Pupil
        fields = ('last_name','first_name','birthday',
                'sex','start_year_id','birth_place','dan_toc',
                'ton_giao','uu_tien','quoc_tich','home_town',
                'ban_dk','school_join_date','school_join_mark')
        widgets = {
            'birthday' : DateInput(attrs={'class':'datepicker'}),
            'school_join_date' : DateInput(attrs={'class':'datepicker'})
        }
        
    def __init__(self, school_id, *args, **kwargs):
        super(ThongTinCaNhanForm, self).__init__(*args, **kwargs)
        self.fields['start_year_id'] = forms.ModelChoiceField(
                queryset=StartYear.objects.filter(school_id=school_id),label='Khóa')
        for field in self.fields:
            self.fields[field].widget.attrs['disabled'] = 'disabled'

class ThongTinLienLacForm(forms.ModelForm):
    class Meta:
        model = Pupil
        fields = ('current_address','phone','father_phone',
                'mother_phone','sms_phone','email')

    def __init__(self, *args, **kwargs):
        super(ThongTinLienLacForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['disabled'] = 'disabled'

class ThongTinGiaDinhForm(forms.ModelForm):
    class Meta:
        model = Pupil
        fields = ('father_name','father_birthday','father_job',
                'mother_name','mother_birthday','mother_job')
        widgets = {
            'father_birthday': DateInput(attrs={'class':'datepicker'}),
            'mother_birthday': DateInput(attrs={'class':'datepicker'}),
        }
    def __init__(self, *args, **kwargs):
        super(ThongTinGiaDinhForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['disabled'] = 'disabled'
        
class ThongTinDoanDoiForm(forms.ModelForm):
    def __init__(self, student_id, *args, **kw):
        student = Pupil.objects.get(id=student_id)
        
        def validate_ttdd_date(value):
            if value < student.birthday+timedelta(days=2190) or value > date.today():
                raise ValidationError(u'Ngày nằm ngoài khoảng cho phép')

        super(ThongTinDoanDoiForm, self).__init__(*args, **kw)
        self.fields.keyOrder = ['doi','ngay_vao_doi','doan',
                'ngay_vao_doan','dang','ngay_vao_dang']
        self.fields['ngay_vao_doi'] = forms.DateField(
                required=False, label=u'Ngày vào đội',
                validators=[validate_ttdd_date],
                widget=forms.DateInput(attrs={'class':'datepicker'}))
        self.fields['ngay_vao_doan'] = forms.DateField(required=False,
                label=u'Ngày vào đoàn',
                validators=[validate_ttdd_date],
                widget=forms.DateInput(attrs={'class':'datepicker'}))
        self.fields['ngay_vao_dang'] = forms.DateField(required=False,
                label=u'Ngày vào đảng',
                validators=[validate_ttdd_date],
                widget=forms.DateInput(attrs={'class':'datepicker'}))

        for field in self.fields:
            self.fields[field].widget.attrs['disabled'] = 'disabled'
        
    class Meta:
        model = Pupil
        fields = {'doi','ngay_vao_doi','doan','ngay_vao_doan','dang','ngay_vao_dang'}

class MoveClassForm(forms.Form):
    def __init__(self, student, *args, **kw):
        super(MoveClassForm,self).__init__(*args, **kw)
        current_class = student.current_class()
        if current_class:
            block = current_class.block_id
            self.fields['move_to'] = forms.ModelChoiceField(
                    label=u'Chuyển tới',
                    queryset=Class.objects.filter(block_id=block)\
                            .exclude(id=current_class.id).order_by('name'))

class SchoolForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(SchoolForm, self).__init__(*args, **kwargs)
        if get_permission(self.request) in [u'HIEU_TRUONG', u'HIEU_PHO']:
            self.fields['name'] = forms.CharField(label=u'Tên trường:',
                    max_length = 100 ) #tên đơn vị. tổ chức
            school = get_school(self.request)
            self.fields['school_level'] = forms.ChoiceField(label=u"Cấp:",
                    choices=KHOI_CHOICES)
            if school.status in [1,2]:
                self.fields['school_level'].widget.attrs['disabled'] = 'disabled'
                self.fields['school_level'].required = False
            self.fields['address'] = forms.CharField(label=u"Địa chỉ:",
                    max_length=255, required=False) #
            self.fields['phone'] = forms.CharField(label="Điện thoại:",
                    max_length=20, validators=[validate_phone], required=False)
            self.fields['email'] = forms.EmailField(max_length=50, required=False) 

    def save_to_model(self):
        try:
            school = get_school(self.request)
            school.name = self.cleaned_data['name']
            if self.cleaned_data['school_level']:
                school.school_level = self.cleaned_data['school_level']
            school.address = self.cleaned_data['address']
            school.phone = self.cleaned_data['phone']
            school.email = self.cleaned_data['email']
            school.save()
        except Exception as e:
            print e

class SettingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(SettingForm, self).__init__(*args, **kwargs)
        self.fields['lock_time'] = forms.IntegerField(
                label=u"Không cho sửa điểm sau:",
                required=True,
                help_text=u"Khoảng thời gian giáo viên được sửa điểm từ lúc nhập") #

        self.fields['semester_start_time'] = forms.DateField(
                label=u'Ngày bắt đầu học kỳ:',
                required=False,
                widget=forms.DateInput(attrs={'class':'datepicker'}))

        self.fields['semester_finish_time'] = forms.DateField(
                label=u'Ngày kết thúc học kỳ:',
                required=False,
                widget=forms.DateInput(attrs={'class':'datepicker'}))

        self.fields['class_labels'] = forms.CharField(
                label=u"Danh sách lớp học:", max_length=512,
                validators=[validate_class_label],
                widget=forms.Textarea,
                required = False)

    def clean(self):
        cleaned_data = super(SettingForm, self).clean()
        semester_start_time = cleaned_data.get("semester_start_time")
        semester_finish_time = cleaned_data.get("semester_finish_time")
        if semester_start_time and semester_finish_time:
            if semester_finish_time < semester_start_time:
                msg = u"Ngày kết thúc học kì phải sau ngày bắt đầu học kì."
                self._errors["semester_finish_time"] = self.error_class([msg])
                raise forms.ValidationError(msg)
        return cleaned_data

    def save_to_model(self):
        try:
            school = get_school(self.request)
            if self.cleaned_data['lock_time'] >= 0:
                school.save_settings('lock_time', self.cleaned_data['lock_time'])
            else:
                raise Exception('LockTimeValueError')
            if self.cleaned_data['class_labels']:
                labels = self.cleaned_data['class_labels']
                labels = labels.split(',')
                result = u'['
                for label in labels:
                    if label.strip():
                        result += u"u'%s'," % label.strip()
                result = result[:-1]
                result += u']'
                school.save_settings('class_labels', unicode(result) )
            if self.cleaned_data['semester_start_time']:
                #TODO: validate start time
                school.save_settings('semester_start_time',
                        self.cleaned_data['semester_start_time'].strftime('%d/%m/%Y'))
            if self.cleaned_data['semester_finish_time']:
                school.save_settings('semester_finish_time',
                        self.cleaned_data['semester_finish_time'].strftime('%d/%m/%Y'))
        except Exception as e:
            print e

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        exclude = {'max'}
        
    def __init__(self, school_id, *args, **kwargs):
        super(ClassForm, self).__init__(*args, **kwargs)
        self.fields['teacher_id'] = forms.ModelChoiceField(required = False, queryset=Teacher.objects.filter(school_id = school_id))
        self.fields['block_id'] = forms.ModelChoiceField(queryset=Block.objects.filter(school_id = school_id))
class TBNamForm(forms.ModelForm):
    class Meta:
        model = TBNam
        exclude = {'number_subject', 'number_finish', 'tong_so_ngay_nghi', 'danh_hieu_nam', 'len_lop', 'thi_lai', 'tb_thi_lai', 'hl_thi_lai'}
        widgets = {
            'hk_thang_9' : forms.TextInput(attrs={'size':'1', 'class':'hk'}),
            'hk_thang_10' : forms.TextInput(attrs={'size':'1', 'class':'hk'}),
            'hk_thang_11' : forms.TextInput(attrs={'size':'1', 'class':'hk'}),
            'hk_thang_12' : forms.TextInput(attrs={'size':'1', 'class':'hk'}),
            'hk_thang_1' : forms.TextInput(attrs={'size':'1', 'class':'hk'}),
            'hk_thang_2' : forms.TextInput(attrs={'size':'1', 'class':'hk'}),
            'hk_thang_3' : forms.TextInput(attrs={'size':'1', 'class':'hk'}),
            'hk_thang_4' : forms.TextInput(attrs={'size':'1', 'class':'hk'}),
            'hk_thang_5' : forms.TextInput(attrs={'size':'1', 'class':'hk'}),
            'term1' : forms.TextInput(attrs={'size':'1', 'class':'hk'}),
            'term2' : forms.TextInput(attrs={'size':'1', 'class':'hk'}),
            'year' : forms.TextInput(attrs={'size':'1', 'class':'hk'})
        }
    def get_list_month(self):
        return [self['hk_thang_9'], self['hk_thang_10'], self['hk_thang_11'], self['hk_thang_12'], self['hk_thang_1'],self['hk_thang_2'], self['hk_thang_3'], self['hk_thang_4'], self['hk_thang_5']]
        

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        exclude = {'index','class_id', 'max'}
        widgets = {
            'hs':forms.TextInput(attrs={'size':'5','maxlength':'5'}),
            'number_lesson': forms.TextInput(attrs={'size':'5','maxlength':'5'}),
            'name':forms.TextInput(attrs={'size':'12','maxlength':'12'}),
        }
        
    def __init__(self, school_id, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)
        self.fields['teacher_id'] = forms.ModelChoiceField(required = False, queryset = Teacher.objects.filter(school_id = school_id), label=u'Giáo viên giảng dạy')

class KhenThuongForm(forms.ModelForm):
    class Meta:
        model = KhenThuong
        exclude = ('student_id', 'term_id')
        widgets = {
            'noi_dung': forms.Textarea(attrs = {'cols': 50, 'rows': 10}),
        }

    def __init__(self, student_id, *args, **kw):
        student = Pupil.objects.get(id = student_id)
        def validate_ktkl_date(value):
            if value < student.school_join_date or value > date.today():
                raise ValidationError(u'Ngày nằm ngoài khoảng cho phép.\n Ngày hợp lệ tính từ ngày học sinh nhập trường đến ngày hiện tại')
        super(KhenThuongForm, self).__init__(*args, **kw)
        self.fields['time'] = forms.DateField(required=False, initial=date.today(), label=u'Ngày',
            validators=[validate_ktkl_date], widget=forms.DateInput(attrs={'class':'datepicker'}))

class KiLuatForm(forms.ModelForm):        
    class Meta:
        model = KiLuat
        exclude = ('student_id', 'term_id')
        field = ('time', 'noi_dung')
        widgets = {
            'time' : DateInput(attrs = {'class':'datepicker'}),
            'noi_dung': forms.Textarea(attrs = {'cols': 50, 'rows': 10}),
        }

    def __init__(self, student_id, *args, **kw):
        student = Pupil.objects.get(id = student_id)
        def validate_ktkl_date(value):
            if value < student.school_join_date or value > date.today():
                raise ValidationError(u'Ngày nằm ngoài khoảng cho phép. Ngày hợp lệ tính từ ngày học sinh nhập trường đến ngày hiện tại')
        super(KiLuatForm, self).__init__(*args, **kw)
        self.fields['time'] = forms.DateField(required=False,
                label=u'Ngày', initial=date.today(),
                validators=[validate_ktkl_date],
                widget=forms.DateInput(attrs={'class':'datepicker'}))

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
    def __init__(self, *args, **kw):
        school = None
        if 'school' in kw:
            school = kw.pop('school')
        super(GroupForm,self).__init__(*args, **kw)
        self.fields['team_id'] = forms.ModelChoiceField(queryset=school.team_set,
                label=u'Tổ')


class DiemDanhForm(forms.ModelForm):
    class Meta:
        model = DiemDanh
        widgets = {
            'time' : DateInput(attrs={'class':'datepicker'})
        }

class DDForm(forms.ModelForm):
    class Meta:
        model = DiemDanh
    def __init__(self,*args,**kw):
        super(DDForm,self).__init__(*args, **kw)
        self.fields['loai'] = forms.CharField(max_length=1, required=False)

class NDiemDanhForm(forms.Form):
    loai = forms.ChoiceField(choices=DIEM_DANH_TYPE)

class TKDiemDanhForm(forms.ModelForm):
    class Meta:
        model = TKDiemDanh

class TermForm(forms.ModelForm):
    class Meta:
        model = Term

class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        
class DateForm(forms.Form):
    date = forms.DateField(label='',
            widget=DateInput(attrs={'class': 'datepicker'}),
            initial=datetime.date.today())

        
class DateAndClassForm(forms.Form):
    class_id = forms.ModelChoiceField(queryset=Class)
    date = forms.DateField(label=u'ngày',
            widget=DateInput(attrs={'class': 'datepicker'}),
            initial=datetime.date.today)
    
    def __init__(self, year_id, *args, **kwargs):
        super(DateAndClassForm, self).__init__(*args, **kwargs)
        self.fields['class_id'] = forms.ModelChoiceField(
                queryset=Class.objects.filter(year_id=year_id).order_by('name'),
                label=u'Lớp', empty_label=None)
    
class UploadImportFileForm(forms.Form):
    def __init__(self, * args, ** kwargs):
        class_list = kwargs.pop('class_list')
        super(UploadImportFileForm, self).__init__(*args, ** kwargs)
        self.fields['the_class'] = forms.ChoiceField(label=u'Nhập vào lớp:',
                choices=class_list, required=False)
        self.fields['import_file'] = forms.FileField(label=u'Chọn file Excel:')
        
class ManualAddingForm(forms.Form):
    def __init__(self, * args, ** kwargs):
        class_list = kwargs.pop('class_list')
        super(ManualAddingForm, self).__init__(*args, ** kwargs)
        self.fields['the_class'] = forms.ChoiceField(label=u'Nhập vào lớp:',
                choices=class_list, required=False)
        
class ClassifyForm(forms.Form):
    def __init__(self, * args, ** kwargs):
        students = kwargs.pop('student_list')
        classes = kwargs.pop('class_list')
        super(ClassifyForm, self).__init__(*args, ** kwargs)
        for student in students:
            label = ' '.join([student.last_name, student.first_name])
            label += u'[' + str(student.birthday.day ) \
                          + '-' + str(student.birthday.month) \
                          + '-' + str(student.birthday.year)+']'
            self.fields[str(student.id)] = forms.ChoiceField(
                    label=label, choices=classes, required=False)
CONTENT_TYPES = ['application/vnd.ms-excel']            

#class uploadFileExcel(forms.Form):
#    file  = forms.FileField(label=u'Chọn file Excel:', widget=forms.FileInput())
#
#    def is_valid(self):
#        file = self.cleaned_data['file']
#        if not file.content_type in CONTENT_TYPES:
#            os.remove(filepath)
#            raise forms.ValidationError(u'Bạn chỉ được phép tải lên file Excel.')
#        elif not os.path.getsize(filepath):
#            raise forms.ValidationError(u'File của bạn rỗng.')
#        elif not xlrd.open_workbook(filepath).sheet_by_index(0).nrows:
#            raise forms.ValidationError(u'File của bạn rỗng.')
#        else:
#            return super(uploadFileExcel, self).is_valid()
    
            
class smsFromExcelForm(forms.Form):
    file  = forms.Field(label="Chọn file Excel:",
                        error_messages={'required': 'Bạn chưa chọn file nào để tải lên.'},
                        widget=forms.FileInput())
    
    def clean_file(self):
        file = self.cleaned_data['file']
        save_file(file)            
        filepath = os.path.join(settings.TEMP_FILE_LOCATION, 'sms_input.xls')
        
        if not file.content_type in CONTENT_TYPES:
            os.remove(filepath)
            raise forms.ValidationError(u'Bạn chỉ được phép tải lên file Excel.')
        elif not os.path.getsize(filepath):
            raise forms.ValidationError(u'Hãy tải lên một file Excel đúng. File của bạn hiện đang trống.')
        elif not xlrd.open_workbook(filepath).sheet_by_index(0).nrows:
            raise forms.ValidationError(u'Hãy tải lên một file Excel đúng. File của bạn hiện đang trống.')
#        if content._size > settings.MAX_UPLOAD_SIZE:
#            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content._size)))
        else:
            return file     

class UsernameChangeForm(forms.Form):
    new_username = forms.RegexField(label=u"Tài khoản mới",
            max_length=30, regex=r'^[\w.@+-]+$')
    password = forms.CharField(label=u'Mật khẩu',
            widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UsernameChangeForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['new_username', 'password']
        
    def clean_password(self):
        password = self.cleaned_data["password"]
        if not self.user.check_password(password):
            raise forms.ValidationError(u"Mật khẩu không đúng hãy nhập lại")
        return password
    
    def clean_new_username(self):
        new_username = self.cleaned_data["new_username"]
        try:
            User.objects.get(username=new_username)
        except User.DoesNotExist:
            return new_username
        raise forms.ValidationError(u"Tên đăng nhập này đã tồn tại")

    def save(self,commit=True):
        self.user.username = self.cleaned_data["new_username"]
        self.user.userprofile.username_change = 1
        if commit:
            self.user.save()
            self.user.userprofile.save()
        return self.user

class TKBForm(forms.ModelForm):
    class Meta:
        model = TKB
        #field = ['class_id', 'day', 'period_1', 'period_2', 'period_3', 'period_4', 'period_5']
    def __init__(self, class_id, *args, **kwargs):
        super(TKBForm,self).__init__(*args, **kwargs)
        self.fields['period_1'] = forms.ModelChoiceField(required=False,
                queryset=Subject.objects.filter(class_id=class_id),
                label=u'Tiết 1')
        self.fields['period_2'] = forms.ModelChoiceField(required=False,
                queryset=Subject.objects.filter(class_id=class_id),
                label=u'Tiết 2')
        self.fields['period_3'] = forms.ModelChoiceField(required=False,
                queryset=Subject.objects.filter(class_id=class_id),
                label=u'Tiết 3')
        self.fields['period_4'] = forms.ModelChoiceField(required=False,
                queryset=Subject.objects.filter(class_id=class_id),
                label=u'Tiết 4')
        self.fields['period_5'] = forms.ModelChoiceField(required=False,
                queryset=Subject.objects.filter(class_id=class_id),
                label=u'Tiết 5')
        self.fields['period_6'] = forms.ModelChoiceField(required=False,
                queryset=Subject.objects.filter(class_id=class_id),
                label=u'Tiết 6')
        self.fields['period_7'] = forms.ModelChoiceField(required=False,
                queryset=Subject.objects.filter(class_id=class_id),
                label=u'Tiết 7')
        self.fields['period_8'] = forms.ModelChoiceField(required=False,
                queryset=Subject.objects.filter(class_id=class_id),
                label=u'Tiết 8')
        self.fields['period_9'] = forms.ModelChoiceField(required=False,
                queryset=Subject.objects.filter(class_id=class_id),
                label=u'Tiết 9')
        self.fields['period_10'] = forms.ModelChoiceField(required=False,
                queryset=Subject.objects.filter(class_id=class_id),
                label=u'Tiết 10')

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        exclude = ('index', 'subject_id')
        widgets = {
            'ngay_day' : DateInput(attrs={'class': 'datepicker'}),
            'title': forms.Textarea(attrs={'cols': 50, 'rows': 2}),
            'note': forms.Textarea(attrs={'cols': 100, 'rows': 2})}


class SelectSchoolLessonForm2(forms.Form):
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES, label="Môn học", initial=1)
    grade = forms.ChoiceField(choices=GRADES_CHOICES2, label ="Khối", initial=6)
    term = forms.ChoiceField(choices=TERMS, label ="Kì", initial=1)

class SelectSchoolLessonForm3(forms.Form):
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES, label="Môn học", initial=1)
    grade = forms.ChoiceField(choices=GRADES_CHOICES3, label ="Khối", initial=10)
    term = forms.ChoiceField(choices=TERMS, label ="Kì", initial=1)
