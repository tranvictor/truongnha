# coding=utf-8
import os
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.template import loader
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from django.utils import simplejson
from decorators import need_login, school_function, operating_permission
from school.models import Teacher, Pupil, Class, Group, Subject, Year, COMMENT_SUBJECT_LIST
from school.forms import MoveClassForm, TeacherForm, TeamForm, GroupForm,\
        TeacherGroupForm, TeacherTTCNForm, TeacherTTLLForm, TeacherTTCBForm,\
        ThongTinCaNhanForm, ThongTinLienLacForm, PupilForm, ThongTinGiaDinhForm,\
        ThongTinDoanDoiForm, ClassForm, TeacherTTCNForm2
from school.school_settings import CAP1_DS_MON, CAP2_DS_MON, CAP3_DS_MON
from school.utils import get_position, move_student, get_school, delete_history,\
        to_en1, to_date, add_teacher, del_teacher, in_school, get_teacher,\
        get_student, get_lower_bound, get_upper_bound, get_current_year,\
        add_subject, get_current_term
from sms.utils import sendSMS, send_email, send_sms_summary_mark

SMS_SUMMARY = os.path.join('school', 'sms_summary.html')

@need_login
@school_function
@operating_permission([u'HIEU_TRUONG', u'HIEU_PHO'])
def activate_teacher(request):
    if request.method == 'POST' and request.is_ajax():
        id_list = request.POST['id_list'].split('-')
        number = 0
        number_activated = 0
        number_cant_contact = 0
        activated_teacher = ''
        cant_contact = ''
        for id in id_list:
            if id:
                teacher = Teacher.objects.get(id=int(id))
                try:
                    teacher.activate_account()
                    number += 1
                    activated_teacher += str(teacher.id) + '-'
                except Exception as e:
                    if e.message == 'NoWayToContact':
                        number_cant_contact += 1
                        cant_contact += str(teacher.id) + '-'
                        #TODO: notice that system can't contact to users
                    elif e.message == 'AccountActivated':
                        number_activated += 1
                    else: raise e
        message = u'Đã kích hoạt ' + unicode(number) + u' tài khoản'
        data = {
            'message': message,
            'number_activated': number_activated,
            'number_cant_contact': number_cant_contact,
            'activated_teacher': activated_teacher,
            'cant_contact': cant_contact,
            'number': number,
            'success': True
        }
        return HttpResponse(simplejson.dumps(data), mimetype='json')
    else:
        raise Exception("BadRequest")

def activate_student(request):
    if request.method == 'POST' and request.is_ajax():
        id_list = request.POST['id_list'].split('-')
        number = 0
        number_activated = 0
        number_cant_contact = 0
        activated_student = ''
        cant_contact = ''
        for id in id_list:
            if id:
                student = Pupil.objects.get(id=int(id))
                try:
                    student.activate_account()
                    number += 1
                    activated_student += str(student.id) + '-'
                except Exception as e:
                    if e.message == 'NoWayToContact':
                        number_cant_contact += 1
                        cant_contact += str(student.id) + '-'
                        #TODO: notice that system can't contact to users
                    elif e.message == 'AccountActivated':
                        number_activated += 1
                    else: raise e
        message = u'Đã kích hoạt ' + unicode(number) + u' tài khoản'
        data = {
            'message': message,
            'number_activated': number_activated,
            'number_cant_contact': number_cant_contact,
            'activated_student': activated_student,
            'cant_contact': cant_contact,
            'number': number,
            'success': True
        }
        return HttpResponse(simplejson.dumps(data), mimetype='json')
    else:
        raise Exception("BadRequest")

def deactivate_student(request):
    if request.method == 'POST' and request.is_ajax():
        id_list = request.POST['id_list'].split('-')
        number = 0
        number_deactivated = 0
        deactivated_student = ''
        cant_contact = ''
        for id in id_list:
            if id:
                student = Pupil.objects.get(id=int(id))
                try:
                    student.deactive_account()
                    number += 1
                    deactivated_student += str(student.id) + '-'
                except Exception as e:
                    pass
        message = u'Đã khóa ' + unicode(number) + u' tài khoản'
        data = {
            'message': message,
            'number_deactivated': number_deactivated,
            'deactivated_student': deactivated_student,
            'cant_contact': cant_contact,
            'number': number,
            'success': True
        }
        return HttpResponse(simplejson.dumps(data), mimetype='json')
    else:
        raise Exception("BadRequest")

