# -*- coding: utf-8 -*-
from datetime import datetime
import os
from django.http import HttpResponseNotAllowed, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
from app.models import Organization
from school.models import Pupil, TKDiemDanh, Attend, StartYear, Mark, Class,\
        Teacher, Subject, TKMon, DiemDanh, Year
from sms.models import sms, get_tsp, regc
from school.school_settings import CAP2_DS_MON, CAP1_DS_MON, CAP3_DS_MON
from school.templateExcel import normalize, CHECKED_DATE
from school.utils import to_en1, add_subject, get_lower_bound,\
        queryset_to_dict, get_current_year
from school.utils import normalize as norm
from sms.utils import to_ascii
from django.db import transaction
from django.db.models import Q
import thread
SYNC_RESULT = os.path.join('helptool','recover_marktime.html')
SYNC_SUBJECT = os.path.join('helptool','sync_subject.html')
TEST_TABLE = os.path.join('helptool','test_table.html')
REALTIME = os.path.join('helptool','realtime_test.html')
CONVERT_MARK= os.path.join('helptool','convert_mark.html')


def check_tbnam():
    schools = Organization.objects.filter(level='T')
    for school in schools:
        years = school.year_set.all()
        sts = school.get_students()
        for year in years:
            for st in sts:
                tbs = st.tbnam_set.filter(year_id=year)
                if len(tbs) > 1:
                    print '---------------'
                    for tb in tbs:
                        print tb.number_subject, tb.id
                        if tb.number_subject == 0: tb.delete()
                    print tbs
                    print st.id, st, year, school

def check_subject_type():
    classes = Class.objects.all()
    number = 0
    for c in classes:
        try:
            c.subject_set.get(type=u'Toán')
            c.subject_set.get(type=u'Ngữ văn')
        except Exception as e:
            number += 1
            print '------------------------------'
            print c, c.id, c.block_id.school_id
            print 'subjects'
            subs = c.subject_set.all()
            for s in subs:
                print s.id, s.name, s.type
            print e
    print 'There are %s class having wrong subject setting' % number

def fail_all_pending_sms():
    sms.objects.filter(recent=True).update(recent=False)

def _tsp_statistic(school=None):
    if school:
        teacher_phone = school.teacher_set.exclude(sms_phone='').values('sms_phone')
        student_phone = school.pupil_set.exclude(sms_phone='').values('sms_phone')
    else:
        teacher_phone = Teacher.objects.exclude(sms_phone='').values('sms_phone')
        student_phone = Pupil.objects.exclude(sms_phone='').values('sms_phone')
    phones = []
    for tphone in teacher_phone:
        phones.append(tphone['sms_phone'])
    for sphone in student_phone:
        phones.append(sphone['sms_phone'])
    total = len(phones)
    result = {}
    for p in phones:
        tsp = get_tsp(p)
        if not tsp:
            tsp = 'OTHERS'
            header = regc(p)
            if not header: print p, 'invalid format'
            else:
                print header.groups()[1]
        if tsp in result: result[tsp] += 1
        else: result[tsp] = 1
    print 'total', total
    for re in result.items():
        print re[0], re[1]

@transaction.commit_on_success
def _sync_start_year():
    school = Organization.objects.all()
    for s in school:
        stys = s.year_set.all()
        dict = {}
        for sty in stys:
            if sty.time in dict:
                dict[sty.time].append(sty)
            else:
                dict[sty.time] = [sty]
        for i in dict.items():
            l = i[1]
            if len(l) > 1:
                for ll in l:
                    print ll.id, ll, s

@transaction.commit_on_success
def _sync_sms_content():
    smses = sms.objects.all()
    number = 0
    sms_dict = {}
    for s in smses:
        key = '%s-%s' % (s.phone, s.content)
        if key in sms_dict:
            sms_dict[key].append(s)
        else:
            sms_dict[key] = [s]
    for item in sms_dict.items():
        key = item[0]
        sms_list = item[1]
        if len(sms_list) > 1:
            number += 1
            saved = None
            for s in sms_list:
                if s.success:
                    saved = s
            if not saved: saved = sms_list[0]
            for s in sms_list:
                if s != saved: s.delete()
    return sms_dict

@transaction.commit_on_success
def _sync_sms_type():
    smses = sms.objects.all()
    for s in smses:
        if 'diem moi' in s.content.lower():
            s.type = 'THONG_BAO'
            s.save()

@transaction.commit_on_success
def _sync_sms_reason():
    smses = sms.objects.filter(success=False)
    smses.update(failed_reason='25')

