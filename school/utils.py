# -*- coding: utf-8 -*-
import os
import random
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
import unicodedata
import re
import datetime as root_dt
from django.db.models import get_model
from django.contrib.auth.models import SiteProfileNotAvailable, User
from django.forms import forms
from app.models import UserProfile, Organization
from school.models import syllables, Pupil, Mark, TKMon, TBHocKy, TBNam, TKDiemDanh, Team, SUBJECT_LIST_ASCII,\
    Group, Subject, Teacher
import settings

def to_date(value):
    v = None
    if '-' in value:
        v = value.split('-')
    elif '/' in value:
        v = value.split('/')
    elif '.' in value:
        v = value.split('.')
    try:
        if int(v[2])<1900:
            raise Exception("PharseDateException")
        result = root_dt.date(int(v[2]), int(v[1]), int(v[0]))
    except Exception as e:
        print e
        raise Exception("PharseDateException")
    return result


#noinspection PyUnusedLocal
def to_en(string):
    result = ''
    uni_a = u'ăắẳẵặằâầấẩẫậàáảãạ'
    uni_o = u'óòỏõọơớờởỡợôốồỗộổ'
    uni_i = u'ìĩịỉí'
    uni_u = u'ủùũụúưừứựữử'
    uni_e = u'éèẽẻẹêếềễệể'
    uni_y = u'ýỳỷỹỵ'
    uni_d = u'đ'
    for char in string:
        c = char.lower()
        for cc in ['a','o','i','u','e','d','y']:
            exec("if c in uni_" + cc + ": c = " + "'" + cc + "'" )
        result += c
    return result
#noinspection PyUnusedLocal
def to_en1(string):
    result = ''
    uni_a = u'ăắẳẵặằâầấẩẫậàáảãạ'
    uni_A = u'ĂẮẲẴẶẰÂẦẤẨẪẬÀÁẢÃẠ'
    uni_o = u'óòỏõọơớờởỡợôốồỗộổ'
    uni_O = u'ÓÒỎÕỌƠỚỜỞỠỢÔỐỒỖỘỔ'
    uni_i = u'ìĩịỉí'
    uni_I = u'ÌĨỊỈÍ'
    uni_u = u'ủùũụúưừứựữử'
    uni_U = u'ỦÙŨỤÚƯỪỨỰỮỬ'
    uni_e = u'éèẽẻẹêếềễệể'
    uni_E = u'ÉÈẼẺẸÊẾỀỄỆỂ'
    uni_y = u'ýỳỷỹỵ'
    uni_Y = u'ÝỲỶỸỴ'
    uni_d = u'đ'
    uni_D = u'Đ'

    for c in string:
        for cc in ['a','o','i','u','e','d','y','A','O','I','U','E','D','Y']:
            exec("if c in uni_" + cc + ": c = " + "'" + cc + "'" )
        result += c
    return result
def convertHlToVietnamese(x):
    if x=='G':
        return u'Giỏi'
    elif x=='K':
        return u'Khá'
    elif x=='TB':
        return u'TB'
    elif x=='Y':
        return u'Yếu'
    elif x=='Kem':
        return u'Kém'
    else:
        return u'Chưa đủ điểm'
def convertCharToDigit(x):
    x=x.lower()
    if (x==u'đ') | (x=='d'):
        return '7'
    elif (x==u'cđ') | (x=='cd')  :
        return '4'
    elif x=="":
        return ""
    else:
        raise Exception('Error. Please contact with luulethe@gmail.com')
        
def convertHkToVietnamese(x):
    if x=='T':
        return u'Tốt'
    elif x=='K':
        return u'Khá'
    elif x=='TB':
        return u'TB'
    elif x=='Y':
        return u'Yếu'
    else:
        return u''    
def convertDanhHieu(x):
    if    x=='G' : return 'HSG'
    elif  x=='TT': return 'HSTT'
    else : return ''


