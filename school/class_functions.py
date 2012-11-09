# coding=utf-8
import os
import string
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect,\
                        HttpResponseNotFound, HttpResponseBadRequest
from django.template import loader, RequestContext
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils import simplejson
from django.shortcuts import render_to_response
from sms.utils import sendSMS, send_email, send_SMS_then_email
from decorators import need_login, school_function, operating_permission
from school.utils import get_position, gvcn, inClass, in_school,\
        get_student, get_current_term, get_school, get_current_year,\
        add_subject, completely_del_student, completely_del_subject, to_en1,\
        to_date, add_student, move_student, get_lower_bound, get_upper_bound
from school.models import Class, Pupil, StartYear, validate_phone, Term,\
        Teacher, Subject, DiemDanh, KhenThuong, KiLuat, UncategorizedClass,\
        this_year, Block, Year
from school.forms import PupilForm, SubjectForm, TBNam, TBNamForm,\
        DiemDanhForm, DateAndClassForm, KhenThuongForm, KiLuatForm, DDForm
from datetime import date, timedelta
from itertools import chain

UNC_CLASS = os.path.join('school', 'unc_class_detail.html')

@need_login
@school_function
@operating_permission([u'HIEU_TRUONG', u'HIEU_PHO'])
def viewUncategorizedClassDetail(request, class_id, l_class_id=None):
    school = get_school(request)
    year = school.get_current_year()
    try:
        last_year = Year.objects.get(school_id=school, time=year.time-1)
        cl_list = last_year.class_set.order_by('name')
    except ObjectDoesNotExist:
        cl_list = []
    try:
        unc_cl = UncategorizedClass.objects.get(id=class_id)
        last_year = Year.objects.get(school_id=school, time=year.time-1)
        number = unc_cl.block_id.number
        cl_list1 = last_year.class_set.filter(block_id__number=number)\
                    .order_by('name')
        cl_list2 = last_year.class_set.filter(block_id__number=number-1)\
                    .order_by('name')
        cl_list = list(chain(cl_list1, cl_list2))
        if not l_class_id:
            for i in range(0, len(cl_list)):
                number = cl_list[i].student_set\
                        .filter(attend__leave_time=None)\
                        .count()
                if number:
                    l_class = cl_list[i]
                    break
        else:
            l_class = Class.objects.get(id=l_class_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    cls1 = year.class_set.filter(block_id__number = unc_cl.block_id.number)
    cls2 = year.class_set.filter(block_id__number = unc_cl.block_id.number + 1)
    students = l_class.student_set.filter(attend__leave_time=None)
    if request.method == 'POST':
        if request.is_ajax():
            if not 'request_type' in request.POST:
                return HttpResponseNotFound()
            if request.POST['request_type'] == 'classify':
                sts = request.POST['students'].split('-')
                try:
                    cl = year.class_set.get(id=request.POST['class_id'])
                    number = 0
                    for st in sts:
                        if st.strip():
                            student = students.get(id = st)
                            move_student(school, student, cl)
                            number += 1
                    data = {'success': True,
                            'message': u'Đã chuyển xong %d học sinh' % (number)}
                except Class.DoesNotExist:
                    data = {'success': False,
                            'message': u'Lớp học không tồn tại'}
                except Pupil.DoesNotExist:
                    data = {'success': False,
                            'message': u'Học sinh không tồn tại'}
                return HttpResponse(simplejson.dumps(data), mimetype='json')
            elif request.POST['request_type'] == 'graduate':
                upper = get_upper_bound(school) - 1
                sts = request.POST['students'].split('-')
                number = 0
                refused = 0
                for st in sts:
                    if st.strip():
                        student = students.get(id = st)
                        if student.current_class().block_id.number == upper:
                            student.graduate()
                            number += 1
                        else: refused += 1
                data = {'success': True,
                        'refused': refused,
                        'number': number,
                        'message': u'Đã duyệt tốt nghiệp cho %d học sinh' % (number)}
                return HttpResponse(simplejson.dumps(data), mimetype='json')

            else: return HttpResponseNotFound()
    return render_to_response(UNC_CLASS, {'students': students,
                                          'cls1': cls1,
                                          'cls2': cls2,
                                          'cl_list': cl_list,
                                          'selected_cl': l_class,
                                          'class': unc_cl},
                                         context_instance=RequestContext(request)) 
    
#User: loi.luuthe@gmail.com
#This function has class_id is an int argument.
#It gets the information of the class corresponding to the class_id and response
#to the template
#This function takes operations: del, send_sms, add
@need_login
@school_function
def viewClassDetail(request, class_id):
    user = request.user
    pos = get_position(request)
    try:
        cl = Class.objects.get(id=class_id)
        this_y = get_current_year(request)
        move_to_cls = cl.block_id.class_set.filter(year_id = this_y)\
                .exclude(id=class_id)\
                .order_by('index')
        bl1 = Block.objects.filter(number = cl.block_id.number +1,
                school_id = cl.block_id.school_id)
        move_to_cls1 = []
        if bl1:
            move_to_cls1 = bl1[0].class_set.filter(year_id = this_y)\
                    .exclude(id=class_id)\
                    .order_by('index')
    except Class.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))
    default_year = int(date.today().year) - cl.block_id.number - 6
    default_date = '01/01/' + str(default_year)
    cn = gvcn(request, cl)
    #inClass(request, class_id)
    if not in_school(request, cl.block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    message = None
    school = cl.block_id.school_id
    cyear = get_current_year(request)
    classList = cyear.class_set.all().order_by('name')
    form = PupilForm(school.id)

    if request.method == 'POST':
        if request.is_ajax():
            if request.POST[u'request_type'] == u'del' and pos > 3:
                data = request.POST[u'data']
                data = data.split('-')
                for e in data:
                    if e.strip():
                        std = school.pupil_set.get(id__exact=int(e))
                        completely_del_student(std)

                data = simplejson.dumps({'success': True})
                return HttpResponse(data, mimetype='json')
            elif request.POST[u'request_type'] == u'send_sms':
                try:
                    content = request.POST[u'content'].strip()
                    include_name = request.POST[u'include_name']
                    student_list = request.POST[u'student_list']
                    student_list = student_list.split("-")
                    sts = []
                    for student in student_list:
                        if student:
                            sts.append(int(student))
                    students = Pupil.objects.filter(id__in=sts)
                    number_of_sent = 0
                    number_of_blank = 0
                    number_of_failed = 0
                    number_of_email_sent = 0
                    for student in students:
                        if student.sms_phone:
                            try:
                                if include_name == 'true':
                                    send_SMS_then_email(
                                            student.sms_phone,
                                            to_en1('Em ' + student.short_name() +\
                                                    ' ' + content),
                                            user,
                                            student.user_id,
                                            True,
                                            school,
                                            u'Trường Nhà thông báo',
                                            content,
                                            to_addr=[student.email]) 
                                else:
                                    send_SMS_then_email(
                                            student.sms_phone,
                                            to_en1(content),
                                            user,
                                            student.user_id,
                                            True,
                                            school,
                                            u'Trường Nhà thông báo',
                                            content,
                                            to_addr=[student.email]) 
                                number_of_sent += 1
                            except Exception as e:
                                print e
                                number_of_failed += 1
                        else:
                            number_of_blank += 1
                            if student.email:
                                try:
                                    send_email(
                                            u'Trường Nhà thông báo',
                                            content,
                                            to_addr=[student.email])
                                    number_of_email_sent += 1
                                except Exception:
                                    pass
                    data = simplejson.dumps({
                        'number_of_sent': number_of_sent,
                        'number_of_blank': number_of_blank,
                        'number_of_failed': number_of_failed,
                        'number_of_email_sent': number_of_email_sent,
                    })
                    return HttpResponse(data, mimetype='json')
                except Exception as e:
                    print e
                    raise e

            elif request.POST[u'request_type'] == u'add' and pos > 3:
                start_year = StartYear.objects.filter(school_id=school.id)\
                        .latest('time')
                lb = get_lower_bound(school)
                syear = this_year() - cl.block_id.number + lb
                start_year, temp = StartYear.objects.get_or_create(
                        time=syear, school_id=school)
                data = None
                try:
                    data = {'first_name': request.POST['first_name'],
                            'last_name': request.POST['last_name'],
                            'birthday': request.POST['birthday'],
                            'sex': request.POST['sex'],
                            'birth_place': request.POST['birth_place'].strip(),
                            'current_address': request.POST['current_address'].strip(),
                            'school_join_date': date.today().strftime("%d/%m/%Y"),
                            'ban_dk': u'CB',
                            'dan_toc':request.POST['dan_toc'],
                            'quoc_tich': u'Việt Nam',
                            'index': cl.pupil_set.count() + 1,
                            'class_id': int(class_id),
                            'start_year_id': start_year.id,
                            'mother_name': request.POST['mother_name'].strip(),
                            'father_name': request.POST['father_name'].strip(),
                            'sms_phone': request.POST['sms_phone']}
                except Exception as e:
                    print e
                form = PupilForm(school.id, data)
                if form.is_valid():
                    school_join_date = date.today()
                    birthday = to_date(request.POST['birthday'])
                    data['birthday'] = birthday
                    _class = Class.objects.get(id=class_id)
                    index = _class.max + 1
                    added, student = add_student(student=data, start_year=start_year,
                            year=get_current_year(request),
                            _class=_class,
                            index=index,
                            term=get_current_term(request),
                            school=get_school(request),
                            school_join_date=school_join_date)

                    if not added:
                            message = u'<li>Học sinh đã tồn tại ở lớp %s</li>'\
                                    % student.current_class()
                            data = simplejson.dumps({'message': message})
                            return HttpResponse(data, mimetype='json')
                    else:
                        temp = os.path.join('school','classDetail_one_student.html')
                        count = _class.number_of_pupils()
                        student_detail = render_to_string(temp, {'student':student,
                                                                'count':count})
                        message = u'Bạn vừa thêm 1 học sinh'
                        data = simplejson.dumps({'message': message,
                                                 'success': True,
                                                 'student_detail': student_detail})
                        return HttpResponse(data, mimetype='json')
                    #form = PupilForm(school.id)
                else:
                    message = ''
                    try:
                        birthday = to_date(request.POST['birthday'])
                        if birthday >= date.today():
                            message += u'<li> ' + u'Ngày không hợp lệ' + u'</li>'
                        find = start_year.pupil_set.filter(
                                first_name__exact=request.POST['first_name'])\
                                .filter(last_name__exact=request.POST['last_name'])\
                                .filter(birthday__exact=birthday)
                        if find:
                            message += u'<li> ' + u'Học sinh đã tồn tại' + u'</li>'
                    except Exception as e:
                        message = u'<li> ' + u'Chưa nhập hoặc nhập không đúng định dạng "ngày/tháng/năm" ' + u'</li>'
                        print e

                    try:
                        if data['sms_phone']:
                            validate_phone(data['sms_phone'])
                    except Exception as e:
                        message = u'<li> ' + u'Số điện thoại không tồn tại' + u'</li>'
                        print e

                    if not request.POST['first_name']:
                        message += u'<li> ' + u'Ô tên là bắt buộc' + u'</li>'

                    data = simplejson.dumps({'message': message})
                    return HttpResponse(data, mimetype='json')

    student_list = cl.students().order_by('index', 'first_name', 'last_name', 'birthday')
    user_id_list = [ss.user_id_id for ss in student_list]
    user_list = User.objects.filter(id__in = user_id_list)
    active_list = {}
    for user in user_list:
        active_list[user.id] = user.is_active
    tmp = get_student(request)
    inCl = inClass(request, class_id)
    id = 0
    if tmp:
        id = tmp.id

    currentTerm = cyear.term_set.get(number=school.status)
    if currentTerm.number == 3:
        currentTerm = Term.objects.get(year_id=currentTerm.year_id, number=2)
    if cl.year_id != currentTerm.year_id :
        selected_term = Term.objects.get(year_id=cl.year_id, number=2)
    else:
        selected_term = currentTerm
    t = loader.get_template(os.path.join('school', 'classDetail.html'))
    c = RequestContext(request, {'form': form,
                                 'message': message,
                                 'studentList': student_list,
                                 'class': cl,
                                 'cl': classList,
                                 'inClass': inCl,
                                 'pos': pos,
                                 'gvcn': cn,
                                 'student_id': id,
                                 'currentTerm': currentTerm,
                                 'selected_term':selected_term,
                                 'move_to_cls': move_to_cls,
                                 'move_to_cls1': move_to_cls1,
                                 'default_date': default_date,
                                 'active_list' : active_list
    })
    return HttpResponse(t.render(c))

@need_login
@school_function
def subjectPerClass(request, class_id):
    user = request.user
    pos = get_position(request)
    subjectList = None
    if not pos:
        return HttpResponseRedirect(reverse('index'))
    message = None
    cl = Class.objects.get(id=class_id)
    if not in_school(request, cl.block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    if user.userprofile.organization.level == 'S':
        school = cl.year_id.school_id
        year = cl.year_id
        term =  get_current_year(request).term_set.get(number = school.status)
    else:
        term = get_current_term(request)
        school = get_school(request)
        year = get_current_year(request)

    try:
        subjectList = cl.subject_set.order_by('index')
    except Exception as e:
        print e

    form = SubjectForm(school.id)
    sfl = []
    for s in subjectList:
        sfl.append(SubjectForm(school.id, instance=s))
    if request.is_ajax() and pos > 3:
        if request.POST['request_type'] == u'add':
            try:
                max_index_subject = cl.subject_set.order_by('-index')[0]
                index = max_index_subject.index + 1
                nx = request.POST.get('nx', 0)
                data = {'name': request.POST['name'].strip(), 'hs': request.POST['hs'], 'class_id': class_id,
                                            'teacher_id': request.POST['teacher_id'], 'index': index, 'primary': request.POST['primary'], 'type': request.POST['type'], 'nx': nx, 'number_lesson': request.POST['number_lesson']}
                form = SubjectForm(school.id, data)
                if form.is_valid():
                    if request.POST['type'] not in [u'',u'Tự chọn']:
                        subject_count = cl.subject_set.filter(type = request.POST['type']).count()
                        if subject_count > 0:
                            message = u'Đã có môn học cùng loại này.'
                            data = simplejson.dumps({'message': message, 'success' : False})
                            return HttpResponse(data, mimetype='json')
                    try:
                        if request.POST['teacher_id'] != u'':
                            teacher = Teacher.objects.get(id=int(data['teacher_id']))
                            add_subject(subject_name=data['name'], hs=float(data['hs']), teacher=teacher, _class=cl,
                                index=index, subject_type=data['type'], nx=data['nx'], number_lesson=data['number_lesson'])
                            form = SubjectForm(school.id)
                        else:
                            add_subject(subject_name=data['name'], hs=float(data['hs']), _class=cl, index=index,
                                subject_type=data['type'], nx=data['nx'])
                            form = SubjectForm(school.id)
                        message = u'Môn học mới đã được thêm.'
                        success = True
                        data = simplejson.dumps({'message': message, 'success' : success})
                        return HttpResponse(data, mimetype='json')
                    except Exception as e:
                        print e
                        message = u'Tên môn học đã tồn tại.'
                        data = simplejson.dumps({'message': message, 'success' : False})
                        return HttpResponse(data, mimetype='json')
                else:
                    message = u'<ul>'
                    if request.POST['name'] == u'': message += u'<li>Tên môn học phải chứa ít nhất một kí tự.</li>'
                    if int(request.POST['number_lesson']) <= 0: message += u'<li>Số tiết trong một tuần phải lớn hơn 0.</li>'
                    if request.POST['hs'] == u'' or float(request.POST['hs']) <= 0 or float(request.POST['hs']) > 3: message += u'<li>Hệ số phải nằm trong khoảng [0, 3].</li>'
                    message += u'</ul>'
#                    print message
                    data = simplejson.dumps({'message': message})
                    return HttpResponse(data, mimetype='json')
            except Exception as e:
                print e
        sid = request.POST.get('id', None)
        sub = cl.subject_set.get(id=sid)
        if request.POST['request_type'] == u'teacher':
            if request.POST['teacher'] != u'':
                shs = int(request.POST['teacher'])
            else:
                shs = None
            if shs:
                teacher = school.teacher_set.get(id=shs)
            else:
                teacher = None
            sub.teacher_id = teacher
            sub.save()
            message = u'Cập nhật thành công.'
        elif request.POST['request_type'] == u'number_lesson':
            try:
                shs = int(request.POST['value'])
            except Exception:
                message = u'Số tiết phải là số nguyên.'
                data = simplejson.dumps({'message': message})
                return HttpResponse(data, mimetype='json')
            if shs < 0:
                message = u'Số tiết trong một tuần không được nhỏ hơn 0.'
                data = simplejson.dumps({'message': message})
                return HttpResponse(data, mimetype='json')
            elif shs > 10:
                message = u'Số tiết trong một tuần không được lớn hơn 10.'
                data = simplejson.dumps({'message': message})
                return HttpResponse(data, mimetype='json')
            else:
                sub.number_lesson = shs
                sub.save()
                message = u'Cập nhật thành công.'

        if request.POST['request_type'] == u'type':
            if request.POST['type'] != u'':
                type = request.POST['type']
            else:
                type = None
            try:
                sub.type = type
                sub.save()
                message = u'Cập nhật thành công.'
            except Exception as e:
                message = u'Cập nhật không thành công.'
                print e

        elif request.POST['request_type'] == u'primary':
            shs = request.POST['primary']
            sub.primary = shs
            sub.save()
            message = u'Cập nhật thành công.'

        elif request.POST['request_type'] == u'nx':
            try:
                shs = request.POST['nx']
                sub.nx = (shs != u'false')
                sub.save()
                message = u'Cập nhật thành công.'
            except Exception as e:
                print e

        elif request.POST['request_type'] == u'hs':
            try:
                shs = float(request.POST['hs'])
            except Exception:
                message = u'Hệ số phải là số thực.'
                data = simplejson.dumps({'message': message})
                return HttpResponse(data, mimetype='json')

            if shs < 0:
                message = u'Hệ số không được nhỏ hơn 0.'
                data = simplejson.dumps({'message': message})
                return HttpResponse(data, mimetype='json')
            elif shs > 3:
                message = u'Hệ số không được lớn hơn 3.'
                data = simplejson.dumps({'message': message})
                return HttpResponse(data, mimetype='json')
            else:
                sub.hs = shs
                sub.save()
                message = u'Cập nhật thành công.'
        elif request.POST['request_type'] == u'xoa':
            try:
                if sub.type == u'Toán' or sub.type == u'Ngữ văn':
                    message = u'Bad request.'
                else:
                    completely_del_subject(sub)
                    message = u'Đã xóa thành công.'
            except Exception:
                message = u'Bad request'
                data = simplejson.dumps({'message': message})
                return HttpResponse(data, mimetype='json')

        data = simplejson.dumps({'message': message})
        return HttpResponse(data, mimetype='json')


#            data = {'name': request.POST['name'].strip(), 'hs': request.POST['hs'], 'class_id': class_id,
#                    'teacher_id': request.POST['teacher_id'], 'index': index, 'primary': request.POST['primary'], 'type': request.POST['type'], 'nx': nxn, 'number_lesson':}
#            form = SubjectForm(school.id, data)
#            if form.is_valid():
#                _class = Class.objects.get(id=class_id)
#                if teacher_list[i] != u'':
#                    teacher = Teacher.objects.get(id=int(data['teacher_id']))
#                    add_subject(subject_name=data['name'], hs=float(data['hs']), teacher=teacher, _class=_class,
#                        index=index, subject_type=data['type'], nx=data['nx'], number_lesson=data['number_lesson'])
#                    form = SubjectForm(school.id)
#                else:
#                    try:
#                        add_subject(subject_name=data['name'], hs=float(data['hs']), _class=_class, index=index,
#                            subject_type=data['type'], nx=data['nx'])
#                        form = SubjectForm(school.id)
#                        message = u'Môn học mới đã được thêm.'
#                    except Exception as e:
#                        print e
#                        message = u'Môn học đã tồn tại.'

#    elif request.method == 'POST' and pos > 3:
#        hs_list = request.POST.getlist('hs')
#        teacher_list = request.POST.getlist('teacher_id')
#        p_list = request.POST.getlist('primary')
#        t_list = request.POST.getlist('type')
#        nx_list = request.POST.getlist('nx')
#        number_list = request.POST.getlist('number_lesson')
#        i = 0
#        j = 0
#        for s in subjectList:
#            data = {'name': s.name, 'hs': hs_list[i], 'class_id': class_id, 'teacher_id': teacher_list[i], 'index': i,
#                    'primary': p_list[i], 'type': s.type, 'nx': s.nx, 'number_lesson':number_list[i]}
#            if s.nx:
#                j += 1
#            of = sfl[i]
#            sfl[i] = SubjectForm(school.id, data, instance=s)
#            if str(of) != str(sfl[i]):
#                if sfl[i].is_valid():
#                    sfl[i].save()
#                    message = 'Danh sách môn học đã được cập nhật.'
#            i += 1
#        if teacher_list[i] != u'' or request.POST['name'].strip() != u'' or hs_list[i] != u'':
#            index = i + 1
#            nxn = False
#            if len(nx_list) > j:
#                nxn = True
#
#            data = {'name': request.POST['name'].strip(), 'hs': hs_list[i], 'class_id': class_id,
#                    'teacher_id': teacher_list[i], 'index': index, 'primary': p_list[i], 'type': t_list[0], 'nx': nxn, 'number_lesson':number_list[i]}
#            form = SubjectForm(school.id, data)
#            if form.is_valid():
#                _class = Class.objects.get(id=class_id)
#                if teacher_list[i] != u'':
#                    teacher = Teacher.objects.get(id=int(data['teacher_id']))
#                    add_subject(subject_name=data['name'], hs=float(data['hs']), teacher=teacher, _class=_class,
#                        index=index, subject_type=data['type'], nx=data['nx'], number_lesson=data['number_lesson'])
#                    form = SubjectForm(school.id)
#                else:
#                    try:
#                        add_subject(subject_name=data['name'], hs=float(data['hs']), _class=_class, index=index,
#                            subject_type=data['type'], nx=data['nx'])
#                        form = SubjectForm(school.id)
#                        message = u'Môn học mới đã được thêm.'
#                    except Exception as e:
#                        print e
#                        message = u'Môn học đã tồn tại.'
#
#            else:
#                message = None

    subjectList = cl.subject_set.order_by('index')

    sfl = []
    teachers = []
    rteachers = []
    teacher_list = school.teacher_set.all()
    classList = year.class_set.all().order_by('name')
    for s in subjectList:
        sfl.append(SubjectForm(school.id, instance=s))
        teachers.append(school.teacher_set.filter(major__contains=s.name))
        rteachers.append(teacher_list.exclude(major__contains=s.name))
    list = zip(subjectList, sfl, teachers, rteachers)
    t = loader.get_template(os.path.join('school', 'subject_per_class.html'))
    c = RequestContext(request, {'list': list,
                                 'form': form,
                                 'message': message,
                                 'subjectList': subjectList,
                                 'teacherList' : teacher_list,
                                 'class': cl,
                                 'term': term,
                                 'classList': classList,
                                 'pos': pos})
    return HttpResponse(t.render(c))

@need_login
def hanh_kiem(request, class_id=0):
    if not class_id:
        return HttpResponseRedirect(reverse('index'))

    c = Class.objects.get(id__exact=class_id)
    user = request.user
    if user.userprofile.organization.level == 'S':
        school = c.year_id.school_id
        year = get_current_year(request)
        term = get_current_year(request).term_set.get(number = school.status)
    else:
        year = get_current_year(request)
        term = get_current_term(request)

    classList = year.class_set.all().order_by('name')

    if not in_school(request, c.block_id.school_id):
        return HttpResponseRedirect(reverse('index'))

    pos = get_position(request)
    if pos < 1:
        return HttpResponseRedirect(reverse('index'))
    if pos == 1:
        if not inClass(request, class_id):
            return HttpResponseRedirect(reverse('index'))
    if gvcn(request, class_id) == 1:
        pos = 4
    message = None
    pupilList = c.students()

    form = []
    all = []
    i = 0
    for p in pupilList:
        form.append(TBNamForm())
        all.append(TBNam())
        hk = p.tbnam_set.get(year_id__exact=year.id)
        all[i] = hk
        form[i] = TBNamForm(instance=hk)
        i += 1

    if request.is_ajax() and pos > 3:
        if request.POST['request_type'] == u'all':
            message = 'Cập nhật thành công hạnh kiểm lớp ' + str(Class.objects.get(id=class_id))
            term1 = request.POST.getlist('term1')
            term2 = request.POST.getlist('term2')
            y = request.POST.getlist('year')
            ThangList = [9, 10, 11, 12, 1, 2, 3, 4, 5]
            thang = {}
            for i in ThangList:
                thang[i] = request.POST.getlist('hk_thang_'+str(i))
            i = 0
            for p in pupilList:
                hk = p.tbnam_set.get(year_id__exact=year.id)
                for j in ThangList:
                    setattr(hk, 'hk_thang_'+str(j), thang[j][i])
                if term.number == 1:
                    hk.term1 = term1[i]
                else:
                    hk.term2 = term2[i]
                    hk.year = y[i]
                hk.save()
                i += 1
        elif request.POST['request_type'] == u'sms':
            data = request.POST[u'data']
            data = data.strip().split(' ')
            try:
                for each in all:
                    sms_message = u'Hạnh kiểm '
                    sms_content = u''
                    for element in data:
                        if not int(element) in [6, 7, 8]:
                            sms_message += u'tháng ' + unicode(element) + u', '
                            sms_content += unicode(getattr(each, "hk_thang_"+str(element))) + u', '
                        else:
                            if int(element) == 6:
                                sms_message += u'kì 1, '
                                sms_content += unicode(each.term1) + u','
                            elif int(element) == 7:
                                sms_message += u'kì 2, '
                                sms_content += unicode(each.term2) + u','
                            elif int(element) == 7:
                                sms_message += u'cả năm, '
                                sms_content += unicode(each.year) + u','
                    # send sms
                    student = each.student_id
                    phone_number = student.sms_phone
                    name = ' '.join([student.last_name, student.first_name])
                    sms_message += name + u' : ' + sms_content[:len(sms_content)-1]
                    if phone_number:
                        try:
                            sent = sendSMS(phone_number, to_en1(sms_message), user)
                        except Exception as e:
                            if e.message == 'InvalidPhoneNumber':
                                message = message + u'<li><b>Số ' + str(phone_number)\
                                          + u' không tồn tại</b>'\
                                          + u': ' + sms_message + u'</li>'
                                continue
                            else:
                                message = e.message
                                continue
                        if sent == '1':
                            message = message + u'<li><b>-> ' + str(
                                phone_number) + u': ' + sms_message + u'</b></li>'
                        else:
                            message = message + u'<li> ' + str(phone_number) + u': ' + sms_message + u'</li>'
                    else:
                        message = message + u'<li> ' + u'<b>Không số</b>' + u': ' + sms_message + u'</li>'
            except Exception as e:
                print e
                raise Exception('StrangeRequestMethod')
            data = simplejson.dumps({'message': message})
            return HttpResponse(data, mimetype='json')
        else:
            try:
                p_id = request.POST['id']
                p = c.pupil_set.get(id=int(p_id))
                hk = p.tbnam_set.get(year_id__exact=year.id)

                val = ''
                if request.POST['val'] != u'':
                    val = request.POST['val']
                valid_value = ['T', 'K', 'TB', 'Y', '']
                if not (val in valid_value):
                    data = simplejson.dumps({'message' : 'Bad request.'})
                    return HttpResponse(data, mimetype='json')

                if term.number == 1:
                    if request.POST['request_type'] in [u'year', u'term2']:
                        data = simplejson.dumps({'message' : 'Bad request.'})
                        return HttpResponse(data, mimetype='json')

                setattr(hk, request.POST['request_type'], val)
                hk.save()
                data = simplejson.dumps({'message': 'Cập nhật thành công hạnh kiểm.',
                                        'success':True})
                return HttpResponse(data, mimetype='json')
            except Exception as e:
                print e
                data = simplejson.dumps({'message': 'Có lỗi xảy ra.',
                                         'success':False})
                return HttpResponse(data, mimetype='json')


    listdh = zip(pupilList, form, all)
    t = loader.get_template(os.path.join('school', 'hanh_kiem.html'))
    c = RequestContext(request, {'form': form,
                                 'message': message,
                                 'class': c,
                                 'list': listdh,
                                 'year': year,
                                 'term': term,
                                 'classList': classList,
                                 'pos': pos})
    return HttpResponse(t.render(c))

@need_login
def viewSubjectDetail (request, subject_id):
    if get_position(request) < 4:
        return HttpResponseRedirect(reverse('index'))
    pos = get_position(request)
    sub = Subject.objects.get(id=subject_id)
    class_id = sub.class_id
    if not in_school(request, class_id.block_id.school_id):
        return HttpResponseRedirect(reverse('index'))

    form = SubjectForm(class_id.block_id.school_id.id, instance=sub)
    message = None
    if request.method == 'POST':
        data = request.POST.copy()
        data['name'] = data['name'].strip()
        form = SubjectForm(class_id.block_id.school_id.id, data, instance=sub)
        if form.is_valid():
            form.save()
            message = u'Bạn đã cập nhật thành công'

    t = loader.get_template(os.path.join('school', 'subject_detail.html'))
    c = RequestContext(request, {'form': form,
                                 'message': message,
                                 'sub': sub,
                                 'pos': pos,
                                 })
    return HttpResponse(t.render(c))

@need_login
@school_function
def deleteSubject(request, subject_id):
    if get_position(request) < 4:
        return HttpResponseRedirect(reverse('index'))
    try:
        sub = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))

    class_id = sub.class_id
    if not in_school(request, class_id.block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    completely_del_subject(sub)
    url = reverse('subject_per_class',args=[class_id.id])
    return HttpResponseRedirect(url)

@need_login
@school_function
def deleteStudentInClass(request, student_id):
    try:
        student = Pupil.objects.get(id=student_id)
    except Pupil.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))

    class_id = student.current_class()
    if not in_school(request, class_id.block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    if get_position(request) < 4:
        return HttpResponseRedirect(reverse('index'))
    completely_del_student(student)
    return HttpResponseRedirect(reverse('viewClassDetail',args=[class_id.id]))

@transaction.commit_manually
@need_login
@school_function
def deleteAllStudentsInClass(request, class_id):
    try:
        cl = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))

    students = cl.pupil_set.all()

    if not in_school(request, cl.block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    if get_position(request) < 4:
        return HttpResponseRedirect(reverse('index'))

    for student in students:
        completely_del_student(student)
    transaction.commit()
    return HttpResponseRedirect(reverse('class_detail',args=[cl.id]))

@school_function
@need_login
def diem_danh(request, class_id, day, month, year, api_called=False, data = None):
    user = request.user
    cl = Class.objects.get(id__exact=class_id)
    if not in_school(request, cl.block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    url = reverse('ds_nghi',args=[class_id,day,month,year])
    pos = get_position(request)
    if pos < 3 or (pos == 3 and not gvcn(request, class_id)):
        return HttpResponseRedirect(url)
    message = ''
    dncdata = {'date': date(int(year), int(month), int(day)), 'class_id': class_id}
    year_id = get_current_year(request).id
    dncform = DateAndClassForm(year_id, dncdata)
    print "ddddddddddddddddddddddddddddddddd"
    if request.is_ajax() or api_called:
        if request.method == 'POST':
            request_type = request.POST[u'request_type']
            if request_type == u'update' or api_called:
                if api_called: data = data
                else: data = request.POST[u'data']
                student = None
                for a_student in data.split('/'):
                    id_loai = a_student.split('-')
                    id = id_loai[0]
                    loai = id_loai[1]
                    student = Pupil.objects.get(id=int(id))
                    time = date(int(year), int(month), int(day))
                    diemdanh = student.diemdanh_set.filter(student_id__exact=student)\
                    .filter(time__exact=time)
                    if not diemdanh:
                        diemdanh = DiemDanh()
                        diemdanh.term_id = get_current_term(request)
                        diemdanh.student_id = student
                        diemdanh.time = time
                        diemdanh.loai = loai
                        diemdanh.save()
                    else:
                        diemdanh = diemdanh[0]
                        if loai == 'k':
                            diemdanh.delete()
                            message = u'No need to update'
                            data = simplejson.dumps({'message': message})
                            return HttpResponse(data, mimetype='json')
                        if diemdanh.loai != loai:
                            diemdanh.loai = loai
                            diemdanh.save()
                message = student.full_name() + ': updated.'
                data = simplejson.dumps({'message': message})
                return HttpResponse(data, mimetype='json')
            if request_type == 'sms':
                data = request.POST[u'data']
                data = data.split(':')
                for element in data:
                    if element:
                        element = element.split('-')
                        id = element[0]
                        loai = element[1]
                        # send sms
                        student = Pupil.objects.get(id=id)
                        phone_number = student.sms_phone

                        if loai == 'k':
                            loai = u'đi học'
                        elif loai == u'Có phép':
                            loai = u'nghỉ học có phép'
                        else:
                            loai = u'nghỉ học không phép'
                        name = ' '.join([student.last_name, student.first_name])
                        time = '/'.join([str(day), str(month), str(year)])
                        sms_message = u' Em ' + name + u' đã ' + loai + u' ngày ' + time
                        if phone_number:
                            try:
                                sent = sendSMS(phone_number, to_en1(sms_message), user)
                            except Exception as e:
                                if e.message == 'InvalidPhoneNumber':
                                    message = message + u'<li><b>Số ' + str(phone_number)\
                                              + u' không tồn tại</b>'\
                                              + u': ' + sms_message + u'</li>'
                                    continue
                                else:
                                    message = e.message
                                    continue
                            if sent == '1':
                                message = message + u'<li><b>-> ' + str(
                                    phone_number) + u': ' + sms_message + u'</b></li>'
                            else:
                                message = message + u'<li> ' + str(phone_number) + u': ' + sms_message + u'</li>'
                        else:
                            message = message + u'<li> ' + u'<b>Không số</b>' + u': ' + sms_message + u'</li>'
                data = simplejson.dumps({'message': message})
                return HttpResponse(data, mimetype='json')
        else:
            raise Exception('StrangeRequestMethod')
    pupilList = Pupil.objects.filter(attend___class=class_id, attend__is_member=True).order_by('index', 'first_name',
        'last_name').distinct()
    print "okkkkkkkkkkkkkkkkkkkkk"
    time = date(int(year), int(month), int(day))
    term = get_current_term(request)
    form = []
    for p in pupilList:
        try:
            dd = DiemDanh\
            .objects.get(time__exact=time, student_id__exact=p.id, term_id__exact=term.id)
            form.append(DiemDanhForm(instance=dd))
        except ObjectDoesNotExist:
            form.append(DiemDanhForm())
    try:
        if request.method == 'POST':
            message = u'Đã lưu điểm danh.'
            list = request.POST.getlist('loai')
            i = 0
            for p in pupilList:
                try:
                    dd = DiemDanh.objects.get(time__exact=time, student_id__exact=p.id, term_id__exact=term.id)
                    if list[i] != 'k':
                        data = {'student_id': p.id, 'time': time, 'loai': list[i], 'term_id': term.id}
                        of = form[i]
                        form[i] = DiemDanhForm(data, instance=dd)
                        if str(of) != str(form[i]):
                            if form[i].is_valid():
                                form[i].save()
                    else:
                        form[i] = DiemDanhForm()
                        dd.delete()
                    i += 1
                except ObjectDoesNotExist:
                    if list[i] != 'k':
                        data = {'student_id': p.id, 'time': time, 'loai': list[i], 'term_id': term.id}
                        form[i] = DiemDanhForm(data)
                        if form[i].is_valid():
                            form[i].save()
                    i += 1
    except IndexError:
        message = None
    listdh = zip(pupilList, form)
    t = loader.get_template(os.path.join('school', 'diem_danh.html'))
    c = RequestContext(request,
            {'dncform': dncform, 'form': form, 'pupilList': pupilList, 'message': message,
             'class_id': class_id, 'time': time, 'list': listdh,
             'day': day, 'month': month, 'year': year, 'cl': cl, 'pos': pos})
    return HttpResponse(t.render(c))

@need_login
def diem_danh_hs(request, student_id, view_type=0):
    pos = get_position(request)
    pupil = Pupil.objects.get(id=student_id)
    if pos == 3 and not gvcn(request, pupil.current_class()):
        pos = 1
    if pos < 1:
        return HttpResponseRedirect(reverse('index'))
    c = pupil.current_class()
    if not in_school(request, c.block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    term = get_current_term(request)
    if not term:
        message = None
        t = loader.get_template(os.path.join('school', 'diem_danh_form.html'))
        ct = RequestContext(request, {'class_id': c.id, 'message': message})
        return HttpResponse(t.render(ct))
    ddl = DiemDanh.objects.filter(student_id=student_id, term_id=term.id).order_by('time')
    count = ddl.count()
    t = loader.get_template(os.path.join('school', 'diem_danh_hs.html'))
    c = RequestContext(request, {'form': ddl,
                                 'pupil': pupil,
                                 'student_id': student_id,
                                 'term': term,
                                 'pos': pos,
                                 'count': count})
    return HttpResponse(t.render(c))

@need_login
def ds_nghi(request, class_id, day, month, year):
    user = request.user
    pos = get_position(request)
    if pos == 3 and not gvcn(request, class_id):
        pos = 2
    cl = Class.objects.get(id=class_id)
    if user.userprofile.organization.level == 'S':
        school = cl.year_id.school_id
        year_id = cl.year_id.id
        term = get_current_year(request).term_set.get(number = school.status)
    else:
        term = get_current_term(request)
        year_id = get_current_year(request).id

    pupilList = Pupil.objects.filter(attend___class=class_id, attend__is_member=True).order_by('first_name',
        'last_name').distinct()
    time = date(int(year), int(month), int(day))
    dncdata = {'date': date(int(year), int(month), int(day)), 'class_id': class_id}
    dncform = DateAndClassForm(year_id, dncdata)
    hs_nghi = []
    stt = []
    message = ''
    if request.is_ajax():
        if request.method == 'POST':
            data = request.POST[u'data']
            data = data.split(':')
            for element in data:
                if element:
                    element = element.split('-')
                    id = element[0]
                    loai = element[1]
                    # send sms
                    student = Pupil.objects.get(id=id)
                    phone_number = student.sms_phone

                    if loai == 'k':
                        loai = u'đi học'
                    elif loai == u'Có phép':
                        loai = u'nghỉ học có phép'
                    else:
                        loai = u'nghỉ học không phép'
                    name = ' '.join([student.last_name, student.first_name])
                    time = '/'.join([str(day), str(month), str(year)])
                    sms_message = u' Em ' + name + u' đã ' + loai + u' ngày ' + time
                    if phone_number:
                        try:
                            sent = sendSMS(phone_number, to_en1(sms_message), user)
                        except Exception as e:
                            if e.message == 'InvalidPhoneNumber':
                                message = message + u'<li><b>Số ' + str(phone_number)\
                                          + u' không tồn tại</b>'\
                                          + u': ' + sms_message + u'</li>'
                                continue
                            else:
                                message = e.message
                                continue
                        if sent == '1':
                            message = message + u'<li><b>-> ' + str(phone_number) + u': ' + sms_message + u'</b></li>'
                        else:
                            message = message + u'<li> ' + str(phone_number) + u': ' + sms_message + u'</li>'
                    else:
                        message = message + u'<li> ' + u'<b>Không số</b>' + u': ' + sms_message + u'</li>'
            data = simplejson.dumps({'message': message})
            return HttpResponse(data, mimetype='json')
        else:
            raise Exception("StrangeRequestMethod")
            #end if request.is_ajax()
    for p in pupilList:
        try:
            dd = DiemDanh.objects.get(time__exact=time, student_id__exact=p.id, term_id__exact=term.id)
            hs_nghi.append(p)
            stt.append(dd.loai)
        except ObjectDoesNotExist:
            pass
    ds_nghi = zip(hs_nghi, stt)
    t = loader.get_template(os.path.join('school', 'ds_nghi_hoc.html'))
    c = RequestContext(request,
            {'list': ds_nghi, 'class_id': class_id, 'time': time, 'day': day, 'month': month, 'year': year, 'cl': cl,
             'pos': pos, 'dncform': dncform})
    return HttpResponse(t.render(c))

@need_login
@school_function
def ktkl(request, student_id):
    pupil = Pupil.objects.get(id=student_id)
    if not in_school(request, pupil.current_class().block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    pos = get_position(request)
    if pos == 3 and gvcn(request, pupil.current_class()):
        pos = 4
    if get_position(request) < 1:
        return HttpResponseRedirect(reverse('index'))
    message = ''
    ktl = pupil.khenthuong_set.order_by('time')
    kll = pupil.kiluat_set.order_by('time')
    ktcount = ktl.count()
    klcount = kll.count()
    t = loader.get_template(os.path.join('school', 'ktkl.html'))
    c = RequestContext(request,{'ktl': ktl, 'message': message,
                                'student_id': student_id, 'pupil': pupil,
                                'kll':kll, 'pos': pos,
                                'ktcount': ktcount,  'klcount': klcount})
    return HttpResponse(t.render(c))

@need_login
@school_function
def add_khen_thuong(request, student_id):
    form = KhenThuongForm(student_id)
    pupil = Pupil.objects.get(id=student_id)
    if not in_school(request, pupil.current_class().block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    pos = get_position(request)
    if pos == 3 and gvcn(request, pupil.current_class()):
        pos = 4
    if pos < 4:
        return HttpResponseRedirect(reverse('index'))
    url = reverse('add_khen_thuong',args=[student_id])
    term = get_current_term(request)
    if request.method == 'POST':
        form = KhenThuongForm(student_id, request.POST)
        if form.is_valid():
            kt = form.save(commit=False)
            kt.student_id = pupil
            kt.term_id = term
            kt.save()
            url = reverse('ktkl',args=[student_id])
            return HttpResponseRedirect(url)
    t = loader.get_template(os.path.join('school', 'khen_thuong_detail.html'))
    c = RequestContext(request, {'form': form, 'p': pupil, 'student_id': student_id, 'term': term, 'url': url})
    return HttpResponse(t.render(c))

@need_login
@school_function
def delete_khen_thuong(request, kt_id):
    kt = KhenThuong.objects.get(id=kt_id)
    student = kt.student_id
    student_id = student.id
    if not in_school(request, student.current_class().block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    pos = get_position(request)
    if pos == 3 and gvcn(request, student.current_class()):
        pos = 4
    if pos < 4:
        return HttpResponseRedirect(reverse('index'))
    kt.delete()
    return HttpResponseRedirect(reverse('ktkl',args=[student_id]))

@need_login
@school_function
def edit_khen_thuong(request, kt_id):
    kt = KhenThuong.objects.get(id=kt_id)
    pupil = kt.student_id
    pupil_id = pupil.id
    if not in_school(request, pupil.current_class().block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    pos = get_position(request)
    if pos == 3 and gvcn(request, pupil.current_class()):
        pos = 4
    if pos < 4:
        return HttpResponseRedirect(reverse('index'))
    url = reverse('edit_khen_thuong',args=[kt.id])
    term = kt.term_id
    form = KhenThuongForm(pupil.id, instance=kt)
    if request.method == 'POST':
        form = KhenThuongForm(pupil.id, request.POST, instance=kt)
        if form.is_valid():
            kt = form.save(commit=False)
            kt.student_id = pupil
            kt.term_id = term
            kt.save()
            return HttpResponseRedirect(reverse('ktkl', args=[pupil_id]))
    t = loader.get_template(os.path.join('school', 'khen_thuong_detail.html'))
    c = RequestContext(request, {'form': form, 'p': pupil, 'student_id': pupil.id, 'term': term, 'url': url})
    return HttpResponse(t.render(c))

@need_login
@school_function
def add_ki_luat(request, student_id):
    form = KiLuatForm(student_id)
    pupil = Pupil.objects.get(id=student_id)
    if not in_school(request, pupil.current_class().block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    pos = get_position(request)
    if pos == 3 and gvcn(request, pupil.current_class()):
        pos = 4
    if pos < 4:
        return HttpResponseRedirect(reverse('index'))
    url = reverse('add_ki_luat',args=[student_id])
    #    cl = Class.objects.get(id__exact=pupil.current_class().id)
    term = get_current_term(request)
    if request.method == 'POST':
        form = KiLuatForm(student_id, request.POST)
        if form.is_valid():
            kt = form.save(commit=False)
            kt.student_id = pupil
            kt.term_id = term
            kt.save()
            return HttpResponseRedirect(reverse('ktkl',args=[student_id]))
    t = loader.get_template(os.path.join('school', 'ki_luat_detail.html'))
    c = RequestContext(request, {'form': form, 'p': pupil, 'student_id': student_id, 'term': term, 'url': url})
    return HttpResponse(t.render(c))


@need_login
@school_function
def delete_ki_luat(request, kt_id):
    kt = KiLuat.objects.get(id=kt_id)
    student = kt.student_id
    student_id = student.id
    if not in_school(request, student.current_class().block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    pos = get_position(request)
    if pos == 3 and gvcn(request, student.current_class()):
        pos = 4
    if pos < 4:
        return HttpResponseRedirect(reverse('index'))
    kt.delete()
    return HttpResponseRedirect(reverse('ktkl',args=[student_id]))

@need_login
@school_function
def edit_ki_luat(request, kt_id):
    kt = KiLuat.objects.get(id=kt_id)
    pupil = kt.student_id
    pupil_id = pupil.id
    if not in_school(request, pupil.current_class().block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    pos = get_position(request)
    if pos == 3 and gvcn(request, pupil.current_class()):
        pos = 4
    if pos < 4:
        return HttpResponseRedirect(reverse('index'))
    url = reverse('edit_ki_luat',args=[kt.id])
    term = kt.term_id
    form = KiLuatForm(pupil.id, instance=kt)
    if request.method == 'POST':
        form = KiLuatForm(pupil.id, request.POST, instance=kt)
        if form.is_valid():
            kt = form.save(commit=False)
            kt.student_id = pupil
            kt.term_id = term
            kt.save()
            return HttpResponseRedirect(reverse('ktkl', args=[pupil_id]))
    t = loader.get_template(os.path.join('school', 'ki_luat_detail.html'))
    c = RequestContext(request, {'form': form, 'p': pupil, 'student_id': pupil.id, 'term': term, 'url': url})
    return HttpResponse(t.render(c))

#TODO: check invalid type of dd
@need_login
@school_function
def dd(request, class_id, day, month, year, api_called=False, data=None):
    school = get_school(request)
    _class = Class.objects.get(id = class_id)
    user = request.user
    if _class.year_id.school_id != school:
        return HttpResponseRedirect(reverse('school_index'))
    url = reverse('ds_nghi',args=[class_id,day,month,year])
    pos = get_position(request)
    if pos < 3 or (pos == 3 and not gvcn(request, class_id)):
        return HttpResponseRedirect(url)
    term_id = get_current_term(request)
    std_list = _class.students()
    if (request.is_ajax() or api_called) and request.method == 'POST':
        if api_called or request.POST['request_type'] == 'dd':
            if api_called:
                diem_danh_data = data
            else:
                diem_danh_data = request.POST['data']
                print request.POST
            for part in diem_danh_data.split('%'):
                if part.strip():
                    temp = part.split('-')
                    student = _class.pupil_set.get(id=temp[0])
                    tkdd = student.tkdiemdanh_set.get(term_id=term_id)
                    loai = string.upper(temp[1])
                    time = to_date('-'.join(temp[2:]))
                    if loai not in [u'P',u'K',u'M',u'']:
                        return HttpResponseBadRequest()
                    try:
                        dd = DiemDanh.objects.get(student_id__exact=student.id,
                            time__exact=time,
                            term_id=term_id)
                        if loai == u'':
                            if dd.loai == u'M':
                                tkdd.muon -= 1
                            elif dd.loai == u'P':
                                tkdd.co_phep -= 1
                            elif dd.loai == u'K':
                                tkdd.khong_phep -= 1
                            tkdd.tong_so = tkdd.co_phep + tkdd.khong_phep
                            dd.delete()
                            tkdd.save()
                        else:
                            if loai == u'P':
                                tkdd.co_phep +=1
                            elif loai == u'K':
                                tkdd.khong_phep +=1
                            elif loai == u'M':
                                tkdd.muon +=1
                            if dd.loai == u'P':
                                tkdd.co_phep -= 1
                            elif dd.loai == u'K':
                                tkdd.khong_phep -= 1
                            elif dd.loai == u'M':
                                tkdd.muon -= 1
                            tkdd.tong_so = tkdd.co_phep + tkdd.khong_phep
                            dd.loai = loai
                            tkdd.save()
                            dd.save()
                    except Exception:
                        dd = DiemDanh(student_id=student, time=time,
                                loai=loai, term_id=term_id)
                        if loai == u'M':
                            tkdd.muon += 1
                        elif loai == u'P':
                            tkdd.co_phep += 1
                        elif loai == u'K':
                            tkdd.khong_phep += 1
                        tkdd.tong_so = tkdd.co_phep + tkdd.khong_phep
                        tkdd.save()
                        dd.save()
            return HttpResponse()
        elif request.POST['request_type'] == 'sms':
            data = request.POST['data']
            data = data.split('-')
            message = ''
            for day in data:
                try:
                    day = to_date(day)
                    ddl = DiemDanh.objects.filter(time__exact=day,
                        student_id__in=std_list)
                    for dd in ddl:
                        student = dd.student_id
                        phone_number = student.sms_phone
                        name = ' '.join([student.last_name, student.first_name])
                        if phone_number:
                            #noinspection PyUnresolvedReferences
                            sms_message = u' Em ' + name + u' đã ' + dd.get_loai_display() + u' ngày ' + day.strftime("%d/%m/%Y")
                            try:
                                sent = sendSMS(phone_number,
                                    to_en1(sms_message),
                                    user,
                                    receiver=student.user_id,
                                    school=school)
                            except Exception as e:
                                if e.message == 'InvalidPhoneNumber':
                                    message = message + u'<li><b>Số ' + str(phone_number)\
                                              + u' không tồn tại</b>'\
                                              + u': ' + sms_message + u'</li>'
                                    continue
                                else:
                                    message = e.message
                                    continue
                            if sent == '1':
                                message = message + u'<li><b>-> ' + str(phone_number) + u': ' + sms_message + u'</b></li>'
                            else:
                                message = message + u'<li> ' + str(phone_number) + u': ' + sms_message + u'</li>'
                        else:
                            notify_message = u' Em ' + name + u' chưa có số điện thoại để gửi tin nhắn'
                            message = message + u'<li> ' + u'<b>Lỗi</b>' + u': ' + notify_message + u'</li>'
                except Exception as e:
                    if e.message == 'PharseDateException':
                        pass
                    else:
                        raise e
            data = simplejson.dumps({'message': message})
            return HttpResponse(data, mimetype='json')

    day = date(int(year), int(month), int(day))
    previous_week = day - timedelta(days = 7)
    next_week = day + timedelta(days = 7)
    daynum = day.weekday()
    bd = day - timedelta(daynum)
    weeklist = []
    d = bd
    for i in range(6):
        weeklist.append(d)
        d += timedelta(1)
    year_id = get_current_year(request).id
    dncdata = {'date': d, 'class_id': class_id}
    dncform = DateAndClassForm(year_id, dncdata)
    fl = {}
    stdid_list = [ss.id for ss in std_list]
    for ss in stdid_list:
        fl[ss] = {}
        for d in weeklist:
            id = str(ss) + "_" + d.strftime("%d/%m/%Y") +'_%s'
            fl[ss][d] = DDForm(auto_id=id)
    dd_list = DiemDanh.objects.filter(student_id__in = stdid_list, time__in=weeklist)
    for dd in dd_list:
        id = str(dd.student_id_id) + "_" + d.strftime("%d/%m/%Y") +'_%s'
        fl[dd.student_id_id][dd.time] = DDForm(auto_id=id,instance=dd)
    c = RequestContext(request,{'pos':pos,'class':_class,'std_list':std_list,
                                'week_list':weeklist,'dncform':dncform,
                                'date':day, 'previous_week': previous_week,
                                'next_week':next_week, 'fl':fl })
    t = loader.get_template(os.path.join('school','dd.html'))
    return HttpResponse(t.render(c))