@transaction.commit_on_success
def _sync_sms_receiver():
    smses = sms.objects.all()
    # Get all students and teachers with their phone numbers
    # Now we have id and sms_phone
    students = Pupil.objects.exclude(sms_phone='')\
            .defer('sms_phone', 'id', 'user_id')
    st_acc_id_list = [st.user_id_id for st in students]
    teachers = Teacher.objects.exclude(sms_phone='')\
            .defer('sms_phone', 'id', 'user_id')
    te_acc_id_list = [te.user_id_id for te in teachers]
    # Fetch all accounts of those people
    accs = User.objects.filter(
            id__in=st_acc_id_list + te_acc_id_list)
    acc_dict = queryset_to_dict(accs)
    st_acc_dict = {}
    for st in students:
        st_acc_dict[st.id] = acc_dict[st.user_id_id]
    te_acc_dict = {}
    for te in teachers:
        te_acc_dict[te.id] = acc_dict[te.user_id_id]
    # Build up map from phone number to people
    phone_map = {}
    for st in students:
        if st.sms_phone:
            if st.sms_phone in phone_map:
                phone_map[st.sms_phone].append(st)
                #print st.sms_phone, st.full_name()
            else:
                phone_map[st.sms_phone] = [st]
    for te in teachers:
        if te.sms_phone:
            if te.sms_phone in phone_map:
                phone_map[te.sms_phone].append(te)
                #print te.sms_phone, te.full_name()
            else:
                phone_map[te.sms_phone] = [te]
    number = 0
    for s in smses:
        if not s.receiver:
            phone = '0' + s.phone[2:]
            if phone in phone_map:
                person = phone_map[phone]
                if len(person) == 1:
                    person = person[0]
                    if isinstance(person, Pupil):
                        s.receiver = st_acc_dict[person.id]
                    else:
                        s.receiver = te_acc_dict[person.id]
                    s.save()
                    number += 1
                else:
                    decided = None
                    for p in person:
                        short_name = to_ascii(p.short_name())
                        full_name = to_ascii(p.full_name())
                        if short_name in s.content or full_name in s.content:
                            decided = p
                            if isinstance(decided, Pupil):
                                s.receiver = st_acc_dict[decided.id]
                            else:
                                s.receiver = te_acc_dict[decided.id]
                            s.save()
                            number += 1
                            break
                    print 'Confusing to detect phone owner for %s' % phone
                    #print 'Decided: ', decided
                    #print 'Content: ', s.content 
            else:
                print 'Cant find owner for the phone number %s' % phone
    print 'Number: ', number

def _sync_sms_recent():
    smses = sms.objects.all()
    smses.update(recent=False)

def _sync_pupil_disable():
    #those students have current class
    attends = Attend.objects.filter(leave_time=None).values('pupil_id')
    #students that do not have current class
    students = Pupil.objects.filter(~Q(id__in=attends))
    students.update(disable=True)

def _sync_current():
    def finish_class(cl, st):
        at = Attend.objects.filter(pupil=st, _class=cl)
        for a in at:
            if a.is_member: return True
        return False

    sts = Pupil.objects.all()
    print len(sts)
    number = 0
    for st in sts:
        number += 1
        cl = st.current_class()
        marks = st.mark_set.all()
        for m in marks:
            #check current = False
            if not m.current:
                the_cl = m.subject_id.class_id
                if the_cl == cl or finish_class(the_cl, st):
                    print '--'
                    print 'number', number
                    print st
                    print the_cl
                    print m, the_cl.block_id.school_id, the_cl.block_id.school_id.id
                    m.current = True
                    m.save()
            else:
                the_cl = m.subject_id.class_id
                if the_cl != cl and not finish_class(the_cl, st):
                    print '--'
                    print 'number', number
                    print st
                    print the_cl
                    print m, the_cl.block_id.school_id, the_cl.block_id.school_id.id
                    m.current = False
                    m.save()
        tkmons = st.tkmon_set.all()
        for m in tkmons:
            if not m.current:
                the_cl = m.subject_id.class_id
                if the_cl == cl or finish_class(the_cl, st):
                    print '--'
                    print 'number', number
                    print st
                    print the_cl
                    print m, the_cl.block_id.school_id, the_cl.block_id.school_id.id
                    m.current = True
                    m.save()
            else:
                the_cl = m.subject_id.class_id
                if the_cl != cl and not finish_class(the_cl, st):
                    print '--'
                    print 'number', number
                    print st
                    print the_cl
                    print m, the_cl.block_id.school_id, the_cl.block_id.school_id.id
                    m.current = False
                    m.save()
                    
@transaction.commit_on_success
def sync_current(request):
    _sync_current()
    message = 'Done'
    context = RequestContext(request)
    return render_to_response( SYNC_RESULT, { 'message' : message},
        context_instance = context )

@transaction.commit_on_success
def fix_tkdd(request):
    student_list = Pupil.objects.all()
    for std in student_list:
        tkdd_list = std.tkdiemdanh_set.all()
        for tkdd in tkdd_list:
            term = tkdd.term_id
            tkdd.co_phep = std.diemdanh_set.filter(term_id = term, loai = u'P').count()
            tkdd.khong_phep = std.diemdanh_set.filter(term_id = term, loai = u'K').count()
            tkdd.tong_so = tkdd.co_phep + tkdd.khong_phep
            tkdd.muon = std.diemdanh_set.filter(term_id = term, loai = u'M').count()
            tkdd.save()
    message = 'Done'
    context = RequestContext(request)
    return render_to_response( SYNC_RESULT, { 'message' : message},
        context_instance = context )

