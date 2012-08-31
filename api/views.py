__author__ = 'vutran'
from djangorestframework.views import View
from djangorestframework.response import Response
from djangorestframework import status
from django.contrib.auth.views import logout
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.core.exceptions import ObjectDoesNotExist
from app.views import login
from school.class_functions import dd
from school.models import Class, Pupil, Term, Subject, DiemDanh
from school.utils import get_position, get_school, is_teacher
from school.forms import MarkForm
from decorators import need_login, operating_permission, school_function
import simplejson
import datetime
import re
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
                elif user_position in [2,3]:
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
                        temp ={
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
            return Response(status=status.HTTP_200_OK, content= result)
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
        if position >=3:
            try:
                _class = Class.objects.filter(
                        block_id__school_id=get_school(request)).get(id=class_id)
            except ObjectDoesNotExist:
                return Response(status.HTTP_400_BAD_REQUEST)
            if all: student_list = _class.attended_student()
            else: student_list = _class.students()
            result ={
                'SUBJECT':'Ten Mon hoc' # Vu~ cho ten mon hoc vao day cai :|
            }
            list = []
            for student in student_list:
                s = {
                    'id': student.id,
                    'name': student.last_name +' '+ student.first_name,
                    'sex': student.sex,
                    'birth': student.birthday
                }
                list.append(s)
            result['list']=list
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
                    time = date.date())
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
            _class = Class.objects.get(id = int(class_id))
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
                    content={'error':'JsonStringNotFormed'})
        ids = data.keys()
        marks = Mark.objects.filter(id__in=ids)
        for m in marks:
            form = MarkForm(data[m.id], instance=m)
            if form.is_valid():
                form.save()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                        content={'error':'MarkNotValid'})
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
        classes =cl_label_re.findall(cl_labels)
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
        data = { 'success': success, 'setting': setting}
        return Response(status.HTTP_200_OK, content=data)

