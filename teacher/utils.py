# -*- coding: utf-8 -*-
__author__ = 'Admin'
import datetime as root_dt
from datetime import datetime
from teacher.models import Student, Attend
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

def normalize(name):
    return ' '.join([e.capitalize() for e in name.split(' ') if e])

def add_many_students( student_list = None,
                       _class = None,
                       force_update = False):
    if not ( student_list and _class ):
        raise Exception("Student,Class,CanNotBeNull")
    existing_student = []
    number_of_change = 0
    for student in student_list:
        if 'fullname' in student:
            first_name, last_name = extract_fullname(student['fullname'])
        else:
            last_name = normalize(student['last_name'])
            first_name = normalize(student['first_name'])

        birthday = student['birthday']
        try:
            find = Attend.objects.filter(_class__teacher_id = _class.teacher_id, pupil__first_name__exact = first_name)\
            .filter(pupil__last_name__exact = last_name)\
            .filter(pupil__birthday__exact = birthday)

            # count primary subjects
            if find:
                st = find[0].pupil
                attendance = Attend.objects.filter(pupil__id=st.id, _class__id=_class.id, leave_time=None)
                #if already found a student then check for his attendance
                if not attendance:
                    Attend.objects.create(
                        pupil=st, _class=_class,
                        attend_time=datetime.now(),
                        leave_time=None)
                    continue

                if not force_update:
                    existing_student.append(student)
                    continue

            else:    # the student does not exist
                st = Student.objects.create(first_name=first_name,
                        last_name=last_name,
                        birthday=birthday)
                Attend.objects.create(
                    pupil=st, _class=_class,
                    attend_time=datetime.now(),
                    leave_time=None)
        except Exception as e:
            print e

        changed = False
        if 'sex' in student:
            if st.sex != student['sex']:
                st.sex = student['sex']
                changed = True
        else:
            if st.sex != 'Nam':
                st.sex = 'Nam'
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

        if force_update and changed:
            st.save()
            number_of_change += 1
        elif not force_update:
            st.save()
    #transaction.commit()
    if force_update: return number_of_change
    return existing_student