@transaction.commit_on_success
def sync_tkdd(request):
    tkdds = TKDiemDanh.objects.all()
    for tkdd in tkdds:
        if tkdd.tong_so==None: tkdd.tong_so=0
        if tkdd.co_phep==None: tkdd.co_phep=0
        if tkdd.khong_phep==None: tkdd.khong_phep=0
        tkdd.save()
    message = 'Done'
    context = RequestContext(request)
    return render_to_response( SYNC_RESULT, { 'message' : message},
                               context_instance = context )

@transaction.commit_on_success
def sync_is_member(request):
    err_ats = Attend.objects.filter(is_member=False)
    for at in err_ats:
        st = at.pupil
        att = Attend.objects.filter(is_member=True, pupil=st)[0]
        olds = err_ats.filter(pupil=st,
                _class__year_id__time=att._class.year_id.time-1).order_by(
                '-leave_time')
        if len(olds) == 1:
            olds[0].is_member = True
            olds[0].save()
        print '...', at._class, at._class.year_id, at.pupil, at.pupil.school_id
    message = 'Done'
    context = RequestContext(request)
    return render_to_response( SYNC_RESULT, { 'message' : message},
                               context_instance = context )

@transaction.commit_on_success
def sync_start_year(request):
    st_years = StartYear.objects.all()
    number = 0
    for sty in st_years:
        dups = st_years.filter(time=sty.time,
                                school_id=sty.school_id)\
                        .exclude(id=sty.id)
        if dups:
            print sty.school_id, sty.school_id_id, sty.time, dups[0].id, sty.id
            number += 1
    wrong_number = 0
    for year in Year.objects.all():
        school = year.school_id
        lb = get_lower_bound(school)
        sts = Pupil.objects.filter(school_id=school)
        for st in sts:
            first_cl = st.first_class()
            if first_cl:
                syear = first_cl.year_id.time - first_cl.block_id.number + lb
                if st.start_year_id.time != syear:
                    sty, temp = StartYear.objects.get_or_create(school_id=school,
                                    time=syear)
                    st.start_year_id = sty
                    st.save()
                    wrong_number += 1
                    print st, st.school_id, first_cl, st.start_year_id.time, syear
            
    verified = True
    invalid_name = 0
    sts = Pupil.objects.all()
    for st in sts:
#        birthyear = st.birthday.year
#        school = st.school_id
#        if school.school_level == '3':
#            syear = birthyear + 15
#        elif school.school_level == '2':
#            syear = birthyear + 11
#        if not st.start_year_id:
#            print '**', st, st.school_id
#        if syear != st.start_year_id.time:
#            verified = False
#            print '--',st, st.school_id, st.current_class(), st.start_year_id, syear
        firstname = st.first_name
        lastname = st.last_name
        father_name = st.father_name
        mother_name = st.mother_name
        new_firstname = norm(firstname)
        new_lastname = norm(lastname)
        new_father_name = norm(father_name)
        new_mother_name = norm(mother_name)

        if new_firstname != firstname or new_lastname != lastname or\
            new_father_name != father_name or new_mother_name != mother_name:

            st.first_name = new_firstname
            st.last_name = new_lastname
            st.father_name = new_father_name
            st.mother_name = new_mother_name
            invalid_name += 1
            try:
                st.save()
            except Exception as e:
                print e
                print st.id, st.first_name, st.last_name, st.school_id, st.current_class()

    print wrong_number, verified, invalid_name
    message = 'Done'
    context = RequestContext(request)
    return render_to_response( SYNC_RESULT, { 'message' : message},
                               context_instance = context )


def convert_data_1n_mn(request):
    classes = Class.objects.all()
    for _class in classes:
        print _class.attend_set.all()
    students = Pupil.objects.all()
    for student in students:
        _class = student.class_id
        if not _class:
            print student, student.get_school()
        else:
            student.join_class(_class, student.school_join_date)
    message = 'Done'
    context = RequestContext(request)
    return render_to_response( SYNC_RESULT, { 'message' : message},
                               context_instance = context )

def make_setting(request):

    orgs = Organization.objects.all()
    for org in orgs:
        if org.level == u'T':
            school = org
            try:
                last_year = school.year_set.latest('time')
                lock_time = school.get_setting('lock_time')
                if int(lock_time) == 24:
                    school.save_settings('lock_time', 24)
                print org
                classes = last_year.class_set.all()
                class_labels = u'['
                for _class in classes:
                    names = _class.name.split(' ')
                    if len(names) > 1:
                        try:
                            a = int(names[0])
                            class_labels += "u'%s'," % ' '.join(names)
                        except Exception as e:
                            print e
                            continue
                class_labels = class_labels[:-1] + u']'
                school.save_settings('class_labels', class_labels)
            except Exception as e:
                continue
    message = 'done'
    context = RequestContext(request)
    return render_to_response( SYNC_RESULT, { 'message' : message},
                               context_instance = context )

@transaction.commit_on_success
def sync_major(request):
    message = ''
    number = 0
    if request.method == 'GET':
        print 'get'
        number = 0
        teachers = Teacher.objects.all()
        for teacher in teachers:
            if teacher.major == '-1': number += 1
        message += u'%s subjects need to change to nx' % number
    elif  request.method == 'POST':
        print 'POST'
        if 'sync' in request.POST:
            teachers = Teacher.objects.all()
            for teacher in teachers:
                if teacher.major == '-1':
                    number += 1
                    teacher.major = ''
                    teacher.save()
            message += "<br><p>Syncing teacher's major: Done</p> number: " + unicode(number)
    context = RequestContext(request)
    return render_to_response(SYNC_SUBJECT, {'message': message, 'number': number},
        context_instance = context)

