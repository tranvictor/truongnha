#! /usr/bin/env python
#encoding:UTF-8
from django.core.urlresolvers import reverse
from base_tests import SchoolSetupTest, AddStudentTest
from school.models import DiemDanh
import simplejson
from school.models import Teacher, Team, Group
from datetime import date
# Loi test nho chu y: test ca get, post. Khi post thi nen test add subject ca
# nhung mon quan trong nhu: Toan, Van, kiem tra he so, kiem tra diem kem theo
# ung voi mon do cho tung hoc sinh trong lop
class AddSubjectTest(SchoolSetupTest):
    def phase8_get_subjects_of_class(self):
        classes = self.year.class_set.order_by('id')
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        #go to subjects per class
        res = self.client.get(reverse('subject_per_class', args=[cl.id]))
        print 'Going to check response status code'
        self.assertEqual(res.status_code, 200)
        print 'Going to check response content'
        context = res.context
        self.assertEqual(context['class'].id, cl.id)

    def phase9_add_a_subject(self):
        classes = self.year.class_set.order_by('id')
        #teachers = self.school.teacher_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]

        response = self.client.post(
            reverse('subject_per_class',args=[cl.id]),
                {
                'request_type': u'add',
                'name': u'Mĩ thuật test',
                'hs' : u'1',
                'teacher_id' : u'',
                'number_lesson': u'1',
                'nx' : u'on',
                'primary' : u'0',
                'type' : u'Mĩ thuật',
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['success'], True)
        self.assertEqual(cont['message'],u'Môn học mới đã được thêm.')

    def phase10_delete_a_subject(self):
        classes = self.year.class_set.order_by('id')
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        sub = cl.subject_set.get(name = u'Mĩ thuật test')
        response = self.client.post(
            reverse('subject_per_class',args=[cl.id]),
                {
                'request_type': u'xoa',
                'id' : sub.id,
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], u'Đã xóa thành công.')
    def phase12_delete_toan_or_nguvan(self):
        classes = self.year.class_set.order_by('id')
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        sub = cl.subject_set.get(type = u'Toán')
        response = self.client.post(
            reverse('subject_per_class',args=[cl.id]),
                {
                'request_type': u'xoa',
                'id' : sub.id,
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], u'Bad request.')
    def phase13_modify_subject(self):
        classes = self.year.class_set.order_by('id')
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        sub = cl.subject_set.get(type = u'Toán')
        print 'Update with negative heso'
        response = self.client.post(
            reverse('subject_per_class',args=[cl.id]),
                {
                'request_type': u'hs',
                'hs' : u'-1',
                'id' : sub.id,
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], u'Hệ số không được nhỏ hơn 0')

        print 'Update with valid heso'
        response = self.client.post(
            reverse('subject_per_class',args=[cl.id]),
                {
                'request_type': u'hs',
                'hs' : u'2',
                'id' : sub.id,
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], u'Cập nhật thành công.')
        
class DiemDanhTest(AddStudentTest):
    def diemdanh_a_student(self, cl, st, t, today):
        data=''
        data+= '-'.join([ str(st.id), t,
            str(today.day),
            str(today.month),
            str(today.year)]) + '%'
        res = self.client.post(reverse('dd',
            args=[cl.id, today.day, today.month, today.year]), {
                'data': data,
                'request_type': 'dd',
                }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        print 'Going to check response status'
        self.assertEqual(res.status_code, 200)
        print 'Going to check database'
        dd_list = DiemDanh.objects.filter(
                student_id=st,
                time=today)
        if t:
            self.assertEqual(len(dd_list), 1)
        else:
            self.assertEqual(len(dd_list), 0)
        for dd in dd_list:
            self.assertEqual(dd.loai, t)
        print 'Going to check update dd to %s' % t

    def phase12_add_diem_danh(self):
        cl = self.year.class_set.all()
        self.assertEqual(len(cl)>=1, True)
        cl = cl[0]
        today = date.today()
        res = self.client.get(reverse('dd',
            args=[cl.id, today.day, today.month, today.year]))
        print 'Going to check response status'
        self.assertEqual(res.status_code, 200)
        print 'Going to check response content'
        context = res.context
        print 'Going to check response context'
        self.assertEqual(context['class'].id, cl.id)
        self.assertEqual(context['date'], today)
        # done check get request
        sts = cl.students()
        types = ['K', 'P', '']
        for st in sts:
            for t in types:
                self.diemdanh_a_student(cl, st, t, today)    

class HanhKiemTest(AddStudentTest):
    def phase12_enter_hk_page(self):
        classes = self.year.class_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        #go to subjects per class
        res = self.client.get(reverse('hanh_kiem', args=[cl.id]))
        print 'Going to check response status'
        self.assertEqual(res.status_code, 200)
        print 'Going to check response context'
        self.assertEqual(res.context['class'].id,cl.id)

    def phase13_edit_current_term_hk(self):
        term = self.year.term_set.get(number = self.school.status)
        classes = self.year.class_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        student = cl.students()[0]
        request_type = 'term' + str(term.number)
        res = self.client.post(reverse('hanh_kiem',
            args=[cl.id]), {
            'request_type': request_type,
            'id': student.id,
            'val':u'T',
            }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        print 'Going to check response status'
        self.assertEqual(res.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(res['Content-Type'], 'json')
        cont = simplejson.loads(res.content)
        print 'Going to check response content'
        self.assertEqual(cont['success'],True)
        hk = student.tbnam_set.get(year_id__exact= self.year.id)
        print 'Going to check if hk is save'
        self.assertEqual(hk.term1,'T')
        res = self.client.post(reverse('hanh_kiem',
            args=[cl.id]), {
            'request_type': u'hk_thang_10',
            'id': student.id,
            'val':u'T',
            }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        print 'Going to check response status'
        self.assertEqual(res.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(res['Content-Type'], 'json')
        cont = simplejson.loads(res.content)
        print 'Going to check response content'
        self.assertEqual(cont['success'],True)
        hk = student.tbnam_set.get(year_id__exact= self.year.id)
        print 'Going to check if hk is save'
        self.assertEqual(hk.hk_thang_10,u'T')

class KhenThuongTest(AddStudentTest):
    def phase12_add_khenthuong(self):
        classes = self.year.class_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        self.assertGreater(len(cl.students()),0)
        student = cl.students()[0]
        num_kt = student.khenthuong_set.count()
        self.assertEqual(num_kt,0)
        res = self.client.post(reverse('add_khen_thuong',args=[student.id]),{
            'hinh_thuc':u'Khen trước lớp',
            'dia_diem':'',
            'noi_dung':'',
            'time': date.today().strftime("%d/%m/%Y")
        })
        print 'Going to check response status'
        self.assertEqual(res.status_code, 302)
        print 'Going to check response content type'
        self.assertEqual(res['Content-Type'],'text/html; charset=utf-8')
        print 'Going to check if kt is save'
        num_kt = student.khenthuong_set.count()
        self.assertEqual(num_kt,1)

    def phase13_edit_khenthuong(self):
        classes = self.year.class_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        self.assertGreater(len(cl.students()),0)
        student = cl.students()[0]
        kts = student.khenthuong_set.all()
        self.assertEqual(kts.count(),1)
        kt = kts[0]
        res = self.client.post(reverse('edit_khen_thuong',args=[kt.id]),{
            'hinh_thuc':u'Được khen thưởng đặc biệt',
            'dia_diem':u'HN',
            'noi_dung':'',
            'time': date.today().strftime("%d/%m/%Y")
        })
        print 'Going to check response status'
        self.assertEqual(res.status_code, 302)
        print 'Going to check response content type'
        self.assertEqual(res['Content-Type'],'text/html; charset=utf-8')
        print 'Going to check if kt is save'
        kt = student.khenthuong_set.all()[0]
        self.assertEqual(kt.dia_diem,u'HN')
        self.assertEqual(kt.hinh_thuc,u'Được khen thưởng đặc biệt')

    def phase14_delete_khenthuong(self):
        classes = self.year.class_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        self.assertGreater(len(cl.students()),0)
        student = cl.students()[0]
        kts = student.khenthuong_set.all()
        self.assertEqual(kts.count(),1)
        kt = kts[0]
        res = self.client.get(reverse('delete_khen_thuong',args=[kt.id]))
        print 'Going to check response status'
        self.assertEqual(res.status_code, 302)
        print 'Going to check response content type'
        self.assertEqual(res['Content-Type'],'text/html; charset=utf-8')
        print 'Going to check if kt is delete'
        num_kt = student.khenthuong_set.count()
        self.assertEqual(num_kt,0)

class KiLuatTest(AddStudentTest):
    def phase12_add_kiluat(self):
        classes = self.year.class_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        self.assertGreater(len(cl.students()),0)
        student = cl.students()[0]
        num_kl = student.kiluat_set.count()
        self.assertEqual(num_kl,0)
        res = self.client.post(reverse('add_ki_luat',args=[student.id]),{
            'hinh_thuc':u'Khiển trách trước hội đồng kỷ luật',
            'dia_diem':'',
            'noi_dung':'',
            'time': date.today().strftime("%d/%m/%Y")
        })
        print 'Going to check response status'
        self.assertEqual(res.status_code, 302)
        print 'Going to check response content type'
        self.assertEqual(res['Content-Type'],'text/html; charset=utf-8')
        print 'Going to check if kt is save'
        num_kl = student.kiluat_set.count()
        self.assertEqual(num_kl,1)
    def phase13_edit_kiluat(self):
        classes = self.year.class_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        self.assertGreater(len(cl.students()),0)
        student = cl.students()[0]
        kls = student.kiluat_set.all()
        self.assertEqual(kls.count(),1)
        kl = kls[0]
        res = self.client.post(reverse('edit_ki_luat',args=[kl.id]),{
            'hinh_thuc':u'Đình chỉ học',
            'dia_diem':u'TB',
            'noi_dung':'',
            'time': date.today().strftime("%d/%m/%Y")
        })
        print 'Going to check response status'
        self.assertEqual(res.status_code, 302)
        print 'Going to check response content type'
        self.assertEqual(res['Content-Type'],'text/html; charset=utf-8')
        print 'Going to check if kl is save'
        kl = student.kiluat_set.all()[0]
        self.assertEqual(kl.dia_diem,u'TB')
        self.assertEqual(kl.hinh_thuc,u'Đình chỉ học')

    def phase14_delete_kiluat(self):
        classes = self.year.class_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        self.assertGreater(len(cl.students()),0)
        student = cl.students()[0]
        kls = student.kiluat_set.all()
        self.assertEqual(kls.count(),1)
        kl = kls[0]
        res = self.client.get(reverse('delete_ki_luat',args=[kl.id]))
        print 'Going to check response status'
        self.assertEqual(res.status_code, 302)
        print 'Going to check response content type'
        self.assertEqual(res['Content-Type'],'text/html; charset=utf-8')
        print 'Going to check if kt is delete'
        num_kl = student.kiluat_set.count()
        self.assertEqual(num_kl,0)

class ImportStudentTest(SchoolSetupTest):
    def phase8_get_a_class(self):
        classes = self.year.class_set.all()
        self.assertEqual(len(classes)>0, True)
        self.cl = classes[0]
        res = self.client.get(reverse('class_detail', args=[self.cl.id]))
        self.assertEqual(res.status_code, 200)
    def phase9_import_5_students(self):
        with open('school/unittests/import_5_student.xls', 'rb') as input_file:
            res = self.client.post(
                    reverse('student_import', args=[self.cl.id,'import']),
                    {
                        'name': 'import file',
                        'files[]': [input_file]
                    })
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res['Content-Type'], 'json')
            content = simplejson.loads(res.content)
            content = content[0]
            self.assertEqual(content['number'], 5)
            self.assertEqual(content['number_ok'], 5)
            self.assertEqual(content['message'], u'Nhập dữ liệu thành công')
            self.assertEqual(content['student_confliction'], '')
    def phase10_import_5_duplicated_students(self):
        with open('school/unittests/import_5_student.xls', 'rb') as input_file:
            res = self.client.post(
                    reverse('student_import', args=[self.cl.id,'import']),
                    {
                        'name': 'import file',
                        'files[]': [input_file]
                    })
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res['Content-Type'], 'json')
            content = simplejson.loads(res.content)
            content = content[0]
            self.assertEqual(content['number'], 5)
            self.assertEqual(content['number_ok'], 0)
            existing_student = self.client.session['saving_import_student']
            self.assertEqual(len(existing_student), 5)
            res = self.client.post(
                    reverse('student_import', args=[self.cl.id, 'update']),
                    {},
                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res['Content-Type'], 'json')
            content = simplejson.loads(res.content)
            self.assertEqual(content['success'], True)
            self.assertEqual(content['message'], u'Thông tin không thay đổi')

class TimetableTest(SchoolSetupTest):
    def phase8_enter_class_timetable(self):
        classes = self.year.class_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        self.cl = cl
        #go to subjects per class
        res = self.client.get(reverse('timetable', args=[cl.id]))
        print 'Going to check response status'
        self.assertEqual(res.status_code, 200)
        print 'Going to check response context'
        self.assertEqual(res.context['class'].id,cl.id)
    def phase9_change_a_normal_lesson(self):
        response = self.client.post(
            reverse('timetable',args=[self.cl.id]),
                {
                'day': u'2',
                'sub' : u'',
                'request_type' : 'period_2',
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], u'Thời khóa biểu thay đổi thành công.')

    def phase10_change_a_special_lesson(self):
        response = self.client.post(
            reverse('timetable',args=[self.cl.id]),
                {
                'day': u'2',
                'sub' : u'-1',
                'request_type' : 'period_1',
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], u'Thời khóa biểu thay đổi thành công.')

    def phase11_change_an_invalid_day(self):
        response = self.client.post(
            reverse('timetable',args=[self.cl.id]),
                {
                'day': u'-2',
                'sub' : u'-1',
                'request_type' : 'period_1',
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], u'Có lỗi xảy ra.')

    def phase12_change_an_invalid_subject(self):
        response = self.client.post(
            reverse('timetable',args=[self.cl.id]),
                {
                'day': u'2',
                'sub' : u'-5',
                'request_type' : 'period_1',
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], u'Có lỗi xảy ra.')

    def phase13_change_an_invalid_period(self):
        response = self.client.post(
            reverse('timetable',args=[self.cl.id]),
                {
                'day': u'2',
                'sub' : u'-2',
                'request_type' : 'period_100',
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], u'Có lỗi xảy ra.')

class AddTeacherTest(SchoolSetupTest):
    def phase8_add_a_teacher(self):
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add',
                'first_name': u'Nguyễn Văn A',
                'birthday': u'20/3/1975',
                'sex': u'Nam',
                'sms_phone': u'0987438383',
                'major' : u'GDCD',
                'team_id' : u'',
                'group_id' : u'',

            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        print cont
        self.assertEqual(cont['success'], True)
        self.assertEqual(cont['message'],u'Bạn vừa thêm một giáo viên mới.')
        teacher = Teacher.objects.get(last_name=u'Nguyễn Văn',
            first_name=u'A',
            birthday=u'1975-03-20')
        print 'Check if teacher was created successfully'
        self.assertIsNotNone(teacher)
    def phase9_add_a_teacher_invalid_sex(self):
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add',
                'first_name': u'Nguyễn Văn B',
                'birthday': u'20/3/1975',
                'sex': u'Invalid',
                'sms_phone': u'0987438383',
                'major' : u'GDCD',
                'team_id' : u'',
                'group_id' : u'',

                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['success'], False)
        self.assertEqual(cont['message'],u'Có lỗi ở dữ liệu nhập vào.')

    def phase10_add_duplicate_teacher(self):
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add',
                'first_name': u'Nguyễn Văn A',
                'birthday': u'20/3/1975',
                'sex': u'Nam',
                'sms_phone': u'0987438383',
                'major' : u'GDCD',
                'team_id' : u'',
                'group_id' : u'',

                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['success'], False)
        self.assertEqual(cont['message'],u'Giáo viên này đã tồn tại trong hệ thống')
        return True

    def phase11_add_teacher_invalid_team(self):
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add',
                'first_name': u'Nguyễn Văn D',
                'birthday': u'2/3/1975',
                'sex': u'Nam',
                'sms_phone': u'0986438383',
                'major' : u'GDCD',
                'team_id' : u'111',
                'group_id' : u'',

                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['success'], False)
        self.assertEqual(cont['message'], u'Có lỗi ở dữ liệu nhập vào.')
        return True

    def phase11_add_teacher_invalid_team(self):
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add',
                'first_name': u'Nguyễn Văn D',
                'birthday': u'2/3/1975',
                'sex': u'Nam',
                'sms_phone': u'0986438383',
                'major' : u'GDCD',
                'team_id' : u'111',
                'group_id' : u'',

                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['success'], False)
        self.assertEqual(cont['message'], u'Có lỗi ở dữ liệu nhập vào.')
        return True

    def phase12_delete_teacher(self):
        teacher = Teacher.objects.get(last_name=u'Nguyễn Văn',
            first_name=u'A',
            birthday=u'1975-03-20')
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'del',
                'data' : str(teacher.id) + u'-',
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['success'], True)
        teacher = Teacher.objects.get(last_name=u'Nguyễn Văn',
            first_name=u'A',
            birthday=u'1975-03-20')
        self.assertIsNone(teacher)
        return True
    def phase13_add_a_team(self):
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add-team',
                'name': u'Tổ Toán',
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], 'OK')
        team = Team.objects.get(name__exact= u'Tổ Toán')
        self.assertIsNotNone(team)

    def phase14_add_a_duplicate_team(self):
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add-team',
                'name': u'Tổ Toán',
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], u'Tổ này đã tồn tại.')

    def phase15_add_a_group(self):
        team = Team.objects.all()[0]
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add-group',
                'name': u'Nhóm Đại số',
                'team_id': str(team.id),
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], 'OK')
        group = Group.objects.get(name__exact= u'Nhóm Đại số', team_id = team.id)
        self.assertIsNotNone(group)

    def phase16_add_a_duplicate_group(self):
        team = Team.objects.all()[0]
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add-group',
                'name': u'Nhóm Đại số',
                'team_id': str(team.id),
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], u'Nhóm này đã tồn tại.')

    def phase17_add_a_group_with_invalid_team(self):
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add-group',
                'name': u'Nhóm Đại số',
                'team_id': '10000',
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], u'Tổ này không tồn tại.')

    def phase18_rename_a_group_successfully(self):
        group = Group.objects.all()[0]
        name = group.name
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'rename-group',
                'name': u'Nhóm Đại số 2',
                'id': str(group.id),
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['success'], True)
        self.assertEqual(cont['message'], u'Đổi tên thành công.')

        old_group = Group.objects.get(id=group.id, name__exact = name)
        self.assertIsNone(old_group)

        new_group = Group.objects.get(id=group.id, name__exact = u'Nhóm Đại số 2')
        self.assertIsNotNone(new_group)

    def phase19_rename_a_group_with_too_long_name(self):
        group = Group.objects.all()[0]
        name = group.name
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'rename-group',
                'name': u'Nhóm Hình học của lớp chất lượng cao trường THPT',
                'id': str(group.id),
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['success'], False)
        self.assertEqual(cont['message'], u'Tên quá dài')

        new_group = Group.objects.get(id=group.id, name__exact = u'Nhóm Hình học của lớp chất lượng cao trường THPT')
        self.assertIsNone(new_group)

        old_group = Group.objects.get(id=group.id, name__exact = name)
        self.assertIsNotNone(old_group)

    def phase20_rename_a_group_with_an_exist_name(self):
        group = Group.objects.all()[0]
        name = group.name
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add-group',
                'name': u'Nhóm Hình học',
                'team_id': str(group.team_id),
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'rename-group',
                'name': u'Nhóm Hình học',
                'id': str(group.id),
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['success'], False)
        self.assertEqual(cont['message'], u'Tên nhóm này đã tồn tại.')

        old_group = Group.objects.get(id=group.id, name__exact = name)
        self.assertIsNotNone(old_group)

    def phase21_rename_a_team_successfully(self):
        team = Team.objects.all()[0]
        name = Team.name
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'rename-team',
                'name': u'Tổ Toán Mới',
                'id': str(team.id),
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['success'], True)
        self.assertEqual(cont['message'], u'Đổi tên thành công.')

        old_team = Team.objects.get(id=team.id, name__exact = name)
        self.assertIsNone(old_team)

        new_team = Team.objects.get(id=team.id, name__exact = u'Tổ Toán Mới')
        self.assertIsNotNone(new_team)


    def phase22_rename_a_team_with_an_exist_name(self):
        team = Team.objects.all()[0]
        name = team.name
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add-team',
                'name': u'Tổ văn',
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'rename-team',
                'name': u'Tổ văn',
                'id' : str(team.id),
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['success'], False)
        self.assertEqual(cont['message'], u'Tên tổ này đã tồn tại.')

        old_team = Team.objects.get(id=team.id, name__exact = name)
        self.assertIsNotNone(old_team)


    def phase23_delete_a_group(self):
        group = Group.objects.all()[0]
        group_id = group.id
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'delete_group',
                'id': str(group_id),
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        tmp = Teacher.objects.get(group_id = group_id)
        self.assertIsNone(tmp)

    def phase24_delete_a_team(self):
        team = Team.objects.all()[0]
        team_id = team.id
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'delete_team',
                'id': str(team_id),
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        tmp = Teacher.objects.get(team_id = team_id)
        self.assertIsNone(tmp)