@need_login
@school_function
def move_one_student(request, student_id):
    school = get_school(request)

    pos = get_position(request)
    if request.is_ajax():
        student = Pupil.objects.get(id=student_id)
        message = ''
        form = MoveClassForm(student)
        attends = student.get_attended()
        check = []
        for a in attends:
            check.append(a.history_check())
        attendlist = zip(attends, check)
        if pos > 3:
            if request.method == 'POST':
                if request.POST['request_type'] == 'movestudent':
                    form = MoveClassForm(student, request.POST)
                    if form.is_valid():
                        new_class = Class.objects.get(id=request.POST['move_to'])
                        move_student(school, student, new_class)
                        form = MoveClassForm(student)
                        message = u'Bạn đã chuyển thành công lớp cho học sinh ' + unicode(student) + '.'
                elif request.POST['request_type'] == 'delete_history':
                    try:
                        history = attends.get(id=request.POST['id'])
                    except ObjectDoesNotExist:
                        return
                    delete_history(history)
                    return HttpResponse()
        t = loader.get_template(os.path.join('school', 'move_one_student.html'))
        c = RequestContext(request, {'student': student,
                                     'class': student.current_class(),
                                     'message': message,
                                     'form': form,
                                     'pos' : pos,
                                     'attendlist': attendlist})
        return HttpResponse(t.render(c))
    return HttpResponseNotAllowed(u'Không được phép truy cập')

@need_login
def move_students(request):
    school = get_school(request)
    if get_position(request) < 4:
        return HttpResponseRedirect(reverse('index'))
    year = get_current_year(request)
    message = ''
    classList = Class.objects.filter(year_id=year).order_by('name')
    if request.is_ajax():
        if request.method == 'POST':
            if request.POST['request_type'] == u'source':
                class_id = int(request.POST['class_id'])
                if not class_id:
                    responseClassList = classList
                    studentList = school.pupil_set.filter(class_id=None)
                else:
                    _class = Class.objects.get(id=class_id)
                    studentList = school.pupil_set.filter(class_id=class_id)
                    responseClassList = classList.filter(block_id=_class.block_id)\
                                                 .exclude(id=class_id)
                list = '<option value=-1> ------ </option>'
                for cl in responseClassList:
                    list +="<option value=" + str(cl.id) + ">" + str(cl) + "</option>"
                table = render_to_string(os.path.join('school',
                                        'classTable.html'),
                                        {'list': studentList})
                data = simplejson.dumps({'message': message,
                                        'ClassList': list,
                                        'table': table})
                return HttpResponse(data, mimetype='json')
            if request.POST['request_type'] == u'move':
                new_class = Class.objects.get(id=request.POST['target'])
                data = request.POST[u'data']
                data = data.split('-')

                for e in data:
                    if e.strip():
                        student = Pupil.objects.get(id__exact=int(e))
                        move_student(school, student, new_class)
                return HttpResponse()
    t = loader.get_template(os.path.join('school', 'move_students.html'))
    c = RequestContext(request, {'classList': classList,
                                 'message': message})
    return HttpResponse(t.render(c))

@need_login
@school_function
@operating_permission([u'HIEU_TRUONG', u'HIEU_PHO'])
def sms_summary(request, class_id=None):
    school = get_school(request)
    year = get_current_year(request, school=school)
    classes = year.class_set.order_by('name')
    term = get_current_term(request)
    try:
        if class_id:
            cl = classes.get(id=class_id)
        else:
            cl = classes[0]
    except ObjectDoesNotExist:
        message = u'Lớp học không tồn tại'
        success = False
        HttpResponse(simplejson.dumps({
            'message': message,
            'success': success}, mimetype='json'))
    info_list, students, marks = cl._generate_mark_summary(term)
    if request.method == 'POST' and request.is_ajax():
        ids = request.POST['students'].split('-')
        ids = [int(id) for id in ids if id]
        number = 0
        for st in students:
            if (st.sms_phone and st.id in ids
                    and info_list[st.id] != u'Không có điểm mới'):
                try:
                    send_sms_summary_mark(st,
                            info_list[st.id],
                            marks[st.id],
                            request.user,
                            cl=cl,
                            school=school)
                    number += 1
                except Exception as e:
                    print e
                    pass
        message = '<li>%d tin nhắn sẽ được gửi trong chậm nhất 1h</li>'\
                % (number)
        if len(ids) > number:
            message += '<li>%d học sinh không có điểm mới để gửi hoặc không có số điện\
                thoại</li>' % (len(ids) - number)
        return HttpResponse(simplejson.dumps({
            'message': message,
            'success': True}), mimetype='json')

    # GET reponse
    return render_to_response(SMS_SUMMARY,
            {'info_list': info_list,
                'students': students,
                'selected_class': cl,
                'classes': classes,},
            context_instance=RequestContext(request))