@transaction.commit_on_success
def sync_class_name(request):
    message = ''
    number = 0
    import re
    digit = re.compile('\d+')
    if request.method == 'GET':
        print 'get'
        number = 0
        classes = Class.objects.all()
        for _class in classes:
            if len(_class.name.split(' ')) <=1: number += 1
        message += u'%s class names need to change' % number
    elif  request.method == 'POST':
        print 'POST'
        if 'sync' in request.POST:
            classes = Class.objects.all()
            for _class in classes:
                if len(_class.name.split(' ')) <=1:
                    print _class
                    m = digit.match(_class.name)
                    if not m:
                        print _class.year_id.school_id
                        continue
                    grade = m.group(0)
                    print grade
                    _class.name = grade + _class.name.replace(grade, ' ')
                    print _class.name
                    _class.save()
                    number += 1
            message += "<br><p>Syncing class names: Done</p> number: " + unicode(number)
    context = RequestContext(request)
    return render_to_response(SYNC_SUBJECT, {'message': message, 'number': number},
        context_instance = context)

@transaction.commit_on_success
def sync_name(request):
    message = ''
    number = 0
    if request.method == 'GET':
        print 'get'
        teachers = Teacher.objects.all()
        students = Pupil.objects.all()
        number = len(teachers) + len(students)
        message += u'%s name -> user: first_name, last_name' % number
    elif  request.method == 'POST':
        print 'POST'
        if 'sync' in request.POST:
            teachers = Teacher.objects.all()
            for teacher in teachers:
                teacher.user_id.first_name = teacher.first_name
                teacher.user_id.last_name = teacher.last_name
                teacher.user_id.save()
                number += 1
            students = Pupil.objects.all()
            for student in students:
                student.user_id.first_name = student.first_name
                student.user_id.last_name = student.last_name
                student.user_id.save()
                number += 1
            message += "User: first_name, last_name: Done  number: " + unicode(number)
    context = RequestContext(request)
    return render_to_response(SYNC_SUBJECT, {'message': message, 'number': number},
        context_instance = context)

@transaction.commit_on_success
def sync_birthday(request):
    message = ''
    number = 0
    if request.method == 'GET':
        print 'get'
        number = 0
        students = Pupil.objects.all()
        for student in students:
            if 20 < student.birthday.year < 100: number += 1
            elif student.birthday.year <= 20: number += 1
        message += u'%s student birthday need to validate' % number
    elif  request.method == 'POST':
        print 'POST'
        if 'sync' in request.POST:
            students = Pupil.objects.all()
            for student in students:
                if 20 < student.birthday.year < 100:
                    student.birthday = datetime(student.birthday.year + 1900, student.birthday.month, student.birthday.day)
                    student.save()
                    number += 1
                elif student.birthday.year <= 20:
                    student.birthday = datetime(student.birthday.year + 2000, student.birthday.month, student.birthday.day)
                    student.save()
                    number += 1
            message += "Syncing birthday: Done | number: " + unicode(number)
    context = RequestContext(request)
    return render_to_response(SYNC_SUBJECT, {'message': message, 'number': number},
        context_instance = context)

@transaction.commit_on_success
def sync_index(request):

    classes = Class.objects.all()
    message = ''
    try:
        for _class in classes:
            students = _class.pupil_set.order_by('index')
            index = 0
            for student in students:
                index +=1
                print student.index, index
                if not student.first_name.strip():
                    message += '\n' + student.last_name + ': wrong name'
                    names = student.last_name.strip().split(' ')
                    last_name = ' '.join(names[:len(names)-1])
                    first_name = names[len(names)-1]
                    try:
                        student.first_name = first_name
                        student.last_name = last_name
                        student.save()
                    except Exception as e:
                        print e
                if student.index != index:
                    student.index = index
                    student.save()
            _class.max = index
            _class.save()

    except Exception as e:
        print e
    message += '\n' + u'Sync xong index.'
    context = RequestContext(request)
    return render_to_response( SYNC_RESULT, { 'message' : message},
                               context_instance = context )
@transaction.commit_on_success
def disable_student():
    students = Pupil.objects.all()
    number = 0
    for student in students:
        user = student.user_id
        try:
            if user.check_password(user.username):
                user.is_active = False
                user.save()
                number += 1
        except Exception as e:
            print e
            print user.username

@transaction.commit_on_success
def disable_user(request):
    teachers = Teacher.objects.all()
    message = ''
    number = 0
    thread.start_new_thread(disable_student, ())
    for teacher in teachers:
        user = teacher.user_id
        try:
            if user.check_password(user.username):
                user.is_active = False
                user.save()
                number += 1
                print number
        except Exception as e:
            print e
            print user.username
    message += u'Sync xong ' + unicode(number) + u' teacher users.'
    context = RequestContext(request)
    return render_to_response( SYNC_RESULT, { 'message' : message},
        context_instance = context )