# make username: example: input: AA, Nguyen Van, 2006 => output: AAnv_2006
#                         input: AA, Nguyen Van       => output: AAnv
def make_username( first_name = None, last_name = None,
                   full_name = None, start_year = None):
    if full_name:
        names = full_name.split(" ")
        last_name = ' '.join(names[:len(names)-1])
        first_name = names[len(names)-1]
    last_name = unicodedata.normalize('NFKD', unicode(last_name)).encode('ascii','ignore').lower()
    if first_name:
        first_name = unicodedata.normalize('NFKD', unicode(first_name)).encode('ascii','ignore').lower()
    username = first_name
    if last_name and last_name.strip() != '':
        for word in last_name.split(" "):
            if word: username += word[0]
    if start_year:
        username += str(start_year.time)
    username = re.compile(r'\W+').sub('', username)
    if len(username) > 28: username = username[:28]
    i = 0
    username1 = username
    while User.objects.filter( username__exact = username1):
        i += 1
        username1 = username + str(i)
    return username1

def make_default_password(words=2, digits=3):
    max_number = 10**digits
    raw_password = ''.join(random.sample(syllables, words))
    if digits > 0:
        raw_password += str(int(random.random()*max_number))
    return make_password(raw_password), raw_password

# student: Pupil object,
# old_class: Class object,
# new_class: Class object,
@transaction.commit_on_success
def move_student(school, student, new_class):
    old_class = student.current_class()
    if not new_class:
        return None
    if not old_class:
        _class = new_class
        subjects = _class.subject_set.all()
        year = school.year_set.latest('time')
        for subject in subjects:
            for i in range(1,3):
                term1 = year.term_set.get( number__exact = i)
                the_mark = Mark()
                the_mark.student_id = student
                the_mark.subject_id = subject
                the_mark.term_id = term1
                the_mark.save()

            tkmon = TKMon()
            tkmon.student_id = student
            tkmon.subject_id = subject
            tkmon.save()
        student.join_class(new_class)
        return student
    if old_class.block_id.number != new_class.block_id.number:
        if new_class.block_id.number - old_class.block_id.number != 1:
            raise Exception(u"chuyển học sinh tới khối không phù hợp")
        else:
            year = new_class.year_id
            last_year = old_class.year_id
            if student.tbnam_set.get(year_id = last_year).len_lop: # hs nay dc len lop
                return student.move_to_new_class(new_class)
            else:
                return student.move_to_new_class(new_class)
    else:
        if student.unc_class_id: return student.move_to_new_class(new_class)
        subjects = old_class.subject_set.all()
        for _subject in subjects:
            try:
                subject_in_new_class = new_class.subject_set.get( type__exact = _subject.type)
                marks = _subject.mark_set.filter( student_id__exact = student)
                for mark in marks:
                    mark.subject_id = subject_in_new_class
                    mark.save()
                tkmons = _subject.tkmon_set.filter( student_id__exact = student)
                for tkmon in tkmons:
                    tkmon.subject_id = subject_in_new_class
                    tkmon.save()

            except ObjectDoesNotExist as e:
                #there are no subject as same as subject in old class
                print e
                m_set = _subject.mark_set.filter( student_id__exact = student)
                for m in m_set:
                    m.current = False
                    m.save()
                tk_set = _subject.tkmon_set.filter( student_id__exact = student)
                for tk in tk_set:
                    tk.current = False
                    tk.save()

        subject_in_new_class = new_class.subject_set.all()
        for _subject in subject_in_new_class:
            marks = _subject.mark_set.filter( student_id__exact = student )
            if not marks:
                old_mark = student.mark_set.filter( subject_id__type = _subject.type)
                if not old_mark:
                    for i in range(1,3):
                        term1 = new_class.year_id.term_set.get( number__exact = i)
                        the_mark = Mark()
                        the_mark.student_id = student
                        the_mark.subject_id = _subject
                        the_mark.term_id = term1
                        the_mark.save()
                    tkmon = TKMon(student_id = student, subject_id = _subject)
                    tkmon.save()
                else:
                    for m in old_mark:
                        m.subject_id = _subject
                        m.current = True
                        m.save()
                    try:
                        tk = student.tkmon_set.get( subject_id__type = _subject.type)
                        tk.current = True
                        tk.subject_id = _subject
                        tk.save()
                    except ObjectDoesNotExist:
                        raise Exception('SubjectTypeWereNotFullyBuilt')

        student.join_class(new_class)
        return student