@need_login
@school_function
def teachers(request):
    user = request.user
    pos = get_position(request)
    school = get_school(request)
    if request.method == 'POST':
        if request.is_ajax() :
            if pos >=3:
                if request.POST['request_type'] == u'send_sms':
                    try:
                        if pos == 3:
                            content = u'%s gửi cho bạn tin nhắn:\n'\
                                        % user.teacher.short_name()
                        else: 
                            content = u'%s gửi cho bạn tin nhắn:\n'\
                                        % school.name
                        content += request.POST[u'content'].strip()
                        teacher_list = request.POST[u'teacher_list']
                        teacher_list = teacher_list.split("-")
                        sts = []
                        for teacher in teacher_list:
                            if teacher: sts.append(int(teacher))
                        teachers = Teacher.objects.filter(id__in=sts)
                        number_of_sent = 0
                        number_of_blank = 0
                        number_of_failed = 0
                        number_of_email_sent = 0
                        for teacher in teachers:
                            sms_sent = False
                            if teacher.sms_phone:
                                try:
                                    if sendSMS(teacher.sms_phone,
                                                to_en1(content),
                                                user) == '1':
                                        number_of_sent += 1
                                        sms_sent = True
                                    else:
                                        number_of_failed += 1
                                except Exception:
                                    number_of_failed += 1
                            else:
                                number_of_blank += 1

                            if not sms_sent and teacher.email:
                                try:
                                    send_email(u'Trường %s thông báo' % school.name,
                                                content,
                                                to_addr=[teacher.email])
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
            if pos > 3:
                if request.POST['request_type'] == u'add':
                    print request.POST
                    if request.POST['first_name'].strip():
                        name = request.POST['first_name'].split()
                        last_name = ' '.join(name[:len(name) - 1])
                        first_name = name[len(name) - 1]
                    else:
                        last_name = ''
                        first_name = ''
                    index = school.teacher_set.count() + 1
                    if request.POST['team_id']:
                        try:
                            team = school.team_set.get(id=request.POST['team_id'])
                        except Exception as e:
                            message = u"Tổ này không tồn tại."
                            response = {
                                'success': False,
                                'message': message
                            }
                            return HttpResponse(simplejson.dumps(response),
                                mimetype='json')

                    else: team = None
                    if request.POST['group_id']:
                        try:
                            group = team.group_set.get(id=request.POST['group_id'])
                        except Exception as e:
                            message = u"Nhóm này không tồn tại."
                            response = {
                                'success': False,
                                'message': message
                            }
                            return HttpResponse(simplejson.dumps(response),
                                mimetype='json')
                    else: group = None
                    data = {'first_name': first_name,
                            'last_name': last_name,
                            'birthday': request.POST['birthday'],
                            'sex': request.POST['sex'],
                            'school_id': school.id,
                            'sms_phone': request.POST['sms_phone'],
                            'team_id': request.POST['team_id'],
                            'group_id': request.POST['group_id'],
                            'major': request.POST['major'],
                            'index': index}
                    form = TeacherForm(school.id, data)
                    if form.is_valid():
                        birthday = to_date(request.POST['birthday'])
                        try:
                            school.teacher_set.get(
                                    first_name__exact=data['first_name'],
                                    last_name__exact=data['last_name'],
                                    birthday__exact=birthday)
                            message = u'Giáo viên này đã tồn tại trong hệ thống'
                            response = {
                                'success': False,
                                'message': message
                            }
                        except ObjectDoesNotExist:
                            teacher = add_teacher(first_name=data['first_name'],
                                                    last_name=data['last_name'],
                                                    school=get_school(request),
                                                    birthday=birthday,
                                                    sms_phone=data['sms_phone'],
                                                    sex=data['sex'],
                                                    team_id=team,
                                                    group_id=group,
                                                    major=data['major'])
                            message = u'Bạn vừa thêm một giáo viên mới.'
                            count = school.teacher_set.count()
                            new_teacher = render_to_string(
                                            os.path.join('school',
                                                'add_teacher_one_teacher.html'),
                                            {'teacher':teacher,
                                             'pos':pos,
                                             'count':count})
                            response = { 'success': True,
                                        'message': message,
                                        'new_teacher': new_teacher}
                        return HttpResponse(simplejson.dumps(response),
                                mimetype='json')
                    else:
                        response = {
                            'success': False,
                            'message': u'Có lỗi ở dữ liệu nhập vào.'
                        }
                        for field in form:
                            if field.errors:
                                response[field.name] = str(field.errors)
                        return HttpResponse(simplejson.dumps(response),
                                mimetype='json')
                if request.POST['request_type'] == u'del':
                    data = request.POST[u'data']
                    data = data.split('-')
                    for e in data:
                        if e.strip():
                            teacher = school.teacher_set.get(id__exact=int(e))
                            del_teacher(teacher)
                    data = simplejson.dumps({'success': True})
                    return HttpResponse(data, mimetype='json')
                if request.POST['request_type'] == u'add-team':
                    data = {'name': request.POST['name'].strip(),
                            'school_id': school.id}
                    try:
                        school.team_set.get(name=request.POST['name'].strip())
                        message = u'Tổ này đã tồn tại.'
                    except ObjectDoesNotExist:
                        message = 'OK'
                        t = TeamForm(data)
                        if t.is_valid():
                            t.save()
                    data = simplejson.dumps({'message': message})
                    return HttpResponse(data, mimetype='json')
                if request.POST['request_type'] == u'add-group':
                    data = {'name': request.POST['name'].strip(),
                            'team_id': request.POST['id'].strip()}
                    try:
                        try:
                            team = school.team_set.get(id=request.POST['id'].strip())
                        except Exception:
                            message = u'Tổ này không tồn tại.'
                            data = simplejson.dumps({'message': message})
                            return HttpResponse(data, mimetype='json')
                        team.group_set.get(name=request.POST['name'].strip())
                        message = u'Nhóm này đã tồn tại.'
                    except ObjectDoesNotExist:
                        message = 'OK'
                        t = GroupForm(data, school = school)
                        if t.is_valid():
                            t.save()
                    data = simplejson.dumps({'message': message})
                    return HttpResponse(data, mimetype='json')
                if request.POST['request_type'] == u'delete_team':
                    try:
                        t = school.team_set.get(id=request.POST['id'])
                        teacherList = t.teacher_set.all()
                        for teacher in teacherList:
                            teacher.group_id = None
                            teacher.team_id = None
                        t.delete()
                        return HttpResponse()
                    except Exception as e:
                        raise Exception('BadRequest')

                if request.POST['request_type'] == u'delete_group':
                    g = Group.objects.get(id=request.POST['id'])
                    if g.team_id.school_id == school:
                        teacherList = g.teacher_set.all()
                        for teacher in teacherList:
                            teacher.group_id = None
                        g.delete()
                        return HttpResponse()
                    else:
                        raise Exception('BadRequest')
                if request.POST['request_type'] == u'rename-team':
                    t = school.team_set.get(id=request.POST['id'])
                    try:
                        school.team_set.get(name=request.POST['name'].strip())
                        message = u'Tên tổ này đã tồn tại.'
                        success = False
                    except ObjectDoesNotExist:
                        t.name = request.POST['name'].strip()
                        t.save()
                        message = u'Đổi tên thành công.'
                        success = True
                    data = simplejson.dumps({'message': message, 'success': success})
                    return HttpResponse(data, mimetype='json')
                if request.POST['request_type'] == u'rename-group':
                    school_groups = Group.objects.filter(team_id__school_id = school)
                    try:
                        school_groups.get(name=request.POST['name'].strip())
                        message = u'Tên nhóm này đã tồn tại.'
                        success = False
                    except ObjectDoesNotExist:
                        group = school_groups.get(id=request.POST['id'])
                        group.name = request.POST['name'].strip()
                        if len(group.name) > 30:
                            message = u'Tên quá dài'
                            success = False
                        else:
                            group.save()
                            message = u'Đổi tên thành công.'
                            success = True
                    data = simplejson.dumps({'message': message, 'success': success})
                    return HttpResponse(data, mimetype='json')

    team_list = school.team_set.all()
    group_list = Group.objects.filter(team_id__school_id = school)
    teacher_list = school.teacher_set.order_by('first_name', 'last_name')
    teacher_form = TeacherForm(school.id)
    t = loader.get_template(os.path.join('school', 'teachers.html'))

    c = RequestContext(request, {'team_list': team_list,
                                 'pos': pos,
                                 'teacher_list': teacher_list,
                                 'group_list': group_list,
                                 'teacher_form': teacher_form,
                                 })
    return HttpResponse(t.render(c))