#
#@transaction.commit_on_success
#def copy_hanh_kiem_data(request):
#
#    students = Pupil.objects.all()
#    number = 0
#    message = ''
#    try:
#        for student in students:
#            tbnams = TBNam.objects.filter(student_id = student)
#            for tbnam in tbnams:
#                print tbnam.student_id, tbnam.year_id
#                hk = HanhKiem.objects.filter(student_id=student, year_id=tbnam.year_id )
#                if len(hk)>1:
#                    for h in hk:
#                        print h.student_id, h.year_id, h.term1, h.term2, h.year, h.ren_luyen_lai, h.hk_ren_luyen_lai
#                number += 1
#                tbnam.term1 = hk[0].term1
#                tbnam.term2 = hk[0].term2
#                tbnam.year = hk[0].year
#                tbnam.ren_luyen_lai = hk[0].ren_luyen_lai
#                tbnam.hk_ren_luyen_lai = hk[0].hk_ren_luyen_lai
#                tbnam.save()
#        message += '\n' + u'Copy xong.' + str(number)
#    except Exception as e:
#        print e
#    context = RequestContext(request)
#    return render_to_response( SYNC_RESULT, { 'message' : message},
#                               context_instance = context )

@transaction.commit_on_success
def sync_subject(request):
    classes = Class.objects.all()
    print classes
    message = ''
    number = 0
    try:
        if request.method == 'GET':
            print 'get'
            for _class in classes:
                if not _class.subject_set.count():
                    number+=1
            print 'message'
            message = u'<p>Have ' + str(number) + ' classes those have no subject.</p>'

            number = 0
            subjects = Subject.objects.all()
            for subject in subjects:
                if subject.primary:
                    number += 1
            message += u'<br><p>%s subjects in database have non zero primary </p>' % number
        elif  request.method == 'POST':
            print 'POST'
            if 'sync' in request.POST:
                for _class in classes:
                    school = _class.year_id.school_id
                    if not school.status:
                        school.status = 1
                        school.save()
                    if school.school_level == '1': ds_mon_hoc = CAP1_DS_MON
                    elif school.school_level == '2': ds_mon_hoc = CAP2_DS_MON
                    elif school.school_level == '3': ds_mon_hoc = CAP3_DS_MON
                    else: raise Exception('SchoolLevelInvalid')

                    if not _class.subject_set.count():
                        index = 0
                        for mon in ds_mon_hoc:
                            index +=1
                            print index
                            add_subject(subject_name= mon, subject_type= mon, _class=_class, index=index)
                message = '<p>Syncing subject from all classes: Done </p>'
                print 'tag'
                subjects = Subject.objects.all()
                for subject in subjects:
                    if subject.primary == 1:
                        subject.primary = 0
                        subject.save()
                message += "<br><p>Syncing subject's primary: Done</p>"
        context = RequestContext(request)
        return render_to_response(SYNC_SUBJECT, {'message': message, 'number': number},
                                  context_instance = context)
    except Exception as e:
        print e


@transaction.commit_on_success
def check_logic(request):
    message = ''
    number = 0
    try:
        if request.method == 'GET':
            print 'get'
#            students = Pupil.objects.all()
#            for student in students:
#                marks = Mark.objects.filter(student_id__exact = student)
#                for mark in marks:
#                    if student.class_id.year_id.school_id != mark.subject_id.class_id.year_id.school_id:
#                        number+=1
#                        print student, student.class_id, student.class_id.year_id.school_id, mark.subject_id.class_id, mark.subject_id.class_id.year_id.school_id, mark.subject_id
#            print 'message'
            tkmons = TKMon.objects.all()
            wrong_logic = 0
            for tk in tkmons:
                student = tk.student_id
                subject = tk.subject_id
                if student.class_id != subject.class_id:
                    wrong_logic += 1

            message = u'<p>Have ' + str(number) + ','+ str(wrong_logic) + ' students that have bugs.</p>'

            number = 0
            classes = Class.objects.all()
            for _class in classes:
                expected_tkmon_number = _class.subject_set.count() * _class.students().count()
                tkmon_number = 0
                subjects = Subject.objects.filter( class_id = _class)
                for subject in subjects:
                    tkmon_number += subject.tkmon_set.count()
                if expected_tkmon_number != tkmon_number:
                    message += r'<li>'+unicode(_class.year_id.school_id) + ':'\
                               + unicode(_class)+':' \
                               + str(expected_tkmon_number) + '----' + str(tkmon_number) + r'</li>'
                number += _class.subject_set.count() * _class.students().count()
            message += r'<li>' + 'Expected tkmon: ' + str(number) + r'</li>'
            message += ':' + str(TKMon.objects.count())
            tkmons = TKMon.objects.all()
            if number == TKMon.objects.count():
                message += 'OK'
        elif  request.method == 'POST':
            print 'POST'
            message = ''
            number = 0
            classes = Class.objects.all()
            for _class in classes:
                subjects = _class.subject_set.all()
                students = _class.pupil_set.all()
                for student in students:
                    for subject in subjects:
                        a = TKMon.objects.filter(student_id = student, subject_id = subject)
                        if not a:

                            print '*', student.get_school(), student.class_id, student, subject
                            a = TKMon.objects.create(student_id = student, subject_id = subject)
                            number += 1
                        elif len(a) >= 2:
                            print '__',student.get_school(), student.class_id, student, subject
                            aa = a[1]
                            aa.delete()
            message += r'Done:' + str(number)