# This function will handle a change of students in a particular class
# where: students: is a list of dictionaries those have 'full_name','birthday','ban' keys
#                                                       'full_name':string, 'birthday': date, 'ban': string,
#                                                       'first_name', 'last_name', 'school_join_date'     
#        start_year: StartYear object, 'term': Term object
#        year: Year object    
#        _class : is a Class object
#        school : is a School object   
# TO DO: if student exists and _class is defferent from student's class:
#              . disassociated student's marks, "TBMon", "TKMon", 
#              . change the student's class into _class
#              . transfer the associated marks to the new corresponding mark table, "TBMon", "TKMon".  
#        if student exists and _class is the same with student's class:
#              . do nothing
#        if student does not exist:
#              . add the student to db  
#              . lets student belong to _class
#              . add: marks for each subject, "khenthuong", "kiluat", "diemdanh", "TKDiemDanh", "TBMon"
#                     "HanhKiem", "TKMon", "TBHocKy", "TBNam"

@transaction.commit_manually
def add_student( student = None, index = 0, start_year = None , year = None,
                 _class = None, term = None, school = None, school_join_date = None ):
    if not ( student and start_year and term and school ):
        raise Exception("Phải có giá trị cho các trường: Student,Start_Year,Term,School.")
    if 'fullname' in student:
        first_name, last_name = extract_fullname(student['fullname'])
    else:
        last_name = normalize(student['last_name'])
        first_name = normalize(student['first_name'])
    if not school_join_date:
        school_join_date = root_dt.date.today()
    birthday = student['birthday']
    if 'uu_tien' in student:
        uu_tien = student['uu_tien']
    else: uu_tien = ''
    if 'ban_dk' in student:
        ban = student['ban_dk']
    else: ban = None
    find = start_year.pupil_set.filter( first_name__exact = first_name)\
            .filter(last_name__exact = last_name)\
            .filter(birthday__exact = birthday)
    # count primary subjects
    print find, 'find'
    number_subject = 0
    if _class:
        number_subject = _class.subject_set.filter( primary=True).count()
    if find: # the student exists:
        transaction.commit()
        return False, find[0]
    else:    # the student does not exist
        try:
            st = Pupil()
            st.first_name = first_name
            st.last_name = last_name
            st.birthday = birthday
            st.ban_dk = ban
            st.school_join_date = school_join_date
            st.start_year_id = start_year
            st.class_id = _class
            st.index = index
            st.school_id = school
            st.uu_tien = uu_tien
            if 'dan_toc' in student: st.dan_toc = student['dan_toc']
            if 'birth_place' in student: st.birth_place = student['birth_place']
            if 'current_address' in student: st.current_address = student['current_address']
            if 'father_name' in student: st.father_name = student['father_name']
            if 'father_phone' in student: st.father_phone = student['father_phone']
            if 'mother_name' in student: st.mother_name = student['mother_name']
            if 'mother_phone' in student: st.mother_phone = student['mother_phone']
            if 'phone' in student: st.phone = student['phone']
            if 'sms_phone' in student: st.sms_phone = student['sms_phone']

            if 'sex' in student:
                st.sex = student['sex']
            else:
                st.sex = 'Nam'
            user = User()
            user.username = make_username( first_name=first_name,
                    last_name=last_name, start_year=start_year)
            user.password, raw_password = make_default_password()
            user.first_name = st.first_name
            user.last_name = st.last_name
            user.is_active = False
            user.save()
            userprofile = UserProfile()
            userprofile.user = user
            userprofile.organization = school
            userprofile.position = 'HOC_SINH'
            userprofile.save()
            st.user_id = user
            st.save()
            st.join_class(_class)

            _class.max += 1
            _class.save()

            for i in range(1,3):
                term1 = year.term_set.get( number__exact = i)

                tb_hoc_ky = TBHocKy()
                tb_hoc_ky.student_id = st
                tb_hoc_ky.number_subject = number_subject
                tb_hoc_ky.term_id = term1
                tb_hoc_ky.save()

                tk_diem_danh = TKDiemDanh()
                tk_diem_danh.student_id = st
                tk_diem_danh.term_id = term1
                tk_diem_danh.save()

            tb_nam = TBNam()
            tb_nam.student_id = st
            tb_nam.number_subject = number_subject
            tb_nam.year_id = year
            tb_nam.save()


            if _class:
                subjects = _class.subject_set.all()
                for i in range(1,3):
                    term1 = year.term_set.get( number__exact = i)
                    for subject in subjects:
                        the_mark = Mark()
                        the_mark.student_id = st
                        the_mark.subject_id = subject
                        the_mark.term_id = term1
                        the_mark.save()

                for subject in subjects:
                    tkmon = TKMon(student_id = st, subject_id = subject)
                    tkmon.save()
            transaction.commit()
            return True, st
        except Exception as e:
            print e
    #end for student in students

