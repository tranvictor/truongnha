# coding: utf8
__author__ = 'vutran'
from django.core.serializers.json import DjangoJSONEncoder
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
from school.models import Class, Pupil, Term, Subject, DiemDanh, TBNam, TKB,\
    KhenThuong, KiLuat
from school.utils import get_position, get_school, is_teacher,\
    get_current_term, get_current_year
from school.forms import MarkForm
from decorators import need_login, operating_permission, school_function
import simplejson
import datetime
import re
from school.templateExcel import  MAX_COL, CHECKED_DATE, normalize

class ApiLogin(View):
    """
    A basic view, that can be handle GET and POST requests.
    Applies some simple form validation on POST requests.
    """

    def get(self, request):
        response = login(request, api_called=True)
        if response.status_code == 200:
            data = {
                'csrfmiddlewaretoken': get_token(request)
            }
            return HttpResponse(simplejson.dumps(data), mimetype='json')
        else:
            return Response(status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        response = login(request, api_called=True)
        if response.status_code == 200:
            result = {}
            try:
                user_position = get_position(request)
                user = None
                if user_position == 1:
                    user = {
                        'type': user_position,
                        'last_name': request.user.last_name,
                        'first_name': request.user.first_name,
                        'class': request.user.pupil.class_id,
                        'school': get_school(request).name,
                        'birth': request.user.pupil.birthday
                    }
                elif user_position in [2, 3]:
                    user = {
                        'type': user_position,
                        'last_name': request.user.last_name,
                        'first_name': request.user.first_name,
                        'school': get_school(request).name,
                        'birth': request.user.teacher.birthday
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
            if user_position < 3:
                #TODO: return necessary information for students
                return Response(status=status.HTTP_404_NOT_FOUND)
            elif user_position == 3:
                try:
                    teaching_subjects = request.user.teacher.teaching_subject()
                    result['teaching_class'] = {}
                    classes = []
                    for subject in teaching_subjects:
                        temp = {
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
                    result['teaching_class'] = classes

                except Exception as e:
                    print e
                    raise e
            elif user_position > 3:
                #TODO: return necessary information for school's admins
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_200_OK, content=result)
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
            return Response(status=status.HTTP_200_OK, content=result)
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
                'firstname': student.first_name,
                'lastname': student.last_name,
                'DOB': student.birthday,
                'sex': student.sex,
                'phone': student.phone,
                'sms_phone': student.sms_phone,
                'email': student.email,
                'status': sta}
            list.append(s)
        return Response(status=status.HTTP_200_OK, content=list)

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


class Subject(View):
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
                'number_lession': s.number_lession,
                'teacher': s.teacher_id.full_name()})
        return Response(status=status.HTTP_200_OK, content=result)


class Mark(View):
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
        return Response(status=status.HTTP_200_OK, content=result)

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
            'info_list': info_list,
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
                'firstname': student.first_name,
                'lastname': student.last_name,
                'DOB': student.birthday,
                'sex': student.sex,
                'phone': student.phone,
                'sms_phone': student.sms_phone,
                'email': student.email,
                }
            FieldList = ['hk_thang_9', 'hk_thang_10', 'hk_thang_11', 'hk_thang_12', 'hk_thang_1', 'hk_thang_2',
                         'hk_thang_3', 'hk_thang_4', 'hk_thang_5', 'term1', 'term2', 'year', 'hk_ren_luyen_lai']
            for i in FieldList:
                s[i] = getattr(hanhkiem, i)
            list.append(s)
        return Response(status=status.HTTP_200_OK, content=list)

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

                    p = c.pupil_set.get(id=int(p_id))
                    hk = p.tbnam_set.get(year_id__exact=year.id)

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


class Schedule(View):
    @need_login
    def get(self, request):
        try:
            year = get_current_year(request)
            classList = year.class_set.all().order_by('name')
            table = {}
            for d in range(2, 8):
                table[d] = []
            for cl in classList:
                for d in range(2, 8):
                    tmp = None
                    try:
                        tmp = cl.tkb_set.get(day=d)
                    except Exception as e:
                        tmp = TKB()
                        tmp.day = d
                        tmp.class_id = cl
                        tmp.save()
                    for field in range(1, 11):
                        sub = getattr(tmp, 'period_' + str(field))
                        if not sub: continue
                        new_dict = {'class': cl.name, 'subject': sub.name, 'time': field}
                        table[d].append(new_dict)
                    if tmp.chaoco:
                        new_dict = {'class': cl.name, 'subject': u'Chào cờ', 'time': tmp.chaoco}
                        table[d].append(new_dict)
                    if tmp.sinhhoat:
                        new_dict = {'class': cl.name, 'subject': u'Sinh hoạt', 'time': tmp.sinhhoat}
                        table[d].append(new_dict)
            return HttpResponse(simplejson.dumps(table), mimetype='json')
        except Exception as e:
            print e
            return Response(status.HTTP_403_FORBIDDEN)


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
        #            return Response(status=status.HTTP_200_OK, content=list)
        except Exception as e:
            print e
            return Response(status.HTTP_403_FORBIDDEN)