#            if 'sync' in request.POST:
#                for _class in classes:
#                    school = _class.year_id.school_id
#                    if not school.status:
#                        school.status = 1
#                        school.save()
#                    if school.school_level == '1': ds_mon_hoc = CAP1_DS_MON
#                    elif school.school_level == '2': ds_mon_hoc = CAP2_DS_MON
#                    elif school.school_level == '3': ds_mon_hoc = CAP3_DS_MON
#                    else: raise Exception('SchoolLevelInvalid')
#
#                    if not _class.subject_set.count():
#                        index = 0
#                        for mon in ds_mon_hoc:
#                            index +=1
#                            print index
#                            add_subject(subject_name= mon, subject_type= mon, _class=_class, index=index)
#                message = '<p>Syncing subject from all classes: Done </p>'
#                print 'tag'
#                subjects = Subject.objects.all()
#                for subject in subjects:
#                    if subject.primary == 1:
#                        subject.primary = 0
#                        subject.save()
#                message += "<br><p>Syncing subject's primary: Done</p>"
        context = RequestContext(request)
        return render_to_response(SYNC_SUBJECT, {'message': message, 'number': number},
                                  context_instance = context)
    except Exception as e:
        print e

def notice_subject_type(subject_name):
    subject = to_en1(subject_name).lower()
    if subject.find('toan') != -1: return u'Toán'
    elif subject.find('van') != -1: return u'Ngữ văn'
    elif subject.find('dia') != -1 or subject.find('di a') != -1: return u'Địa lí'
    elif subject.find('vat') != -1 or subject.find('li') != -1 or subject.find('ly') != -1: return u'Vật lí'
    elif subject.find('hoa') != -1: return u'Hóa học'
    elif subject.find('sinh') != -1: return u'Sinh học'
    elif subject.find('tin') != -1: return u'Tin học'
    elif subject.find('su') != -1: return u'Lịch sử'
    elif subject.find('anh') != -1 or subject.find('ngoai') != -1: return u'Ngoại ngữ'
    elif subject.find('phap') != -1 or subject.find('nga') != -1 or subject.find('duc') != -1\
        or subject.find('nhat') != -1 or subject.find('tieng hoa') != -1 or subject.find('trung quoc') !=-1: return u'NN2'
    elif subject.find('cong dan') != -1 or subject.find('cd') != -1 or subject.find('c d') != -1: return u'GDCD'
    elif subject.find('cong nghe') != -1: return u'Công nghệ'
    elif subject.find('the duc') != -1: return u'Thể dục'
    elif subject.find('quoc phong') != -1 or subject.find('qp') != -1 or subject.find('q p') != -1: return u'GDQP-AN'
    elif subject.find('nhac') != -1: return u'Âm nhạc'
    elif subject.find('mi') != -1 or subject.find('my') != -1: return u'Mĩ thuật'
    else:
        raise Exception('BadSubjectName')

@transaction.commit_on_success
def sync_subject_nx(request):
    message = ''
    number = 0
    if request.method == 'GET':
        print 'get'
        number = 0
        subjects = Subject.objects.all()
        for subject in subjects:
            if (subject.type == u'Âm nhạc' or subject.type == u'Mĩ thuật' or subject.type == u'Thể dục') and not subject.nx:
                number += 1
        message += u'%s subjects need to change to nx' % number
    elif  request.method == 'POST':
        print 'POST'
        if 'sync' in request.POST:
            print 'tag'
            subjects = Subject.objects.all()
            number = 0
            for subject in subjects:
                if subject.type == u'Âm nhạc' or subject.type == u'Mĩ thuật' or subject.type == u'Thể dục':
                    number += 1
                    subject.nx = True
                    subject.save()
            message += "<br><p>Syncing subject's nx: Done</p> number: " + unicode(number)
    context = RequestContext(request)
    return render_to_response(SYNC_SUBJECT, {'message': message, 'number': number},
        context_instance = context)

@transaction.commit_on_success
def sync_subject_type(request):
    message = ''
    number = 0
    try:
        if request.method == 'GET':
            number = 0
            subjects = Subject.objects.all()
            for subject in subjects:
                if not subject.type or subject.type == '-1' or ( not subject.type in CAP2_DS_MON and not subject.type in CAP3_DS_MON):
                    number += 1
            message += u'<br><p>%s subjects in database do not have correct type </p>' % number
            number = 0
            classes = Class.objects.all()
            for cl in classes:
                subjects = cl.subject_set.all()
                container = []
                for subject in subjects:
                    if subject.type in container:
                        number += 1
                        print subject, subject.type, cl, cl.year_id.school_id
                        print cl.id, subject.id
                    else:
                        container.append(subject.type)
            message += u'Duplicate subject type: %s' % number
        elif  request.method == 'POST':
            print 'POST'
            if 'sync' in request.POST:
                print 'tag'
                subjects = Subject.objects.all()
                number = 0
                for subject in subjects:
                    if not subject.type or subject.type == '-1' or ( not subject.type in CAP2_DS_MON and not subject.type in CAP3_DS_MON):
                        try:
                            subject.type = notice_subject_type(subject.name)
                            subject.save()
                        except Exception:
                            number += 1
                message += "<br><p>Syncing subject's type: Done</p> except: " + unicode(number)
        context = RequestContext(request)
        return render_to_response(SYNC_SUBJECT, {'message': message, 'number': number},
                                  context_instance = context)
    except Exception as e:
        print e