# adding students to database, return list of existing students.
#@transaction.commit_manually
def add_many_students( student_list = None,
                       start_year = None ,
                       year = None,
                       _class = None,
                       term = None,
                       school = None,
                       school_join_date = None,
                       force_update = False):
    if not ( student_list and start_year and term and school and _class ):
        raise Exception("Student,Start_Year,Term,School,CanNotBeNull")
    index = _class.max
    existing_student = []
    number_of_change = 0
    unc_st_found = False
    for student in student_list:
        index += 1
        if 'fullname' in student:
            first_name, last_name = extract_fullname(student['fullname'])
        else:
            last_name = normalize(student['last_name'])
            first_name = normalize(student['first_name'])

        if not school_join_date:
            school_join_date = root_dt.date.today()

        birthday = student['birthday']
        ban = student['ban_dk']
        find = start_year.pupil_set.filter(first_name__exact = first_name)\
                                   .filter(last_name__exact = last_name)\
                                   .filter(birthday__exact = birthday)
        cr_bl_found = False
        bl = _class.block_id
        unc_set = bl.uncategorizedclass_set.filter(year_id = year)
        for unc in unc_set:
            unc_st = unc.pupil_set.filter(first_name__exact = first_name)\
                                  .filter(last_name__exact = last_name)\
                                  .filter(birthday__exact = birthday)
            if unc_st:
                st = unc_st[0]
                unc_st_found = True
                cr_bl_found = True
                break
        if not cr_bl_found:
            try:
                bl = school.block_set.get(number = bl.number - 1)
                unc_set = bl.uncategorizedclass_set.filter(year_id = year)
                for unc in unc_set:
                    unc_st = unc.pupil_set.filter(first_name__exact = first_name)\
                                          .filter(last_name__exact = last_name)\
                                          .filter(birthday__exact = birthday)
                    if unc_st:
                        st = unc_st[0]
                        unc_st_found = True
                        break
            except ObjectDoesNotExist:
                pass

        # count primary subjects
        if find or unc_st_found: # the student exists:
            if force_update:
                st = find[0]
            elif not unc_st_found:
                existing_student.append(student)
                st = find[0]
                continue
        else:    # the student does not exist
            st = Pupil(first_name = first_name,
                       last_name = last_name,
                       birthday = birthday,
                       ban_dk = ban,
                       school_join_date = school_join_date,
                       start_year_id = start_year,
                       class_id = _class,
                       index = index,
                       school_id = school)
        changed = False
        if 'sex' in student:
            if st.sex != student['sex']:
                st.sex = student['sex']
                changed = True
        else:
            if st.sex != 'Nam':
                st.sex = 'Nam'
                changed = True
        if 'ban_dk' in student and st.ban_dk!= student['ban_dk']:
            st.ban_dk = student['ban_dk']
            changed = True
        if 'dan_toc' in student and st.dan_toc!= student['dan_toc']:
            st.dan_toc = student['dan_toc']
            changed = True
        if 'birth_place' in student and st.birth_place!=student['birth_place']:
            st.birth_place = student['birth_place']
            changed = True
        if 'current_address' in student and st.current_address!=student['current_address']:
            st.current_address = student['current_address']
            changed = True
        if 'father_name' in student and st.father_name!=student['father_name']:
            st.father_name = student['father_name']
            changed = True

        if 'father_phone' in student and st.father_phone !=student['father_phone']:
            st.father_phone = student['father_phone']
            changed = True

        if 'mother_name' in student and st.mother_name!=student['mother_name']:
            st.mother_name = student['mother_name']
            changed = True

        if 'mother_phone' in student and st.mother_phone!=student['mother_phone']:
            st.mother_phone = student['mother_phone']
            changed = True
        if 'sms_phone' in student and st.sms_phone!=student['sms_phone']:
            st.sms_phone = student['sms_phone']
            changed = True
        if force_update and st.current_class() != _class:
            move_student(school, st, _class)
            changed = True

        if not force_update and not unc_st_found:
            user = User()
            user.username = make_username(first_name = first_name,
                                          last_name = last_name,
                                          start_year = start_year)
            user.password, raw_password = make_default_password()
            user.first_name = st.first_name
            user.last_name = st.last_name
            user.is_active = False
            user.save()
            userprofile = UserProfile()
            userprofile.user = user
            userprofile.organization = school
            userprofile.position = 'HOC_SINH'
            userprofile.save()
            st.user_id = user
        if force_update and changed:
            st.save()
            number_of_change += 1
        elif not force_update:
            st.save()
            if st.unc_class_id:
                st.move_to_new_class(_class)
            else:
                st.join_class(_class)
        if not force_update:
            for i in range(1,3):
                term1 = year.term_set.get( number__exact = i)
                number_subject = 0
                if _class:
                    number_subject += _class.subject_set.filter(primary = 0).count()
                    number_subject += _class.subject_set.filter(primary = 3).count()
                    if i == 1:
                        number_subject = _class.subject_set.filter(primary=1).count()
                    if i == 2:
                        number_subject = _class.subject_set.filter(primary=2).count()

                TBHocKy.objects.get_or_create(student_id = st,
                                            number_subject = number_subject,
                                            term_id = term1)

                TKDiemDanh.objects.get_or_create(student_id = st,
                                                term_id = term1)

            number_subject = 0
            if _class:
                number_subject += _class.subject_set.filter(primary=0).count()
            TBNam.objects.get_or_create(student_id = st,
                                        number_subject = number_subject,
                                        year_id = year)

            if _class:
                subjects = _class.subject_set.all()
                for i in range(1,3):
                    term1 = year.term_set.get( number__exact = i)
                    for subject in subjects:
                        Mark.objects.get_or_create(student_id = st,
                                                    subject_id = subject,
                                                    term_id = term1)
                for subject in subjects:
                    TKMon.objects.get_or_create(student_id = st,
                                                subject_id = subject)
    _class.max = index
    _class.save()
    #transaction.commit()
    if force_update: return number_of_change
    return existing_student