@need_login
def viewTeacherDetail(request, teacher_id):
    message = None
    school = get_school(request)
    try:
        teacher = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        return HttpResponseRedirect(reverse('teachers'))
    if not in_school(request, teacher.school_id):
        return HttpResponseRedirect(reverse('index'))
    pos = get_position(request)
    teamlist = school.team_set.all()
    grouplist = []
    for ateam in teamlist:
        grouplist.append(ateam.group_set.all())
    tng = zip(teamlist,grouplist)
    if pos == 3:
        if get_teacher(request) is not None:
            if not(get_teacher(request).id == int(teacher_id)):
                pos = 1
    if pos < 1:
        return HttpResponseRedirect(reverse('index'))
    form = TeacherForm(school.id, instance=teacher)
    if teacher.team_id is not None:
        tgform = TeacherGroupForm(teacher.team_id.id, instance=teacher)
    else:
        tgform = TeacherGroupForm(0, instance=teacher)
    ttcnform = TeacherTTCNForm(school.id,instance=teacher)
    ttcnform2 = TeacherTTCNForm2(instance=teacher)
    ttllform = TeacherTTLLForm(instance=teacher)
    ttcbform = TeacherTTCBForm(instance=teacher)
    if request.method == 'POST' and pos >= 3:
        data = request.POST.copy()
        message = u'Đã lưu'
        ttcnform2 = TeacherTTCNForm2(data, instance=teacher)
        ttllform = TeacherTTLLForm(data, instance=teacher)
        if pos == 4:
            ttcbform = TeacherTTCBForm(data, instance=teacher)
            data['first_name'] = data['first_name'].strip()
            data['last_name'] = data['last_name'].strip()
            ttcnform = TeacherTTCNForm(school.id, data, instance=teacher)
            if ttcnform.is_valid():
                if 'group_id' in request.POST:
                    if request.POST['group_id'] != '':
                        try:
                            t1 = school.team_set.get(id = request.POST['team_id'])
                            g = t1.group_set.get(id = request.POST['group_id'])
                            teacher.group_id = g
                            teacher.save()
                            ttcnform.save()
                        except Exception:
                            message = 'Có lỗi ở thông tin tổ nhóm'
                    else:
                        ttcnform.save()
        if ttcnform2.is_valid():
            ttcnform2.save()
        if ttllform.is_valid():
            ttllform.save()
    if request.is_ajax() and pos >= 3:
        if request.method == 'POST':
            first_name = ''
            last_name = ''
            birthday = ''
            phone = ''
            email = ''
            sms_phone = ''
            cmt = ''
            ngay_vao_doan = ''
            ngay_vao_dang = ''
            muc_luong = ''
            hs_luong = ''
            bhxh = ''
            if pos == 4:
                if not ttcnform.is_valid():
                    message = 'Có lỗi ở dữ liệu nhập vào'
                    for a in ttcnform:
                        if a.name == 'first_name':
                            if a.errors:
                                first_name = str(a.errors)
                        if a.name == 'last_name':
                            if a.errors:
                                last_name = str(a.errors)
                        if a.name == 'birthday':
                            if a.errors:
                                birthday = str(a.errors)
                if not ttcbform.is_valid():
                    message = 'Có lỗi ở dữ liệu nhập vào'
                    for a in ttcbform:
                        if a.errors:
                            if a.name == 'cmt':
                                cmt = str(a.errors)
                            if a.name == 'ngay_vao_doan':
                                ngay_vao_doan = str(a.errors)
                            if a.name == 'ngay_vao_dang':
                                ngay_vao_dang = str(a.errors)
                            if a.name == 'muc_luong':
                                muc_luong = str(a.errors)
                            if a.name == 'hs_luong':
                                hs_luong = str(a.errors)
                            if a.name == 'bhxh':
                                bhxh = str(a.errors)
            if not ttllform.is_valid():
                message = 'Có lỗi ở dữ liệu nhập vào'
                for a in ttllform:
                    if a.name == 'phone':
                        if a.errors:
                            phone = str(a.errors)
                    if a.name == 'email':
                        if a.errors:
                            email = str(a.errors)
                    if a.name == 'sms_phone':
                        if a.errors:
                            sms_phone = str(a.errors)
            response = simplejson.dumps(
                    {'first_name': first_name,
                        'last_name': last_name,
                        'birthday': birthday,
                        'phone': phone,
                        'email': email,
                        'sms_phone': sms_phone,
                        'cmt': cmt,
                        'ngay_vao_doan': ngay_vao_doan,
                        'ngay_vao_dang': ngay_vao_dang,
                        'muc_luong': muc_luong,
                        'hs_luong': hs_luong,
                        'bhxh': bhxh,
                        'message':message })
            return HttpResponse(response, mimetype='json')

    t = loader.get_template(os.path.join('school', 'teacher_detail.html'))
    c = RequestContext(request,
            {'form': form, 'message': message,
                'teacher': teacher, 'id': teacher_id,
                'ttcnform': ttcnform,
                'tng':tng, 'tgform':tgform,
                'pos': pos, 'ttllform': ttllform,
                'ttcbform': ttcbform,
                'ttcnform2':ttcnform2})
    return HttpResponse(t.render(c))