class MarkForASubject(View):
    @need_login
    @school_function
    @operating_permission(['HIEU_PHO', 'HIEU_TRUONG', 'GIAO_VIEN'])
    def get(self, request, subject_id, term_id):
        selected_subject = Subject.objects.get(id=subject_id)
        selected_term = Term.objects.get(id=term_id)
        time_to_edit = int(selected_term.year_id.school_id.get_setting('lock_time')) * 60
        now = datetime.datetime.now()
        time_now = int((now - CHECKED_DATE).total_seconds() / 60)
        print time_to_edit
        list = []
        marks = Mark.objects.filter(term_id=term_id, subject_id=subject_id, current=True).order_by(
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
            adict = {}
            adict.update({"id": int(m.id)})
            adict.update({"last_name": m.student_id.last_name})
            adict.update({"first_name": m.student_id.first_name})

            arr_mark = m.toArrayMark()
            arr_time = m.toArrayTime()
            arr_sent = m.to_array_sent()
            temp_arr = []
            for (i, a) in enumerate(arr_mark):
                if a != '':
                    a_mark = {}
                    a_mark.update({'n': i})
                    a_mark.update({'m': a})
                    if arr_sent[i] == '1':
                        a_mark.update({'s': 1})
                    else:
                        a_mark.update({'s': 0})
                    if (time_now - int(arr_time[i]) > time_to_edit):
                        a_mark.update({'e': 0})
                    else:
                        a_mark.update({'e': 1})

                    temp_arr.append(a_mark)

            if m.ck != None:
                a_mark = {}
                a_mark.update({'n': 3 * MAX_COL + 1})
                a_mark.update({'m': m.ck})

                if arr_sent[3 * MAX_COL + 1] == '1':
                    a_mark.update({'s': 1})
                else:
                    a_mark.update({'s': 0})

                if (time_now - int(arr_time[3 * MAX_COL + 1]) > time_to_edit):
                    a_mark.update({'e': 0})
                else:
                    a_mark.update({'e': 1})

                temp_arr.append(a_mark)

            if selected_term.number == 2:
                if term1s[t].tb != None:
                    a_mark = {}
                    a_mark.update({'n': 3 * MAX_COL + 2})
                    a_mark.update({'m': term1s[t].tb})
                    arr_sent1 = term1s[t].to_array_sent()
                    if arr_sent1[3 * MAX_COL + 2] == '1':
                        a_mark.update({'s': 1})
                    else:
                        a_mark.update({'s': 0})

                    a_mark.update({'e': 0})
                    temp_arr.append(a_mark)

            if m.tb != None:
                a_mark = {}
                a_mark.update({'n': 3 * MAX_COL + 3})
                a_mark.update({'m': m.tb})
                if arr_sent[3 * MAX_COL + 2] == '1':
                    a_mark.update({'s': 1})
                else:
                    a_mark.update({'s': 0})

                if (time_now - int(arr_time[3 * MAX_COL + 2]) > time_to_edit):
                    a_mark.update({'e': 0})
                else:
                    a_mark.update({'e': 1})

                temp_arr.append(a_mark)

            if selected_term.number == 2:
                if tbnams[t].tb_nam != None:
                    a_mark = {}
                    a_mark.update({'n': 3 * MAX_COL + 4})
                    a_mark.update({'m': tbnams[t].tb_nam})
                    if tbnams[t].sent:
                        a_mark.update({'s': 1})
                    else:
                        a_mark.update({'s': 0})
                    a_mark.update({'e': 0})
                    temp_arr.append(a_mark)

            adict.update({"mark": temp_arr})
            list.append(adict)
        return Response(status=status.HTTP_200_OK, content=list)

    @need_login
    @operating_permission(['HIEU_PHO', 'HIEU_TRUONG', 'GIAO_VIEN'])
    def post(self, request):
        pass


class MarkForAStudent(View):
    @need_login
    @school_function
    @operating_permission(['HOC_SINH'])
    def get(self, request, student_id, term_id=None):
        if term_id == None:
            term_id = get_current_term(request)
        selected_term = Term.objects.get(id=term_id)
        marks = Mark.objects.filter(term_id=term_id, student_id=student_id).order_by("subject_id__index",
            "subject_id__name")
        if selected_term.number == 2:
            before_term = Term.objects.get(year_id=selected_term.year_id,number=1)
            term1s = Mark.objects.filter(term_id=before_term, student_id=student_id).order_by("subject_id__index",
                "subject_id__name")
            tbnams = TKMon.objects.filter(student_id=student_id)

        list = []
        for m in marks:
            a_subject = {}
            subject = m.subject_id
            a_subject.update({"id":subject_id})
            a_subject.update({"name":subject.name})
            arr_mark = m.toArrayMark()
            temp_mark = []
            for (i,a) in enumerate(arr_mark):
                if a != '' :
                    a_mark = {}
                    a_mark.update({"n":i})
                    a_mark.update({"m":normalize(a,subject.nx)})
                    temp_mark.append(a_mark)
            if m.ck != None:
                a_mark = {}
                a_mark.update({"n":3*MAX_COL+1})
                a_mark.update({"m":normalize(m.ck,subject.nx)})
                temp_mark.append(a_mark)
            if selected_term.number == 2:
                term1 = Mark.objects.get(student_id=student_id,term_id=before_term,subject_id=subject)
                if term1.tb != None:
                    a_mark = {}
                    a_mark.update({"n":3*MAX_COL+2})
                    a_mark.update({"m":normalize(term1.tb,subject.nx)})
                    temp_mark.append(a_mark)
            if m.tb != None:
                a_mark = {}
                a_mark.update({"n":3*MAX_COL+3})
                a_mark.update({"m":normalize(m.tb,subject.nx)})
                temp_mark.append(a_mark)
            if selected_term.number == 2:
                tbnam = TKMon.objects.get(student_id=student_id,subject_id=subject)
                a_mark = {}
                a_mark.update({"n":3*MAX_COL+4})
                a_mark.update({"m":normalize(tbnam.tb_nam,subject.nx)})
                temp_mark.append(a_mark)

            a_subject.update({"mark":temp_mark})
            list.append(a_subject)
        return Response(status=status.HTTP_200_OK, content=list)

    @need_login
    @operating_permission(['HIEU_PHO', 'HIEU_TRUONG', 'GIAO_VIEN'])
    def post(self, request):
        pass