# student: Pupil object
def del_student( student):
    student.disable = True
    student.save()

def completely_del_student( student):
    student.user_id.delete()


def add_teacher( first_name=None, last_name=None, full_name=None,
                 birthday=None, sms_phone='', sex='N', dan_toc='Kinh',
                 major='', current_address='', home_town='', birthplace='',
                 school=None, team_id=None, group_id=None, email='',
                 force_update=False):
    if full_name:
        first_name, last_name = extract_fullname(full_name)
    else:
        first_name = normalize(first_name)
        last_name = normalize(last_name)
    if team_id:
        if (type(team_id) == str or type(team_id) == unicode) and team_id.strip():
            name = team_id.strip()
            try:
                team_id = school.team_set.get(name=name)
            except Exception as e:
                print e
                team_id = Team()
                team_id.name = name
                team_id.school_id = school
                team_id.save()
        elif not isinstance(team_id, Team):
            team_id = None
    else:
        team_id = None
    if team_id:
        if group_id:
            if (type(group_id) == str
                    or type(group_id) == unicode) and group_id.strip():
                name = group_id
                try:
                    group_id = team_id.group_set.get( name = name)
                except Exception as e:
                    print e
                    group_id = Group()
                    group_id.name = name
                    group_id.team_id = team_id
                    group_id.save()
            elif isinstance(group_id, Group):
                if group_id.team_id != team_id:
                    raise Exception("GroupNotBelongToTeam")
            else:
                group_id = None
        else:
            group_id = None
    else:
        group_id = None

    if major.strip():
        if to_en(major) not in SUBJECT_LIST_ASCII:
            try:
                major = to_subject_name(major)
            except Exception:
                major = ''

    teacher = Teacher()
    teacher.first_name = first_name
    teacher.last_name = last_name
    teacher.school_id = school
    teacher.birthday = birthday
    find = school.teacher_set.filter( first_name__exact = first_name,
                                      last_name__exact = last_name,
                                      birthday__exact = birthday)
    if find :
        if force_update:
            teacher = find[0]
        else:
            return find
    teacher.sms_phone = sms_phone
    teacher.email = email
    teacher.home_town = home_town
    teacher.sex = sex
    teacher.dan_toc = dan_toc
    teacher.current_address = current_address
    teacher.birth_place = birthplace
    teacher.team_id = team_id
    teacher.group_id = group_id
    teacher.major = major

    if not force_update:
        user = User()
        user.username = make_username(first_name=first_name, last_name=last_name)
        user.password, raw_password = make_default_password()
        user.is_active = False
        user.first_name = teacher.first_name
        user.last_name = teacher.last_name
        user.save()
        userprofile = UserProfile()
        userprofile.user = user
        userprofile.organization = school
        userprofile.position = 'GIAO_VIEN'
        userprofile.save()
        teacher.user_id = user
    teacher.save()
    return teacher

