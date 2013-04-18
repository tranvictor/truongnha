# coding: utf8
__author__ = 'vutran'
from djangorestframework.views import View
from django.db import transaction
from djangorestframework.response import Response
from djangorestframework import status
from django.contrib.auth.views import logout
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.core.exceptions import ObjectDoesNotExist
from app.views import login
from sms.models import sms
from school.class_functions import dd
from school.models import Class, Pupil, Term, Subject, DiemDanh, TBNam, TKB, \
    KhenThuong, KiLuat, Mark, TKMon
from school.utils import get_position, get_school, is_teacher,\
        get_current_term, get_current_year, get_student, get_teacher,\
        to_date
from api.utils import getMarkForAStudent
from school.forms import MarkForm
from decorators import need_login, operating_permission, school_function
import simplejson
import time
import datetime
import re
from school.templateExcel import  MAX_COL, CHECKED_DATE
from school.viewMark import update_mark

class ApiLogin(View):
    """
    A basic view, that can be handle GET and POST requests.
    Applies some simple form validation on POST requests.
    """

    def get(self, request):
        response = login(request, api_called=True)
        print "-----------------------" + str(response.status_code)
        if response.status_code == 200:
            data = {
                'csrfmiddlewaretoken': get_token(request)
            }
            return HttpResponse(simplejson.dumps(data), mimetype='json')
            #return Response(status=status.HTTP_200_OK, content=data)
        else:
            return Response(status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        response = login(request, api_called=True)
        print request
        if response.status_code == 200:
            result = {}
            try:
                user_position = get_position(request)
                user = None
                if user_position == 1:
                    user = {
                        'userId': request.user.id,
                        'type': user_position,
                        'lastName': request.user.last_name,
                        'firstName': request.user.first_name,
                        'class': request.user.pupil.class_id.name,
                        'school': get_school(request).name,
                        'birth': request.user.pupil.birthday.strftime("%d/%m/%Y"),
                        'studentId': request.user.pupil.id,
                        }
                elif user_position in [2, 3]:
                    user = {
                        'userId': request.user.id,
                        'type': user_position,
                        'lastName': request.user.last_name,
                        'firstName': request.user.first_name,
                        'school': get_school(request).name,
                        'birth': request.user.teacher.birthday.strftime("%d/%m/%Y"),
                        'teacherId': request.user.teacher.id
                    }
                    homeroom_class = request.user.teacher.current_homeroom_class()
                    if homeroom_class:
                        user['class'] = homeroom_class.name
                    else:
                        user['class'] = ''

                elif user_position == 4:
                    raise Exception('NotFound')
                result['user'] = user
            except Exception as e:
                print e
                raise e
            if user_position == 1:
                #TODO: return necessary information for students
                #return Response(status=status.HTTP_404_NOT_FOUND)
                #term_id = get_current_term(request, except_summer=True).id
                #list = getMarkForAStudent(request.user.pupil.id, term_id)
                #result['mark'] = list
                pass
            elif user_position == 3:
                try:
                    teaching_subjects = request.user.teacher. current_teaching_subject()
                    result['teachingClass'] = {}
                    classes = []
                    for subject in teaching_subjects:
                        temp = {
                            'subjectId': subject.id,
                            'isComment': subject.nx,
                            'classId': subject.class_id.id,
                            'className': subject.class_id.name,
                            'subject': subject.name,
                            'size': subject.class_id.number_of_pupils(),
                            'homeTeacher': subject.class_id.teacher_id
                        }
                        if subject.class_id.teacher_id:
                            temp['homeTeacher'] = subject.class_id.teacher_id.full_name()
                        classes.append(temp)
                    homeroom_classes = request.user.teacher.homeroom_class()
                    if homeroom_classes:
                        for homeroom_class in homeroom_classes:
                            temp = {
                                'classId': homeroom_class.id,
                                'className': homeroom_class.name,
                                'subject': '-1',
                                'size': homeroom_class.number_of_pupils(),
                                'homeTeacher': homeroom_class.teacher_id
                            }
                            if homeroom_class.teacher_id:
                                temp['homeTeacher'] = homeroom_class.teacher_id.full_name()
                            classes.append(temp)
                    result['teachingClass'] = classes

                except Exception as e:
                    print e
                    raise e
            elif user_position > 3:
                #TODO: return necessary information for school's admins
                return Response(status=status.HTTP_404_NOT_FOUND)
            return HttpResponse(simplejson.dumps(result), mimetype='json')
        #return Response(status=status.HTTP_200_OK, content=result)
        else:
            return Response(status.HTTP_401_UNAUTHORIZED)


class ApiLogout(View):
    def get(self, request):
        logout(request=request)
        return Response(status=status.HTTP_200_OK)


class ApiGetStudentList(View):
    def get(self, request,
            class_id,
            day=None,
            month=None,
            year=None,
            all=False):
        if request.user.is_anonymous():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        position = get_position(request)
        if position >= 3:
            try:
                _class = Class.objects.filter(
                    block_id__school_id=get_school(request)).get(id=class_id)
            except ObjectDoesNotExist:
                return Response(status.HTTP_400_BAD_REQUEST)
            if all: student_list = _class.attended_student()
            else: student_list = _class.students()
            result = {
                'SUBJECT': 'Ten Mon hoc' # Vu~ cho ten mon hoc vao day cai :|
            }
            list = []
            for student in student_list:
                s = {
                    'id': student.id,
                    'name': student.last_name + ' ' + student.first_name,
                    'sex': student.sex,
                    'birth': student.birthday
                }
                list.append(s)
            result['list'] = list
            #return Response(status=status.HTTP_200_OK, content=result)
            return HttpResponse(simplejson.dumps(result), mimetype='json')
        else:
            return Response(status.HTTP_403_FORBIDDEN)


class Attendance(View):
    def get(self, request,
            class_id,
            day=None,
            month=None,
            year=None):
        if request.user.is_anonymous():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        date = None
        try:
            _class = Class.objects.filter(
                block_id__school_id=get_school(request)).get(id=class_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            date = datetime.datetime(int(year), int(month), int(day))
        except Exception:
            pass
        student_list = _class.students()
        if date:
            diemdanh_list = DiemDanh.objects.filter(student_id__in=student_list,
                time=date.date())
        else:
            diemdanh_list = []
        list = []
        for student in student_list:
            sta = ''
            for diemdanh in diemdanh_list:
                if diemdanh.student_id == student:
                    sta = diemdanh.loai
                    break
            s = {
                'id': student.id,
                'firstName': student.first_name,
                'lastName': student.last_name,
                'DOB': student.birthday,
                'sex': student.sex,
                'phone': student.phone,
                'smsPhone': student.sms_phone,
                'email': student.email,
                'status': sta}
            list.append(s)
        #return Response(status=status.HTTP_200_OK, content=list)
        return HttpResponse(simplejson.dumps(list), mimetype='json')


    @need_login
    @operating_permission(['HIEU_PHO', 'HIEU_TRUONG', 'GIAO_VIEN'])
    def post(self, request):
        """
        3. def for post Diem danh to server:
          post:
          "classId": "xxx"
          "date":"20-04-2012"
          "list":"studentId-status-20-04-2012%studentId-status-20-04-2012%studentId-status-20-04-2012"

        status la trang thai di hoc: K-Nghi ko phep; P- Nghi co phep; M-Di muon;
        """
        class_id = request.POST['classId']
        day = request.POST['date']
        data = request.POST['list']
        try:
            _class = Class.objects.get(id=int(class_id))
        except ObjectDoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        if (is_teacher(request)
            and request.user.teacher in _class.associated_teacher()):
            date_parts = day.split('-')
            try:
                response = dd(request,
                    class_id,
                    date_parts[0],
                    date_parts[1],
                    date_parts[2],
                    api_called=True,
                    data=data)
                if response.status_code == 200:
                    return Response(status.HTTP_200_OK)
                else:
                    return Response(status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print e
                raise e
        else:
            return Response(status.HTTP_403_FORBIDDEN)


class GetSubject(View):
    @need_login
    @school_function
    def get(self, request, class_id):
        try:
            cl = Class.objects.get(id=class_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        subjects = cl.subject_set.all()
        result = []
        for s in subjects:
            result.append({
                'name': s.name,
                'type': s.type,
                'hs': s.hs,
                'nx': s.nx,
                'primary': s.primary,
                'index': s.index,
                'numberLession': s.number_lession,
                'teacher': s.teacher_id.full_name()})
        #return Response(status=status.HTTP_200_OK, content=result)
        return HttpResponse(simplejson.dumps(result), mimetype='json')


class GetMark(View):
    @need_login
    @school_function
    @operating_permission(['HIEU_PHO', 'HIEU_TRUONG', 'GIAO_VIEN'])
    def get(self, request, student_id, subject_id, term_id):
        try:
            st = Pupil.objects.get(id=student_id)
            subject = Subject.objects.get(id=subject_id)
            term = Term.objects.get(id=term_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        marks = Mark.objects.filter(student_id=st,
            subject_id=subject,
            term_id=term)
        result = []
        for m in marks:
            a_mark = {}
            for f in m._meta.fields:
                a_mark[f.name] = getattr(m, f.name)
            result.append(a_mark)
        #return Response(status=status.HTTP_200_OK, content=result)
        return HttpResponse(simplejson.dumps(result), mimetype='json')

    @need_login
    @school_function
    @operating_permission(['HIEU_PHO', 'HIEU_TRUONG', 'GIAO_VIEN'])
    def post(self, request):
        #post some marks for students.
        #post data in form: request.POST[data]: '{id:mark, id:mark...}'
        #mark: {'diem_mieng_1':10, ..}
        #eg: "{11: {'diem_mieng_1': '10', ...},23: ...}"
        data = request.POST['data']
        try:
            data = simplejson.loads(data)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                content={'error': 'JsonStringNotFormed'})
        ids = data.keys()
        marks = Mark.objects.filter(id__in=ids)
        for m in marks:
            form = MarkForm(data[m.id], instance=m)
            if form.is_valid():
                form.save()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                    content={'error': 'MarkNotValid'})
        return Response(status=status.HTTP_200_OK)


class SchoolSetting(View):
    @need_login
    @school_function
    @operating_permission(['HIEU_PHO', 'HIEU_TRUONG'])
    def get(self, request):
        school = get_school(request)
        classes = school.get_setting('class_labels')
        print classes
        return Response(status=status.HTTP_200_OK,
            content={'classes': classes})

    @need_login
    @school_function
    @operating_permission(['HIEU_PHO', 'HIEU_TRUONG'])
    def post(self, request):
        if not 'class_labels' in request.POST:
            return Response(status.HTTP_404_NOT_FOUNT)
        cl_labels = request.POST['class_labels']
        school = get_school(request)
        if school.school_level == '2':
            cl_label_re = re.compile(r'(6|7|8|9)(\s*)(\w+)', flags=re.U)
        elif school.school_level == '3':
            cl_label_re = re.compile(r'(10|11|12)(\s*)(\w+)', flags=re.U)
        classes = cl_label_re.findall(cl_labels)
        setting = []
        success = True
        for cl in classes:
            grade, class_label = cl[0], cl[2]
            if not (grade and class_label):
                success = False
                break
            else: setting.append(' '.join([grade, class_label]))
        if success:
            result = u'['
            for st in setting:
                result += u"u'%s'," % st
            result += u']'
            school.save_settings('class_labels', result)
        data = {'success': success, 'setting': setting}
        return Response(status.HTTP_200_OK, content=data)


class SmsStatus(View):
    @need_login
    def get(self, request, ids):
        user = request.user
        ids = ids.split('-')
        _smses = sms.objects.filter(id__in=ids, sender=user)
        result = {}
        for s in _smses:
            result[s.id] = '%s-%s' % (s.recent, s.success)
        return Response(status.HTTP_200_OK, content=result)


class FailedSms(View):
    re_post_format = re.compile('^(\d+\-(failed|ok)\*{1,2})+')

    @need_login
    @operating_permission(['SUPER_USER'])
    def get(self, request, from_date, limit=10):
        try:
            from_date = to_date(from_date)
        except Exception:
            message = u'Ngày cần theo dạng dd-mm-yyyy'
            success = False
            HttpResponse(simplejson.dumps({
                'message': message,
                'success': success}, mimetype='json'))
        smses = sms.objects.filter(recent=False,
                success=False,
                created__gte=from_date)[:limit]
        result = []
        for s in smses:
            result.append({
                'id': s.id,
                'phone': s.phone,
                'content': s.content})
        for s in smses:
            s.recent = True
            s.save()
        return HttpResponse(simplejson.dumps({
            'message': u'Nhận %d tin nhắn' % len(smses),
            'smses': result,
            'success': True}), mimetype='json')

    @need_login
    @operating_permission(['SUPER_USER'])
    def post(self, request, from_date=None):
        sms_list = request.POST['sms_list']
        sms_list += '*' # Stupid maker
        temp = FailedSms.re_post_format.match(sms_list)
        if not temp:
            message = u'Danh sách tin nhắn gửi lên không đúng'
            success = False
            HttpResponse(simplejson.dumps({
                'message': message,
                'success': success}, mimetype='json'))
        else:
            sms_list = sms_list.split('*')
            number = 0
            for s in sms_list:
                if s:
                    try:
                        temp = s.split('-')
                        s_id = temp[0]
                        s_status = temp[1]
                        the_sms = sms.objects.get(id=s_id)
                        if s_status.lower() == 'ok':
                            the_sms.recent = False
                            the_sms.success = True
                            the_sms.save()
                        else:
                            the_sms.recent = False
                            the_sms.success = False
                            the_sms.save()
                        number += 1
                    except Exception:
                        pass
            message = u'Đã cập nhật thành công %d tin nhắn ' % number
            success = True
            return HttpResponse(simplejson.dumps({
                'message': message,
                'success': success}), mimetype='json')

class MySms(View):
    @need_login
    def get(self, request, from_date=None):
        user = request.user
        try:
            from_date = to_date(from_date)
        except Exception:
            message = u'Ngày cần theo dạng dd-mm-yyyy'
            success = False
            HttpResponse(simplejson.dumps({
                'message': message,
                'success': success}, mimetype='json'))

        smses = sms.objects.filter(sender=user,
                created__gte=from_date)

        result = []
        for s in smses:
            print s.receiver
            result.append({
                'id': s.id,
                'phone': s.phone,
                'receiver': s.receiver.username if s.receiver else '',
                'success': s.success,
                'recent': s.recent,
                'content': s.content})

        for s in smses:
            s.recent = True
            s.save()
        return HttpResponse(simplejson.dumps({
            'message': u'Nhận %d tin nhắn' % len(smses),
            'smses': result,
            'success': True}), mimetype='json')

class SmsSummary(View):
    @need_login
    @school_function
    @operating_permission([u'HIEU_TRUONG', u'HIEU_PHO'])
    def get(self, request, class_id=None):
        school = get_school(request)
        try:
            if class_id:
                cl = Class.objects.get(id=class_id)
                if cl.year_id.school_id != school:
                    raise Exception("BadRequest")
        except ObjectDoesNotExist:
            message = u'Lớp học không tồn tại'
            success = False
            HttpResponse(simplejson.dumps({
                'message': message,
                'success': success}, mimetype='json'))
        term = get_current_term(request)
        info_list, students, subjects = cl._generate_mark_summary(term)
        result = {
            'infoList': info_list,
            'students': students}
        return Response(status.HTTP_200_OK, content=result)


class hanhkiem(View):
    def get(self, request, class_id):
        if request.user.is_anonymous():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        year = get_current_year(request)
        try:
            _class = Class.objects.filter(
                block_id__school_id=get_school(request)).get(id=class_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        student_list = _class.students()

        list = []
        for student in student_list:
            hanhkiem = student.tbnam_set.get(year_id__exact=year.id)
            s = {
                'id': student.id,
                'firstName': student.first_name,
                'lastName': student.last_name,
                'DOB': student.birthday,
                'sex': student.sex,
                'phone': student.phone,
                'smsPhone': student.sms_phone,
                'email': student.email,
                }
            FieldList = ['hk_thang_9', 'hk_thang_10', 'hk_thang_11', 'hk_thang_12', 'hk_thang_1', 'hk_thang_2',
                         'hk_thang_3', 'hk_thang_4', 'hk_thang_5', 'term1', 'term2', 'year', 'hk_ren_luyen_lai']
            for i in FieldList:
                s[i] = getattr(hanhkiem, i)
            list.append(s)
        #return Response(status=status.HTTP_200_OK, content=list)
        return HttpResponse(simplejson.dumps(list), mimetype='json')


    @need_login
    @operating_permission(['HIEU_PHO', 'HIEU_TRUONG', 'GIAO_VIEN'])
    @transaction.commit_manually
    def post(self, request):
        """
        3. def for post HanhKiem to server:
          post:
          "classId": "xxx"
          "list":"studentId-field-status%studentId-field-status%studentId-field-status%studentId-field-status%"

        status la muc hanh kiem, (u'', u'Chưa xét'), (u'T', u'Tốt'), (u'K', u'Khá'), (u'TB',u'TB'), (u'Y', u'Yếu')
        field in FieldList
        """
        class_id = request.POST['classId']
        data = request.POST['list']
        list = data.split("%")
        term = get_current_term(request)
        try:
            _class = Class.objects.get(id=int(class_id))
        except ObjectDoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        if (is_teacher(request)
            and request.user.teacher in _class.associated_teacher()):
            try:
                for ul in list:
                    p_id = int(ul.split('-')[0].strip())
                    field = ul.split('-')[1].strip()
                    type = ul.split('-')[2].strip().upper()

                    p = _class.pupil_set.get(id=int(p_id))
                    hk = p.tbnam_set.get(year_id=_class.year_id.id)

                    valid_value = ['T', 'K', 'TB', 'Y', '']
                    FieldList = ['hk_thang_9', 'hk_thang_10', 'hk_thang_11', 'hk_thang_12', 'hk_thang_1', 'hk_thang_2',
                                 'hk_thang_3', 'hk_thang_4', 'hk_thang_5', 'term1', 'term2', 'year', 'hk_ren_luyen_lai']
                    if not (field in FieldList):
                        raise Exception("Bad request")
                    if not (type in valid_value):
                        raise Exception("Bad request")

                    if term.number == 1:
                        if field in ['year', 'term2']:
                            raise Exception("Bad request")

                    setattr(hk, field, type)
                    hk.save()
            except Exception as e:
                print e
                raise e
                return Response(status.HTTP_400_BAD_REQUEST)
            transaction.commit()
        else:
            return Response(status.HTTP_403_FORBIDDEN)


def get_schedule_for_teacher(request):
    current_year = get_current_year(request)
    tc = get_teacher(request)
    subjects = Subject.objects.filter(teacher_id=tc, class_id__year_id=current_year)
    table = [0] * 8

    for day in range(2, 8):
        temp = [0] * 11
        for i in range(11):
            temp[i] = []
        table[day] = temp

    for day in range(2, 8):
        print table[day]
    for s in subjects:
        cl = s.class_id
        schedules = cl.tkb_set.all().order_by("day")
        print len(schedules)
        for sch in schedules:
            print sch.day
            for time in range(1, 11):
                sub = getattr(sch, 'period_' + str(time))
                if s == sub:
                    table[sch.day][time].append(sub)
    for day in range(2, 8):
        print table[day]
    result = {}
    for day in range(2, 8):
        aday = []
        for time in range(1, 10):
            for x in table[day][time]:
                a_period = {}
                a_period['time'] = time
                a_period['subject'] = x.name
                a_period['class'] = x.class_id.name
                aday.append(a_period)
        result[day] = aday
    return result


def get_schedule_for_student(request):
    current_year = get_current_year(request)
    pupil = get_student(request)
    cl = pupil.current_class()
    schedules = cl.tkb_set.all().order_by("day")
    result = {}

    for (i, s) in enumerate(schedules):
        aday = []
        for time in range(1, 10):
            sub = getattr(s, 'period_' + str(time))
            if sub != None:
                a_period = {}
                a_period['time'] = time
                a_period['subject'] = sub.name
                teacher = sub.teacher_id
                if teacher != None:
                    a_period['teacher'] = teacher.last_name + ' ' + teacher.first_name
                else:
                    a_period['teacher'] = ''
                aday.append(a_period)
        result[i + 2] = aday
    return result


class Schedule(View):
    @need_login
    def get(self, request):
        if get_position(request) == 1:
            result = get_schedule_for_student(request)
        elif get_position(request) == 3:
            result = get_schedule_for_teacher(request)
            #return Response(status=status.HTTP_200_OK, content=list)
        return HttpResponse(simplejson.dumps(result), mimetype='json')


class ScheduleForStudent(View):
    @need_login
    def get(self, request):
    #return Response(status=status.HTTP_200_OK, content=list)
        result = ''
        return HttpResponse(simplejson.dumps(result), mimetype='json')


class StudentProfile(View):
    @need_login
    def get(self, request, student_id):
        try:
            student = Pupil.objects.get(id=student_id)
            ttcn_fields = ('last_name', 'first_name', 'birthday',
                           'sex', 'start_year_id', 'birth_place', 'dan_toc',
                           'ton_giao', 'uu_tien', 'quoc_tich', 'home_town',
                           'ban_dk', 'school_join_date', 'school_join_mark')
            ttll_fields = ('current_address', 'phone', 'father_phone',
                           'mother_phone', 'sms_phone', 'email')

            ttgd_fields = ('father_name', 'father_birthday', 'father_job',
                           'mother_name', 'mother_birthday', 'mother_job')

            ttdd_fields = {'doi', 'ngay_vao_doi', 'doan', 'ngay_vao_doan', 'dang', 'ngay_vao_dang'}
            data = {'ttcn': {}, 'ttll': {}, 'ttgd': {}, 'ttdd': {}, 'khenthuong': [], 'kiluat': []}
            for field in ttcn_fields:
                tmp = getattr(student, field)
                data['ttcn'][field] = unicode(tmp)

            for field in ttll_fields:
                tmp = getattr(student, field)
                data['ttll'][field] = unicode(tmp)

            for field in ttgd_fields:
                tmp = getattr(student, field)
                data['ttgd'][field] = unicode(tmp)

            for field in ttdd_fields:
                tmp = getattr(student, field)
                data['ttdd'][field] = unicode(tmp)

            ktl = student.khenthuong_set.order_by('time')
            kll = student.kiluat_set.order_by('time')
            for kt in ktl:
                new_dict = {}
                for field in KhenThuong._meta.get_all_field_names():
                    tmp = getattr(kt, field)
                    new_dict[field] = unicode(tmp)
                data['khenthuong'].append(new_dict)

            for kl in kll:
                new_dict = {}
                for field in KiLuat._meta.get_all_field_names():
                    tmp = getattr(kl, field)
                    new_dict[field] = unicode(tmp)
                data['kiluat'].append(new_dict)

            return HttpResponse(simplejson.dumps(data), mimetype='json')
            #return Response(status=status.HTTP_200_OK, content=list)
        except Exception as e:
            print e
            return Response(status.HTTP_403_FORBIDDEN)


class MarkForASubject(View):
    @need_login
    #@school_function
    #@operating_permission(['HIEU_PHO', 'HIEU_TRUONG', 'GIAO_VIEN'])
    def get(self, request, subject_id, term_number=None):
        selected_subject = Subject.objects.get(id=subject_id)
        year = selected_subject.class_id.year_id
        current_year = get_current_year(request)
        if term_number == None:
            if year != current_year:
                selected_term = Term.objects.get(year_id=year, number=2)
            else:
                selected_term = get_current_term(request, True)
        else:
            selected_term = Term.objects.get(year_id=year, number=term_number)
        time_to_edit = int(selected_term.year_id.school_id.get_setting('lock_time')) * 60
        now = datetime.datetime.now()
        time_now = int((now - CHECKED_DATE).total_seconds() / 60)
        print time_to_edit
        list = []
        marks = Mark.objects.filter(term_id=selected_term.id, subject_id=subject_id, current=True).order_by(
            'student_id__index', 'student_id__first_name', 'student_id__last_name', 'student_id__birthday')
        if selected_term.number == 2:
            before_term = Term.objects.get(year_id=selected_term.year_id, number=1).id
            term1s = Mark.objects.filter(term_id=before_term, subject_id=subject_id, current=True).order_by(
                'student_id__index', 'student_id__first_name', 'student_id__last_name', 'student_id__birthday')
            tbnams = TKMon.objects.filter(subject_id=subject_id, current=True).order_by('student_id__index',
                'student_id__first_name', 'student_id__last_name', 'student_id__birthday')
            # to avoid lazy query
            temp = len(term1s)
            temp = len(tbnams)
        for (t, m) in enumerate(marks):
            adict = {
                "id": int(m.id),
                "lastName": m.student_id.last_name,
                "firstName": m.student_id.first_name
            }

            arr_mark = m.toArrayMark()
            arr_time = m.toArrayTime()
            arr_sent = m.to_array_sent()
            temp_arr = []
            for (i, a) in enumerate(arr_mark):
                if a != '':
                    a_mark = {
                        'n': i,
                        'm': a
                    }
                    if arr_sent[i] == '1':
                        a_mark['s'] = 1
                    else:
                        a_mark['s'] = 0
                    if (time_now - int(arr_time[i]) > time_to_edit):
                        a_mark['e'] = 0
                    else:
                        a_mark['e'] = 1

                    temp_arr.append(a_mark)

            if m.ck != None:
                a_mark = {
                    'n': 3 * MAX_COL + 1,
                    'm': m.ck
                }

                if arr_sent[3 * MAX_COL + 1] == '1':
                    a_mark['s'] = 1
                else:
                    a_mark['s'] = 0

                if (time_now - int(arr_time[3 * MAX_COL + 1]) > time_to_edit):
                    a_mark['e'] = 0
                else:
                    a_mark['e'] = 1

                temp_arr.append(a_mark)

            if selected_term.number == 2:
                if term1s[t].tb != None:
                    a_mark = {
                        'n': 3 * MAX_COL + 2,
                        'm': term1s[t].tb
                    }
                    arr_sent1 = term1s[t].to_array_sent()
                    if arr_sent1[3 * MAX_COL + 2] == '1':
                        a_mark['s'] = 1
                    else:
                        a_mark['s'] = 0

                    a_mark['e'] = 0
                    temp_arr.append(a_mark)

            if m.tb != None:
                if selected_term.number == 2:
                    a_mark = {
                        'n': 3 * MAX_COL + 3,
                        'm': m.tb
                    }
                else:
                    a_mark = {
                        'n': 3 * MAX_COL + 2,
                        'm': m.tb
                    }
                if arr_sent[3 * MAX_COL + 2] == '1':
                    a_mark['s'] = 1
                else:
                    a_mark['s'] = 0
                if (time_now - int(arr_time[3 * MAX_COL + 2]) > time_to_edit):
                    a_mark['e'] = 0
                else:
                    a_mark['e'] = 1

                temp_arr.append(a_mark)

            if selected_term.number == 2:
                if tbnams[t].tb_nam != None:
                    a_mark = {
                        'n': 3 * MAX_COL + 4,
                        'm': tbnams[t].tb_nam
                    }
                    if tbnams[t].sent:
                        a_mark['s'] = 1
                    else:
                        a_mark['s'] = 0
                    a_mark['e'] = 0
                    temp_arr.append(a_mark)

            adict["mark"] = temp_arr
            list.append(adict)
            #print list
        #return Response(status=status.HTTP_200_OK, content=list)
        return HttpResponse(simplejson.dumps(list), mimetype='json')


    @need_login
    def post(self, request):
        tt1 = time.time()
        data = request.POST['data']
        #data = '[{"first_name": "\u00c1nh", "last_name": "\u0110\u1eb7ng Ng\u1ecdc", "id": 602038, "mark": [{"e": 1, "s": 0, "m": "5", "n": 1}, {"e": 1, "s": 0, "m": "6", "n": 2}, {"e": 1, "s": 0, "m": "6", "n": 3}, {"e": 1, "s": 0, "m": "2", "n": 4}, {"e": 1, "s": 0, "m": "9", "n": 9}]}]'
        data = eval(data)
        teacher = get_teacher(request)
        position = 3
        user = request.user
        time_history = 60
        for p in data:
            mark_id = p['id']
            selected_mark = Mark.objects.get(id=mark_id)
            subject = selected_mark.subject_id

            temp = str(mark_id) + ':'
            number_str = ''
            mark_str = ''
            marks = p['mark']
            for m in marks:
                number_str += str(m['n']) + '*'
                mark_str += str(m['m']) + '*'
            temp += number_str + ':' + mark_str
            update_mark(temp, subject.primary, subject.nx, user, time_history, position, None, teacher)
        tt2 = time.time()
        print tt2 - tt1


class MarkForAStudent(View):
    @need_login
    @school_function
    @operating_permission(['HOC_SINH'])
    def get(self, request, student_id, term_id=None):
        if term_id == None:
            term_id = get_current_term(request, except_summer=True).id
            print get_current_term(request, except_summer=True).number
        list = getMarkForAStudent(student_id, term_id)
        #return Response(status=status.HTTP_200_OK, content=list)
        return HttpResponse(simplejson.dumps(list), mimetype='json')

    @need_login
    @operating_permission(['HIEU_PHO', 'HIEU_TRUONG', 'GIAO_VIEN'])
    def post(self, request):
        pass


class GetListTerm(View):
    @need_login
    def get(self, request):
        school = request.user.userprofile.organization
        terms = Term.objects.filter(year_id__school_id=school).order_by("year_id__time", "number")
        list = []
        for term in terms:
            if term.number != 3:
                a_term = {}
                a_term['termId'] = term.id
                a_term['year'] = term.year_id.time
                a_term['number'] = term.number
                list.append(a_term)
        return HttpResponse(simplejson.dumps(list), mimetype='json')


class GetAttendanceForStudent(View):
    @need_login
    def get(self, request, all=None, day=None, month=None, year=None, day1=None, month1=None, year1=None):
        student = get_student(request)
        if all == 'allTerm':
            current_term = get_current_term(request)
            attendaces = DiemDanh.objects.filter(student_id=student, term_id=current_term).order_by("time")
        elif all == 'allYear':
            current_year = get_current_year(request)
            term1 = Term.objects.get(year_id=current_year, number=1)
            term2 = Term.objects.get(year_id=current_year, number=2)
            attendaces = DiemDanh.objects.filter(student_id=student, term_id__in=[term1.id, term2.id]).order_by("time")
        elif all != None:
            raise Exception("Page not found")
        else:
            first_day = datetime.datetime(int(year), int(month), int(day))
            second_day = datetime.datetime(int(year1), int(month1), int(day1))
            attendaces = DiemDanh.objects.filter(student_id=student, time__range=(first_day, second_day)).order_by(
                "time")
        result = []
        for att in attendaces:
            a_att = {}
            a_att['time'] = att.time.strftime("%d/%m/%Y")
            a_att['type'] = att.loai
            a_att['sent'] = att.sent
            result.append(a_att)

        return HttpResponse(simplejson.dumps(result), mimetype='json')


class GetSubjectOfHomeroomTeacher(View):
    @need_login
    @operating_permission(['GIAO_VIEN'])

    def get(self, request):
        teacher = get_teacher(request)
        homeroom_class = teacher.current_homeroom_class()
        result = []
        if homeroom_class != None:
            subjects = Subject.objects.filter(class_id=homeroom_class)
            for subject in subjects:
                a_subject = {
                    'subjectId': subject.id,
                    'isComment': subject.nx,
                    'classId': homeroom_class.id,
                    'className': homeroom_class.name,
                    'subject': subject.name,
                    #'size': h.number_of_pupils(),
                }
                result.append(a_subject)
        return HttpResponse(simplejson.dumps(result), mimetype='json')