@need_login
@school_function
def deleteTeacher(request, teacher_id, team_id=0):
    try:
        s = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))

    if not in_school(request, s.school_id):
        return HttpResponseRedirect(reverse('teachers'))
    if get_position(request) < 4:
        return HttpResponseRedirect(reverse('index'))
    cl = Subject.objects.filter(teacher_id=s.id)
    for sj in cl:
        sj.teacher_id = None
        sj.save()
    cl = Class.objects.filter(teacher_id=s.id)
    for sj in cl:
        sj.teacher_id = None
        sj.save()
    del_teacher(s)
    if int(team_id):
        return HttpResponseRedirect("/school/teachers_in_team/" + team_id)
    return HttpResponseRedirect("/school/teachers_tab")

@need_login
@school_function
def viewStudentDetail(request, student_id):
    pos = get_position(request)
    if pos == 1:
        if get_student(request):
            if not(get_student(request).id == int(student_id)):
                pos = 2
    if get_position(request) < 1:
        return HttpResponseRedirect(reverse('index'))
    message = None
    pupil = Pupil.objects.get(id=student_id)
    school_id = pupil.school_id.id
    if not in_school(request, pupil.current_class().block_id.school_id):
        return HttpResponseRedirect(reverse('index'))
    form = PupilForm(school_id, instance=pupil)
    ttcnform = ThongTinCaNhanForm(school_id, instance=pupil)
    ttllform = ThongTinLienLacForm(instance=pupil)
    ttgdform = ThongTinGiaDinhForm(instance=pupil)
    ttddform = ThongTinDoanDoiForm(student_id, instance=pupil)
    if request.method == 'POST' and request.is_ajax():
        data = request.POST.copy()
        data['first_name'] = data['first_name'].strip()
        data['last_name'] = data['last_name'].strip()
        data['start_year_id'] = pupil.start_year_id_id
        data['class_id'] = pupil.current_class().id
        pupilform = PupilForm(school_id, data, instance=pupil)
        first_name = ''
        last_name = ''
        birthday = ''
        school_join_date = ''
        school_join_mark = ''
        phone = ''
        father_phone = ''
        mother_phone = ''
        email = ''
        sms_phone = ''
        father_birthday = ''
        mother_birthday = ''
        ngay_vao_doi = ''
        ngay_vao_doan = ''
        ngay_vao_dang = ''
        find = pupil.current_class().student_set\
                .filter(first_name__exact=data['first_name'])\
                .filter(last_name__exact = data['last_name'])\
                .filter(birthday__exact = to_date(data['birthday']))\
                .exclude(id__exact = pupil.id)
        if find:
            dup_student = find[0]
            message = u'Thông tin học sinh vừa sửa trùng với học sinh STT {} {} {}.'.format(dup_student.index,dup_student.last_name,
            dup_student.first_name)
        elif pupilform.is_valid():
            pupilform.save()
            message = 'Bạn đã cập nhật thành công thông tin học sinh.'
        if not pupilform.is_valid():
            if not message:
                message = 'Có lỗi ở dữ liệu nhập vào.'
            for a in pupilform:
                if a.errors:
                    print a.name
                if a.name == 'first_name':
                    if a.errors:
                        first_name = str(a.errors)
                if a.name == 'last_name':
                    if a.errors:
                        last_name = str(a.errors)
                if a.name == 'birthday':
                    if a.errors:
                        birthday = str(a.errors)
                if a.name == 'school_join_date':
                    if a.errors:
                        school_join_date = str(a.errors)
                if a.name == 'school_join_mark':
                    if a.errors:
                        school_join_mark = str(a.errors)
                if a.name == 'phone':
                    if a.errors:
                        phone = str(a.errors)
                if a.name == 'father_phone':
                    if a.errors:
                        father_phone = str(a.errors)
                if a.name == 'mother_phone':
                    if a.errors:
                        mother_phone = str(a.errors)
                if a.name == 'email':
                    if a.errors:
                        email = str(a.errors)
                if a.name == 'sms_phone':
                    if a.errors:
                        sms_phone = str(a.errors)
                if a.name == 'father_birthday':
                    father_birthday = str(a.errors)
                if a.name == 'mother_birthday':
                    mother_birthday = str(a.errors)
                if a.name == 'ngay_vao_doan':
                    if a.errors:
                        ngay_vao_doan = str(a.errors)
                if a.name == 'ngay_vao_doi':
                    if a.errors:
                        ngay_vao_doi = str(a.errors)
                if a.name == 'ngay_vao_dang':
                    if a.errors:
                        ngay_vao_dang = str(a.errors)
        response = simplejson.dumps({'message': message,
            'response_type': 'tths',
            'first_name': first_name,
            'last_name': last_name,
            'birthday': birthday,
            'school_join_date': school_join_date,
            'school_join_mark': school_join_mark,
            'father_phone': father_phone,
            'mother_phone': mother_phone,
            'phone': phone,
            'email': email,
            'sms_phone': sms_phone,
            'father_birthday': father_birthday,
            'mother_birthday': mother_birthday,
            'ngay_vao_doi': ngay_vao_doi,
            'ngay_vao_doan': ngay_vao_doan,
            'ngay_vao_dang': ngay_vao_dang})
        return HttpResponse(response, mimetype='json')
    attended = pupil.get_attended()
    t = loader.get_template(os.path.join('school', 'student_detail.html'))
    c = RequestContext(request, {'form': form,
        'ttcnform': ttcnform,
        'ttllform': ttllform,
        'ttgdform': ttgdform,
        'ttddform': ttddform,
        'message': message,
        'id': student_id,
        'class': pupil.current_class(),
        'attended': attended,
        'pos': pos,
        'student': pupil,})
    return HttpResponse(t.render(c))