def del_teacher( teacher):
    _class = teacher.current_homeroom_class()
    if _class:
        _class.teacher_id = None
        _class.save()
    teacher.user_id.delete()
# subject_name: string, teacher : Teacher object, _class : Class object
@transaction.commit_manually
def add_subject( subject_name = None, subject_type = '', hs = 1, teacher = None, _class = None, index = 0, nx= False, number_lesson = 0):
    find = _class.subject_set.filter( name__exact = subject_name)
    try:
        #noinspection PyUnusedLocal
        term = _class.year_id.term_set.get(number = _class.year_id.school_id.status)
    except Exception as e:
        print e
        raise Exception("TermDoesNotExist")
    if find:
        raise Exception("SubjectExist")
    else:
        subject = Subject()
        subject.name = subject_name
        subject.type = subject_type
        subject.hs = hs
        subject.teacher_id = teacher
        subject.class_id = _class
        subject.nx=nx
        subject.number_lesson = number_lesson
        subject.index = index
        subject.save()
        students = _class.pupil_set.all()
        for student in students:
            for i in range(1,3):
                t = _class.year_id.term_set.get(number = i)
                mark = Mark()
                mark.student_id = student
                mark.subject_id = subject
                mark.term_id = t
                mark.save()

            tkmon = TKMon()
            tkmon.student_id = student
            tkmon.subject_id = subject
            tkmon.save()

            # get TBHocKy
            school = _class.year_id.school_id
            current_term = _class.year_id.term_set.get( number = school.status )
            #print current_term
            try:
                tbhocky = student.tbhocky_set.get( term_id = current_term)
                #print tbhocky
                tbhocky.number_subject += 1
                tbhocky.save()
            except Exception as e:
                transaction.rollback()
                print e

            # get TBNam
            try:
                tbnam = student.tbnam_set.get( year_id = _class.year_id)
                #print tbnam
                tbnam.number_subject += 1
                tbnam.save()
            except Exception as e:
                transaction.rollback()
                print e
        transaction.commit()


def completely_del_subject( subject):
    if subject.type == u"Toán" or subject.type == u"Ngữ văn":
        raise Exception("Invalid request")
    _class = subject.class_id
    students = _class.pupil_set.all()
    if subject.primary < 3:
        for student in students:
            # get tbHocKy
            school = _class.year_id.school_id
            current_term = _class.year_id.term_set.get( number = school.status)
            try:
                tbhocky = student.tbhocky_set.get( term_id = current_term)
                tbhocky.number_subject -= 1
                if tbhocky.number_subject < 0: raise Exception("TBHocKy.number_subject<0")
                tbhocky.save()
            except Exception as e:
                print e

            # get TBNam
            try:
                tbnam = student.tbnam_set.get( year_id = _class.year_id)
                tbnam.number_subject -= 1
                if tbnam.number_subject < 0: raise Exception("TBNam.number_subject<0")
                tbnam.save()
            except Exception as e:
                print e
    subject.delete()

def delete_history(history):
    if history.history_check():
        mark = history.pupil.mark_set()
        for m in mark:
            if not m.current:
                if m.subject_id.class_id == history._class:
                    m.delete()
        history.delete()
    else:
        history.delete()