@transaction.commit_on_success
def sync_subject_primary(request):
    subjects = Subject.objects.all()
    for subject in subjects:
        if subject.primary:
            subject.primary = 0
            subject.save()
    message = "Syncing subject's primary is done"
    context = RequestContext(request)
    return render_to_response( SYNC_RESULT, { 'message' : message},
                               context_instance = context )


def test_table(request):
    context = RequestContext(request)
    student_list = [x for x in range(1,70)]
    mark_list = [x for x in range(1,20)]
    return render_to_response( TEST_TABLE, {'mark_list': mark_list,
                                            'student_list': student_list}, context_instance = context)

#def realtime(request):
#    print request.session.session_key
#    return render_to_response( REALTIME, {
#        "user":request.user,
#        "CHANNEL_NAME":'message',
#        "STOMP_PORT":settings.STOMP_PORT,
#        "HOST":settings.INTERFACE,
#        "SESSION_COOKIE_NAME": settings.SESSION_COOKIE_NAME
#    }, context_instance = RequestContext(request))

#class myHTTPTransport(HTTPTransport):
#    username = None
#    password = None
#    @classmethod
#    def setAuthen(cls, u, p):
#        cls.username = u
#        cls.password = p
#    def call(self, addr, data, namespace, soapaction=None,
#             encoding=None, http_proxy=None, config=Config, timeout=None):
#        if not isinstance(addr, SOAPAddress):
#            addr=SOAPAddress(addr, config)
#        if self.username != None:
#            addr.user = self.username + ':' + self.password
#        return HTTPTransport.call(self, addr, data, namespace, soapaction, encoding, http_proxy, config, timeout)
def convertaMark(mark,sent,time,markStr,markSMS,markTime,pre,number):
    if mark!=None:
        markStr+='*'*(number-pre)+normalize(mark)
        if time==None:
            markTime+='*'*(number-pre)
        else:
            markTime+='*'*(number-pre)+str(int((time-CHECKED_DATE).total_seconds()/60))
        if sent=='1':
            markSMS+='*'*(number-pre)+'1'
        else:
            markSMS+='*'*(number-pre)
        pre=number
        
    return markStr,markSMS,markTime,pre