@need_login
@school_function
def addClass(request):
    user = request.user
    if get_position(request) < 4:
        return HttpResponseRedirect(reverse('index'))
    school = user.userprofile.organization
    low = get_lower_bound(school)
    up = get_upper_bound(school)
    if school.status:
        form = ClassForm(school.id)

        if request.method == 'POST':
            print request.POST
            names = request.POST['name'].split(" ")
            block_num = names[0]

            try:
                block = school.block_set.get(number=int(block_num))
            except Exception:
                t = loader.get_template(os.path.join('school', 'add_class.html'))
                c = RequestContext(request, {'form': form})
                return HttpResponse(t.render(c))

            index = get_current_year(request).class_set.count()
            data = {'name': request.POST['name'],
                    'year_id': Year.objects.filter(school_id=school.id)\
                            .latest('time').id, 'block_id': block.id,
                    'teacher_id': request.POST['teacher_id'],
                    'phan_ban': request.POST['phan_ban'],
                    'max': 0,
                    'status': school.status,
                    'index': index}
            form = ClassForm(school.id, data)
            if form.is_valid():
                _class = form.save()
                if school.school_level == '1': ds_mon_hoc = CAP1_DS_MON
                elif school.school_level == '2': ds_mon_hoc = CAP2_DS_MON
                elif school.school_level == '3': ds_mon_hoc = CAP3_DS_MON
                else: raise Exception('SchoolLevelInvalid')
                index = 0
                try:
                    for mon in ds_mon_hoc:
                        index += 1
                        if mon in COMMENT_SUBJECT_LIST:
                            add_subject(subject_name=mon,
                                    subject_type=mon,
                                    nx=True,
                                    _class=_class,
                                    index=index)
                        else:
                            add_subject(subject_name=mon,
                                    subject_type=mon,
                                    _class=_class,
                                    index=index)
                    return HttpResponseRedirect(reverse('classes'))
                except Exception as e:
                    print e

        t = loader.get_template(os.path.join('school', 'add_class.html'))
        c = RequestContext(request, {'form': form, 'low': low, 'up': up})
        return HttpResponse(t.render(c))
    else:
        t = loader.get_template(os.path.join('school', 'add_class.html'))
        c = RequestContext(request)
        return HttpResponse(t.render(c))