def get_school(request):
    if not request.user.is_authenticated():
        raise Exception('NotAuthenticated')
    if request.user.is_superuser: raise Exception('UserDoesNotHaveAnySchool')
    if request.user.userprofile.organization.level == 'S':
        school_id = request.session.get('school_id', 0)
        if school_id:
            school = Organization.objects.get(id = school_id)
        else:
            school = request.user.userprofile.organization
        return school
    if request.user.userprofile.organization.level != 'T':
        raise Exception('UserDoesNotHaveAnySchool')
    return request.user.userprofile.organization

def get_permission(request):
    if get_position(request) < 0:
        raise Exception('UserDoesNotHaveAnySchoolPosition')
    return request.user.userprofile.position
def get_lower_bound(school):
    if school.school_level == '1': return 1
    elif school.school_level == '2': return 6
    elif school.school_level == '3': return 10
    else: raise Exception('SchoolLevelIsNotProvided')
def get_upper_bound(school):
    if school.school_level == '1': return 6
    elif school.school_level == '2': return 10
    elif school.school_level == '3': return 13
    else: raise Exception('SchoolLevelIsNotProvided')
def get_level(request):
    return request.user.userprofile.organization.level
def get_position(request):
    try:
        if request.user.userprofile.organization.level == 'T':
            if request.user.userprofile.position == 'HOC_SINH':
                return 1
            elif request.user.userprofile.position == 'GIAO_VU':
                return 2
            elif request.user.userprofile.position == 'GIAO_VIEN':
                return 3
            elif request.user.userprofile.position == 'HIEU_PHO':
                return 4
            elif request.user.userprofile.position == 'HIEU_TRUONG':
                return 4
            else:
                return 0
        elif request.user.userprofile.organization.level == 'S':
            return 3
        else:
            return -1
    except Exception: return -1
def is_teacher(request):
    try:
        if request.user.userprofile.organization.level == 'T':
            if request.user.userprofile.position == 'GIAO_VIEN':
                return True
            else: return False
        else: return False
    except Exception: return False
def get_current_year(request):
    school = get_school(request)
    year = None
    try:
        year = school.year_set.latest('time')
    except ObjectDoesNotExist as e:
        print e
        pass
    return year

def get_latest_startyear(request):
    school = get_school(request)
    try:
        return school.startyear_set.latest('time')
    except Exception():
        return None


def get_startyear(request, time):
    school = get_school(request)

    try:
        return school.startyear_set.get(time = time)
    except Exception( 'StartYearDoesNotExist'):
        return None



def get_current_term(request):
    school = get_school(request)
    try:
        return school.year_set.latest('time').term_set.get(number = school.status)
    except Exception( 'TermDoesNotExist'):
        return None

def in_school(request,school_id):
    if request.user.userprofile.organization.level == 'T':
        try:
            school = get_school(request)
            if school == school_id:
                return True
            else:
                return False
        except Exception('UserDoesNotHaveAnySchool'):
            return False
    elif request.user.userprofile.organization.level == 'S':
        if request.user.userprofile.organization == school_id.upper_organization:
            request.session['school_id'] = school_id.id
            return True
        else:
            return False

def save_file(file):
    saved_file = open(os.path.join(settings.TEMP_FILE_LOCATION, 'sms_input.xls'), 'wb+')
    for chunk in file.chunks():
        saved_file.write(chunk)
    saved_file.close()
    return 'sms_input.xls'
#this function check whether the current user is the gvcn of the class with class_id or not
def gvcn(request, class_id):
    from school.models import Class
    if request.user.userprofile.position != 'GIAO_VIEN':
        return 0
    if isinstance(class_id, Class):
        cClass = class_id
    else:
        cClass = Class.objects.get(id=int(class_id))
    if cClass.teacher_id and (cClass.teacher_id.user_id == request.user):
        return 1
    return 0

#this function check whether the current user is the student of the class with class_id or not
def inClass(request, class_id):
    if request.user.userprofile.position != 'HOC_SINH':
        return 0
    st = request.user.pupil
    if st.class_id.id == int(class_id):
        return 1
    else:
        return 0
#this function return the student ID of the current user

def get_teacher(request):
    if request.user.userprofile.position != 'GIAO_VIEN':
        return None
    teacher = request.user.teacher
    return teacher