@transaction.commit_on_success
def convertMark(request):

    #subjects = Subject.objects.filter(id=328)
    subjects = Subject.objects.all()
    tong=0
    for s in subjects:
        #print "fffffffffffffff",to_en1(s.class_id.year_id.school_id.name)
        tong+=1
        if tong % 10==0: print tong
        #print tong
        for i in range(1,3):
            markList =Mark.objects.filter(subject_id=s.id,term_id__number=i).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday')
            timeList =MarkTime.objects.filter(mark_id__subject_id=s.id,mark_id__term_id__number=i).order_by('mark_id__student_id__index','mark_id__student_id__first_name','mark_id__student_id__last_name','mark_id__student_id__birthday')
            tkMonList=TKMon.objects.filter(subject_id=s.id).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday')
            for m,mt,tkMon in zip(markList,timeList,tkMonList):

                miengStr=''
                miengSMS=''
                miengTime=''
                pre=1
                miengStr,miengSMS,miengTime,pre=convertaMark(m.mieng_1,m.sent_mark[0],mt.mieng_1,miengStr,miengSMS,miengTime,pre,1)
                miengStr,miengSMS,miengTime,pre=convertaMark(m.mieng_2,m.sent_mark[1],mt.mieng_2,miengStr,miengSMS,miengTime,pre,2)
                miengStr,miengSMS,miengTime,pre=convertaMark(m.mieng_3,m.sent_mark[2],mt.mieng_3,miengStr,miengSMS,miengTime,pre,3)
                miengStr,miengSMS,miengTime,pre=convertaMark(m.mieng_4,m.sent_mark[3],mt.mieng_4,miengStr,miengSMS,miengTime,pre,4)
                miengStr,miengSMS,miengTime,pre=convertaMark(m.mieng_5,m.sent_mark[4],mt.mieng_5,miengStr,miengSMS,miengTime,pre,5)

                mlamStr=''
                mlamSMS=''
                mlamTime=''
                pre=1
                mlamStr,mlamSMS,mlamTime,pre=convertaMark(m.mlam_1,m.sent_mark[5],mt.mlam_1,mlamStr,mlamSMS,mlamTime,pre,1)
                mlamStr,mlamSMS,mlamTime,pre=convertaMark(m.mlam_2,m.sent_mark[6],mt.mlam_2,mlamStr,mlamSMS,mlamTime,pre,2)
                mlamStr,mlamSMS,mlamTime,pre=convertaMark(m.mlam_3,m.sent_mark[7],mt.mlam_3,mlamStr,mlamSMS,mlamTime,pre,3)
                mlamStr,mlamSMS,mlamTime,pre=convertaMark(m.mlam_4,m.sent_mark[8],mt.mlam_4,mlamStr,mlamSMS,mlamTime,pre,4)
                mlamStr,mlamSMS,mlamTime,pre=convertaMark(m.mlam_5,m.sent_mark[9],mt.mlam_5,mlamStr,mlamSMS,mlamTime,pre,5)

                motTietStr=''
                motTietSMS=''
                motTietTime=''
                pre=1
                motTietStr,motTietSMS,motTietTime,pre=convertaMark(m.mot_tiet_1,m.sent_mark[10],mt.mot_tiet_1,motTietStr,motTietSMS,motTietTime,pre,1)
                motTietStr,motTietSMS,motTietTime,pre=convertaMark(m.mot_tiet_2,m.sent_mark[11],mt.mot_tiet_2,motTietStr,motTietSMS,motTietTime,pre,2)
                motTietStr,motTietSMS,motTietTime,pre=convertaMark(m.mot_tiet_3,m.sent_mark[12],mt.mot_tiet_3,motTietStr,motTietSMS,motTietTime,pre,3)
                motTietStr,motTietSMS,motTietTime,pre=convertaMark(m.mot_tiet_4,m.sent_mark[13],mt.mot_tiet_4,motTietStr,motTietSMS,motTietTime,pre,4)
                motTietStr,motTietSMS,motTietTime,pre=convertaMark(m.mot_tiet_5,m.sent_mark[14],mt.mot_tiet_5,motTietStr,motTietSMS,motTietTime,pre,5)

                diem=miengStr +'|'+mlamStr+'|'+motTietStr
                sent=miengSMS +'|'+mlamSMS+'|'+motTietSMS
                time=miengTime+'|'+mlamTime+'|'+motTietTime
                #####################################################
                if m.ck!=None:
                    #diem+='|'+normalize(m.ck)
                    if (mt.ck==None):
                        time+='|'
                    else:
                        time+='|'+str(int((mt.ck-CHECKED_DATE).total_seconds()/60))
                    if m.sent_mark[15]==1:
                        sent+='|1'
                    else:
                        sent+='|'
                else:
                    #diem+='|'
                    sent+='|'
                    time+='|'
                #########################
                if m.tb!=None:
                    #diem+='|'+normalize(m.tb)
                    if (mt.tb==None):
                        time+='|'
                    else:
                        time+='|'+str(int((mt.tb-CHECKED_DATE).total_seconds()/60))
                    if i==1:
                        if m.sent_mark[16]==1:
                            sent+='|1'
                        else:
                            sent+='|'
                    else:
                        if m.sent_mark[17]==1:
                            sent+='|1'
                        else:
                            sent+='|'
                else:
                    #diem+='|'
                    sent+='|'
                    time+='|'

                if i==2:
                    if m.sent_mark[18]=='1':
                        tkMon.sent=True
                    else:
                        tkMon.sent=False

                m.diem=diem
                m.sent=sent
                m.time=time
                m.save()
                tkMon.save()

#
#                print m.mieng_1,m.mieng_2,m.mieng_3,m.mieng_4,m.mieng_5,
#                print m.mlam_1,m.mlam_2,m.mlam_3,m.mlam_4,m.mlam_5,
#                print m.mot_tiet_1,m.mot_tiet_2,m.mot_tiet_3,m.mot_tiet_4,m.mot_tiet_5
#                print m.ck,' ',m.tb
#                print diem
#                print sent
#                print time
#                print
#
    print CHECKED_DATE
    message = "convert is done"
    context = RequestContext(request)
    return render_to_response( CONVERT_MARK, { 'message' : message},
                               context_instance = context )


def convert_diem_danh(request):
    if request.user.is_superuser:
        ddl = DiemDanh.objects.filter(loai = u'Có phép')
        for dd in ddl:
            dd.loai = u'P'
            dd.save()
        ddl = DiemDanh.objects.filter(loai = u'Không phép')
        for dd in ddl:
            dd.loai = u'K'
            dd.save()
        return HttpResponse("Convert Done")
    else:
        return HttpResponseNotAllowed(302)

@transaction.commit_on_success
def _sync_subject_comment():
    set_subject = [u'Âm nhạc',u'Mĩ thuật',u'Thể dục']
    subject_list = Subject.objects.filter(class_id__year_id__time=2012,
            type__in=set_subject)
    print len(subject_list)
    number = 0
    for s in subject_list:
        number += 1
        if number % 100==0:
            print number
        s.nx = True
        s.save()

    subject_list = Subject.objects.filter(class_id__year_id__time=2012, hs=2)
    print len(subject_list)
    number = 0
    for s in subject_list:
        number += 1
        if number % 100==0:
            print number
        s.hs = 1
        s.save()


def sync_tkb_db(request):
    year = get_current_year(request)
    classList = Class.objects.filter(year_id=year).order_by('name')
    for cl in classList:
        tkbs = cl.tkb_set.all().order_by('day')
        previous_day = 0
        for i_tkb in tkbs:
            if i_tkb.day == previous_day:
                i_tkb.delete()
            else:
                previous_day = i_tkb.day