@need_login
@school_function
def classes(request):
    pos = get_position(request)
    if pos == 1:
        url = reverse('class_detail', args=[get_student(request).current_class().id])
        return HttpResponseRedirect(url)
    message = None
    school = get_school(request)
    if request.method == 'POST':
        if request.is_ajax():
            cyear = get_current_year(request)
            class_id = request.POST['id']
            c = cyear.class_set.get(id=int(class_id))
            tc = None
            teacher_id = ''
            teacher = None
            if request.POST['teacher_id'] != u'':
                teacher_id = request.POST['teacher_id']
                try:
                    teacher = school.teacher_set.get(id=int(teacher_id))
                except ObjectDoesNotExist:
                    return HttpResponse(simplejson.dumps({
                        'message': u'Giáo viên không tồn tại',
                        'success': False
                    }), mimetype='json')
                try:
                    tc = cyear.class_set.get(teacher_id__exact=teacher)
                except ObjectDoesNotExist as e:
                    print e, 'caught'
                except MultipleObjectsReturned as e:
                    tc = True
            if not tc:
                try:
                    c.teacher_id = teacher
                    c.save()
                    return HttpResponse(simplejson.dumps({ 'success': True }),
                                                            mimetype='json')
                except Exception as e:
                    print e
                    raise e
            else:
                message = u'Giáo viên đã có lớp chủ nhiệm'
                data = simplejson.dumps({'message': message, 'success': False})
                return HttpResponse(data, mimetype='json')

    blockList = school.block_set.all()
    classList = get_current_year(request).class_set.order_by('name')
    teacherList = school.teacher_set.order_by('last_name', 'first_name')
    t = loader.get_template(os.path.join('school', 'teacher_vs_class.html'))
    c = RequestContext(request, {'message': message,
                                 'blockList': blockList,
                                 'classList': classList,
                                 'teacherList': teacherList,
                                 'pos': pos, })
    return HttpResponse(t.render(c))