def get_student(request):
    if request.user.userprofile.position != 'HOC_SINH':
        return None
    pupil = request.user.pupil
    return pupil

def dd_convert(loai):
    if loai == u'P' or loai == u'p':
        return u'P'
    elif loai == u'K' or loai == u'k':
        return u'K'
    elif loai == u'M' or loai == u'm':
        return u'M'
    else:
        raise Exception(u'Không phải loại cho phép')


def get_profile_model():
    """
    Return the model class for the currently-active user profile
    model, as defined by the ``AUTH_PROFILE_MODULE`` setting. If that
    setting is missing, raise
    ``django.contrib.auth.models.SiteProfileNotAvailable``.

    """
    if (not hasattr(settings, 'AUTH_PROFILE_MODULE')) or \
           (not settings.AUTH_PROFILE_MODULE):
        raise SiteProfileNotAvailable
    profile_mod = get_model(*settings.AUTH_PROFILE_MODULE.split('.'))
    if profile_mod is None:
        raise SiteProfileNotAvailable
    return profile_mod


def get_profile_form():
    """
    Return a form class (a subclass of the default ``ModelForm``)
    suitable for creating/editing instances of the site-specific user
    profile model, as defined by the ``AUTH_PROFILE_MODULE``
    setting. If that setting is missing, raise
    ``django.contrib.auth.models.SiteProfileNotAvailable``.

    """
    profile_mod = get_profile_model()
    class _ProfileForm(forms.ModelForm):
        class Meta:
            model = profile_mod
            exclude = ('user',) # User will be filled in by the view.
    return _ProfileForm

def convert_diem_danh(loai):
    if loai == u'M':
        return u'đi học muộn'
    if loai == u'K':
        return u'Nghỉ học không phép'
    if loai == u'P':
        return u'Nghỉ học có phép'

def to_subject_name(name):
    name = name.lower()
    name = to_en(name)
    sub_toan = [u'Toán',u'toan',u'dai',u'hinh',u'dai so',u'hinh hoc',u'toan hoc']
    sub_van = [u'Ngữ văn',u'van', u'ngu van', u'v', u'nv']
    sub_ly = [u'Vật lí',u'vat ly', u'vat li', u'ly', u'li']
    sub_hoa = [u'Hóa học',u'hoa', u'hoa hoc']
    sub_sinh = [u'Sinh học',u'sinh', u'sinh hoc']
    sub_su = [u'Lịch sử',u'lich su', u'su']
    sub_dia = [u'Địa lí',u'dia', u'dia ly', u'dia li']
    sub_nn = [u'Ngoại ngữ',u'nn', u'ngoai ngu',u'anh',u'tieng anh']
    sub_nn2 = [u'NN2', u'nn2',u'ngoai ngu 2',u'phap',u'tieng phap',u'nhat',u'tieng nhat',
               u'nga',u'tieng nga',u'duc',u'tieng duc',u'trung',u'tieng trung']
    sub_gdcd = [u'GDCD',u'gdcd', u'cd', u'cong dan', u'giao duc cong dan']
    sub_cn = [u'Công nghệ',u'cn', u'cong nghe', u'c/nghe', u'cn']
    sub_td = [u'Thể dục',u'td', u'the duc']
    sub_nhac = [u'Âm nhạc',u'nhac', u'am nhac', u'an']
    sub_mt = [u'Mĩ thuật',u'my thuat', u'mt',u've']
    sub_tin = [u'Tin học',u'tin', u'tin hoc']
    sub_gdqp = [u'GDQP-AN',u'gdqp', u'gdqp-an', u'gdqpan', u'giao duc quoc phong',
                u'giao duc quoc phong an ninh', u'qs', u'qp', u'quan su',
                u'quoc phong']
    sub_list = [sub_toan,sub_van,sub_ly,sub_hoa,sub_sinh,sub_su,sub_dia,sub_nn,sub_gdcd,
                sub_gdqp,sub_cn,sub_td,sub_tin,sub_nhac,sub_mt,sub_nn2]
    for sub in sub_list:
        if name in sub:
            return sub[0]
    raise Exception(u'Can not recognize')

def normalize(name):
    return ' '.join([e.capitalize() for e in name.split(' ') if e])

def extract_fullname(name):
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