@need_login
@school_function
def classtab(request, block_id=0):
    pos = get_position(request)
    if pos == 1:
        url = reverse('class_detail',
                args=[str(get_student(request).current_class().id)])
        return HttpResponseRedirect(url)
    message = None
    school = get_school(request)
    school_id = school.id
    form = ClassForm(school_id)
    cyear = get_current_year(request)
    if not int(block_id):
        classList = cyear.class_set.order_by('name')
    else:
        block = school.block_set.get(id=int(block_id))
        classList = block.class_set.order_by('name')
    cfl = []
    num = []
    for c in classList:
        cfl.append(ClassForm(school_id, instance=c))
        num.append(c.students().count())
    if request.method == 'POST':
        if request.is_ajax() and request.POST['request_type'] == u'update':
            class_id = request.POST['id']
            c = classList.get(id=int(class_id))
            tc = None
            if request.POST['teacher_id'] != u'':
                teacher_id = request.POST['teacher_id']
                teacher = school.teacher_set.get(id=int(teacher_id))
                try:
                    tc = cyear.class_set.get(teacher_id__exact=teacher.id)
                except ObjectDoesNotExist:
                    pass
            else:
                teacher_id = None
            if not teacher_id or not tc:
                data = {'name': c.name,
                        'year_id': c.year_id.id,
                        'block_id': c.block_id.id,
                        'teacher_id': teacher_id,
                        'status': c.status,
                        'index': c.index}
                form = ClassForm(school_id, data, instance=c)
                if form.is_valid():
                    form.save()
            else:
                message = u'Giáo viên đã có lớp chủ nhiệm'
                data = simplejson.dumps({'message': message})
                return HttpResponse(data, mimetype='json')
        elif request.POST['request_type'] == 'update_all':
            teacher_list = request.POST.getlist('teacher_id')
            i = 0
            c = None
            for c in classList:
                try:
                    t = school.teacher_set.get(id=int(teacher_list[i]))
                except Exception:
                    t = None
                c.teacher_id = t
                c.save()
                i += 1
            cfl.append(ClassForm(school_id, instance=c))
            url = reverse('classes')
            return HttpResponseRedirect(url)
    list = zip(classList, cfl, num)
    teachers = school.teacher_set.all()
    t = loader.get_template(os.path.join('school', 'classtab.html'))
    c = RequestContext(request, {'list': list,
                                 'form': form,
                                 'message': message,
                                 'classList': classList,
                                 'block_id': block_id,
                                 'teachers': teachers,
                                 'pos': pos, })
    return HttpResponse(t.render(c))

