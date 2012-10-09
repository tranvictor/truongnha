#! /usr/bin/env python
#encoding:UTF-8
from django.core.urlresolvers import reverse
from base_tests import SchoolSetupTest, AddStudentTest
from school.models import DiemDanh
import simplejson
from school.models import Teacher, Team, Group
from datetime import date

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
        self.assertEqual(cont['message'], u"Tổ này không tồn tại.")

    def phase12_add_teacher_invalid_team_n_group(self):
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
                'group_id' : u'111',

                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['success'], False)
        self.assertEqual(cont['message'], u"Tổ này không tồn tại.")


    def phase13_delete_teacher(self):
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
        teacher = None
        try:
            teacher = Teacher.objects.get(last_name=u'Nguyễn Văn',
                first_name=u'A',
                birthday=u'1975-03-20')
        except Exception:
            pass
        self.assertIsNone(teacher)

    def phase14_add_a_team(self):
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

    def phase15_add_a_duplicate_team(self):
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

    def phase16_add_a_group(self):
        team = Team.objects.all()[0]
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add-group',
                'name': u'Nhóm Đại số',
                'id': str(team.id),
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], 'OK')
        print 'Going to check object'
        group = Group.objects.get(name__exact= u'Nhóm Đại số', team_id = team.id)
        self.assertIsNotNone(group)

    def phase17_add_a_duplicate_group(self):
        team = Team.objects.all()[0]
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add-group',
                'name': u'Nhóm Đại số',
                'id': str(team.id),
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], u'Nhóm này đã tồn tại.')

    def phase18_add_a_group_with_invalid_team(self):
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add-group',
                'name': u'Nhóm Đại số',
                'id': '10000',
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['message'], u'Tổ này không tồn tại.')

    def phase19_rename_a_group_successfully(self):
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
        old_group = None
        try:
            old_group = Group.objects.get(id=group.id, name__exact = name)
        except Exception:
            pass
        self.assertIsNone(old_group)

        new_group = Group.objects.get(id=group.id, name__exact = u'Nhóm Đại số 2')
        self.assertIsNotNone(new_group)

    def phase20_rename_a_group_with_too_long_name(self):
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

        new_group = None
        try:
            new_group = Group.objects.get(id=group.id, name__exact = u'Nhóm Hình học của lớp chất lượng cao trường THPT')
        except Exception:
            pass
        self.assertIsNone(new_group)

        old_group = Group.objects.get(id=group.id, name__exact = name)
        self.assertIsNotNone(old_group)

    def phase21_rename_a_group_with_an_exist_name(self):
        group = Group.objects.all()[0]
        name = group.name
        response = self.client.post(
            reverse('teachers'),
                {
                'request_type':u'add-group',
                'name': u'Nhóm Hình học',
                'id': str(group.team_id.id),
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

    def phase22_rename_a_team_successfully(self):
        team = Team.objects.all()[0]
        name = team.name
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

        old_team = None
        try:
            old_team = Team.objects.get(id=team.id, name__exact = name)
        except Exception:
            pass
        self.assertIsNone(old_team)

        new_team = Team.objects.get(id=team.id, name__exact = u'Tổ Toán Mới')
        self.assertIsNotNone(new_team)


    def phase23_rename_a_team_with_an_exist_name(self):
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


    def phase24_delete_a_group(self):
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
        tmp = None
        try:
            tmp = Teacher.objects.get(group_id = group_id)
        except Exception:
            pass
        self.assertIsNone(tmp)

    def phase25_delete_a_team(self):
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
        tmp = None
        try:
            tmp = Teacher.objects.get(team_id = team_id)
        except Exception:
            pass
        self.assertIsNone(tmp)

class AddClassTest(SchoolSetupTest):
    def phase8_add_a_class(self):
        block = self.school.block_set.latest('id')
        class_name = str(block.number) + ' Test 1'
        num_of_class = self.school.get_current_year().class_set.count()
        response = self.client.post(
            reverse('add_class'),
            {
                'name':class_name,
                'phan_ban' : u'CB',
                'teacher_id': u'',
                }
        )
        self.assertEqual(response.status_code, 302)
        num_of_class_1 = self.school.get_current_year().class_set.count()
        self.assertEqual(num_of_class + 1, num_of_class_1)
        new_class = self.school.get_current_year().class_set.get(name = class_name)
        self.assertEqual(new_class.block_id,block)

    def phase9_prepare_data(self):
        block = self.school.block_set.latest('id')
        class_name_1 = str(block.number) + ' Test 2'
        class_name_2 = str(block.number) + ' Test 3'
        class_name_3 = str(block.number) + ' Test 4'
        response = self.client.post(
            reverse('add_class'),
            {
                'name':class_name_1,
                'phan_ban' : u'CB',
                'teacher_id': u'',
                }
        )
        response = self.client.post(
            reverse('add_class'),
            {
                'name':class_name_2,
                'phan_ban' : u'CB',
                'teacher_id': u'',
                }
        )
        response = self.client.post(
            reverse('add_class'),
            {
                'name':class_name_3,
                'phan_ban' : u'CB',
                'teacher_id': u'',
                }
        )

class AddSubjectTest2(AddClassTest):
    def phase10_add_a_subject(self):
        block = self.school.block_set.latest('id')
        class_name = str(block.number) + ' Test 3'
        cl = self.school.get_current_year().class_set.get(name = class_name)
        num_of_sub = cl.subject_set.count()

        response = self.client.post(
            reverse('subject_per_class',args=[cl.id]),
            {
                'request_type': u'add',
                'name': u'Mĩ thuật test',
                'hs' : u'1',
                'teacher_id' : u'',
                'number_lesson': u'1',
                'primary' : u'0',
                'type' : u'Mĩ thuật',
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'json')
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['success'], True)
        num_of_sub_1 = cl.subject_set.count()
        self.assertEqual(num_of_sub+1, num_of_sub_1)

    def phase11_delete_a_subject(self):
        block = self.school.block_set.latest('id')
        class_name = str(block.number) + ' Test 4'
        cl = self.school.get_current_year().class_set.get(name = class_name)
        num_of_sub = cl.subject_set.count()
        sub = cl.subject_set.get(name = u'Lịch sử')
        response = self.client.post(
            reverse('subject_per_class',args=[cl.id]),
            {
                'request_type': u'xoa',
                'id' : sub.id,
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'json')
        num_of_sub_1 = cl.subject_set.count()
        self.assertEqual(num_of_sub-1, num_of_sub_1)

class AddStudentTest2(AddSubjectTest2):
    def phase12_add_a_student(self):
        block = self.school.block_set.latest('id')
        class_name = str(block.number) + ' Test 1'
        cl = self.school.get_current_year().class_set.get(name = class_name)
        num_of_student = cl.number_of_pupils()
        response = self.client.post(
            reverse('class_detail',args=[cl.id]),
            {
                'request_type':u'add',
                'first_name': u'Nguyễn Thị',
                'last_name': u'Xuân',
                'birthday': u'22/10/1995',
                'sex': u'Nam',
                'birth_place': u'Ninh Bình',
                'current_address': u'Tam Điệp',
                'ban_dk': u'CB',
                'dan_toc':u'1',
                'quoc_tich': u'Việt Nam',
                'mother_name': u'Võ Thị Hương',
                'father_name': u'Nguyễn Văn An',
                'sms_phone': u'0987438383'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'json')
        cont = simplejson.loads(response.content)
        self.assertEqual(cont['success'], True)
        self.assertEqual(cont['message'],u'Bạn vừa thêm 1 học sinh')
        pupil = cl.students().get(first_name=u'Nguyễn Thị',
            last_name=u'Xuân',
            birthday=u'1995-10-22')
        self.assertEqual(pupil.current_class().id,cl.id)
        subject_num = cl.subject_set.count()
        marks_num = pupil.mark_set.count()
        self.assertEqual(marks_num,subject_num*2)
        tbhk_num = pupil.tbhocky_set.count()
        self.assertEqual(tbhk_num,2)
        tbnam_num = pupil.tbnam_set.count()
        self.assertEquals(tbnam_num,1)
        tkdh_num = pupil.tkdiemdanh_set.count()
        self.assertEqual(tkdh_num,2)
        tkmon_num = pupil.tkmon_set.count()
        self.assertEqual(tkmon_num, subject_num)
        num_of_student_1 = cl.number_of_pupils()
        self.assertEqual(num_of_student+1, num_of_student_1)

class MarkTest(AddStudentTest2):
    def phase13_add_mark(self):
        school = self.school
        current_term = school.year_set.latest('time').term_set.get(number = school.status)
        block = self.school.block_set.latest('id')
        class_name = str(block.number) + ' Test 1'
        cl = self.school.get_current_year().class_set.get(name = class_name)
        sub = cl.subject_set.get(name = u'Lịch sử')
        pupil = cl.students().get(first_name=u'Nguyễn Thị',
            last_name=u'Xuân',
            birthday=u'1995-10-22')
        mark = pupil.mark_set.get(subject_id = sub, term_id = current_term)
        data = u'1//0/false/%s:1*2*9*10*11*17*18*19*25*26:1*2*3*4*5*6*7*8*9' % mark.id
        response = self.client.post(
            reverse('save_mark'),
            {
                'data':data,
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        mark = pupil.mark_set.get(subject_id = sub, term_id = current_term)
        self.assertEqual(mark.diem,'1*2|3*4*5|6*7*8')
        self.assertEqual(mark.ck,9)

class MoveStudentTest1(MarkTest):
    def phase14_move_student_to_class_with_same_sub(self):
        school = self.school
        current_term = school.year_set.latest('time').term_set.get(number = school.status)
        block = self.school.block_set.latest('id')
        class_name = str(block.number) + ' Test 1'
        cl = self.school.get_current_year().class_set.get(name = class_name)
        pupil = cl.students().get(first_name=u'Nguyễn Thị',
            last_name=u'Xuân',
            birthday=u'1995-10-22')
        history_count = pupil.attend_set.count()
        num_of_std_1 = cl.students().count()
        move_class_name = str(block.number) + ' Test 2'
        move_cl = self.school.get_current_year().class_set.get(name = move_class_name)
        num_of_std_2 = move_cl.students().count()
        sub_cl_count = cl.subject_set.count()
        sub_mcl_count = move_cl.subject_set.count()
        self.assertEqual(sub_cl_count,sub_mcl_count)
        data = str(pupil.id) + '-'
        response = self.client.post(
            reverse('move_students'),
            {
                'target':move_cl.id,
                'data':data,
                'request_type':u'move'
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        num_of_std_3 = cl.students().count()
        num_of_std_4 = move_cl.students().count()
        self.assertEqual(num_of_std_1, num_of_std_3 + 1)
        self.assertEqual(num_of_std_2 + 1, num_of_std_4)
        history_count_2 = pupil.attend_set.count()
        self.assertEqual(history_count + 1, history_count_2)
        mark = pupil.mark_set.get(subject_id__name = u'Lịch sử',term_id = current_term.id)
        subject = move_cl.subject_set.get(name = u'Lịch sử')
        self.assertEqual(mark.current,True)
        self.assertEqual(mark.diem,'1*2|3*4*5|6*7*8')
        self.assertEqual(mark.ck, 9)
        self.assertEqual(mark.subject_id.id, subject.id)

    def phase15_edit_mark(self):
        school = self.school
        current_term = school.year_set.latest('time').term_set.get(number = school.status)
        block = self.school.block_set.latest('id')
        class_name = str(block.number) + ' Test 2'
        cl = self.school.get_current_year().class_set.get(name = class_name)
        sub = cl.subject_set.get(name = u'Lịch sử')
        pupil = cl.students().get(first_name=u'Nguyễn Thị',
            last_name=u'Xuân',
            birthday=u'1995-10-22')
        mark = pupil.mark_set.get(subject_id = sub, term_id = current_term)
        data = u'1//0/false/%s:1*2*9*10*11*17*18*19*25*26:1*2*3*9*5*6*7*8*6' % (mark.id)
        response = self.client.post(
            reverse('save_mark'),
            {
                'data':data,
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        mark = pupil.mark_set.get(subject_id = sub, term_id = current_term)
        self.assertEqual(mark.diem,'1*2|3*9*5|6*7*8')
        self.assertEqual(mark.ck,6)

    def phase16_move_student_back(self):
        school = self.school
        current_term = school.year_set.latest('time').term_set.get(number = school.status)
        block = self.school.block_set.latest('id')
        class_name = str(block.number) + ' Test 2'
        cl = self.school.get_current_year().class_set.get(name = class_name)
        pupil = cl.students().get(first_name=u'Nguyễn Thị',
            last_name=u'Xuân',
            birthday=u'1995-10-22')
        history_count = pupil.attend_set.count()
        num_of_std_1 = cl.students().count()
        class_name = str(block.number) + ' Test 1'
        move_cl = self.school.get_current_year().class_set.get(name = class_name)
        num_of_std_2 = move_cl.students().count()
        data = str(pupil.id) + '-'
        response = self.client.post(
            reverse('move_students'),
            {
                'target':move_cl.id,
                'data':data,
                'request_type':u'move'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        num_of_std_3 = cl.students().count()
        num_of_std_4 = move_cl.students().count()
        self.assertEqual(num_of_std_1,num_of_std_3+1)
        self.assertEqual(num_of_std_2+1,num_of_std_4)
        history_count_2 = pupil.attend_set.count()
        self.assertEqual(history_count+1,history_count_2)
        mark = pupil.mark_set.get(subject_id__name = u'Lịch sử',term_id = current_term)
        subject = move_cl.subject_set.get(name = u'Lịch sử')
        self.assertEqual(mark.current,True)
        self.assertEqual(mark.diem,'1*2|3*9*5|6*7*8')
        self.assertEqual(mark.ck,6)
        self.assertEqual(mark.subject_id,subject)

class MoveStudentTest2(MarkTest):
    def phase14_move_student_to_class_with_less_sub(self):
        school = self.school
        current_term = school.year_set.latest('time').term_set.get(number = school.status)
        block = self.school.block_set.latest('id')
        class_name = str(block.number) + ' Test 1'
        cl = self.school.get_current_year().class_set.get(name = class_name)
        pupil = cl.students().get(first_name=u'Nguyễn Thị',
            last_name=u'Xuân',
            birthday=u'1995-10-22')
        history_count = pupil.attend_set.count()
        num_of_std_1 = cl.students().count()
        class_name = str(block.number) + ' Test 4'
        move_cl = self.school.get_current_year().class_set.get(name = class_name)
        sub_cl_count = cl.subject_set.count()
        sub_mcl_count = move_cl.subject_set.count()
        self.assertGreater(sub_cl_count,sub_mcl_count)
        num_of_std_2 = move_cl.students().count()
        data = str(pupil.id) + '-'
        response = self.client.post(
            reverse('move_students'),
            {
                'target':move_cl.id,
                'data':data,
                'request_type':u'move'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        num_of_std_3 = cl.students().count()
        num_of_std_4 = move_cl.students().count()
        self.assertEqual(num_of_std_1,num_of_std_3+1)
        self.assertEqual(num_of_std_2+1,num_of_std_4)
        history_count_2 = pupil.attend_set.count()
        self.assertEqual(history_count+1,history_count_2)
        mark = pupil.mark_set.get(subject_id__name = u'Lịch sử',term_id = current_term)
        subject = cl.subject_set.get(name = u'Lịch sử')
        self.assertEqual(mark.current,False)
        self.assertEqual(mark.diem,'1*2|3*4*5|6*7*8')
        self.assertEqual(mark.ck,9)
        self.assertEqual(mark.subject_id,subject)

    def phase15_move_student_to_back(self):
        school = self.school
        current_term = school.year_set.latest('time').term_set.get(number = school.status)
        block = self.school.block_set.latest('id')
        class_name = str(block.number) + ' Test 4'
        cl = self.school.get_current_year().class_set.get(name = class_name)
        pupil = cl.students().get(first_name=u'Nguyễn Thị',
            last_name=u'Xuân',
            birthday=u'1995-10-22')
        history_count = pupil.attend_set.count()
        num_of_std_1 = cl.students().count()
        class_name = str(block.number) + ' Test 1'
        move_cl = self.school.get_current_year().class_set.get(name = class_name)
        num_of_std_2 = move_cl.students().count()
        data = str(pupil.id) + '-'
        response = self.client.post(
            reverse('move_students'),
            {
                'target':move_cl.id,
                'data':data,
                'request_type':u'move'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        num_of_std_3 = cl.students().count()
        num_of_std_4 = move_cl.students().count()
        self.assertEqual(num_of_std_1,num_of_std_3+1)
        self.assertEqual(num_of_std_2+1,num_of_std_4)
        history_count_2 = pupil.attend_set.count()
        self.assertEqual(history_count+1,history_count_2)
        mark = pupil.mark_set.get(subject_id__name = u'Lịch sử',term_id = current_term)
        subject = move_cl.subject_set.get(name = u'Lịch sử')
        self.assertEqual(mark.current,True)
        self.assertEqual(mark.diem,'1*2|3*4*5|6*7*8')
        self.assertEqual(mark.ck,9)
        self.assertEqual(mark.subject_id,subject)

class MoveStudentTest3(MarkTest):
    def phase14_move_student_to_class_with_more_sub(self):
        school = self.school
        current_term = school.year_set.latest('time').term_set.get(number = school.status)
        block = self.school.block_set.latest('id')
        class_name = str(block.number) + ' Test 1'
        cl = self.school.get_current_year().class_set.get(name = class_name)
        pupil = cl.students().get(first_name=u'Nguyễn Thị',
            last_name=u'Xuân',
            birthday=u'1995-10-22')
        history_count = pupil.attend_set.count()
        num_of_std_1 = cl.students().count()
        class_name = str(block.number) + ' Test 3'
        move_cl = self.school.get_current_year().class_set.get(name = class_name)
        sub_cl_count = cl.subject_set.count()
        sub_mcl_count = move_cl.subject_set.count()
        self.assertGreater(sub_mcl_count,sub_cl_count)
        num_of_std_2 = move_cl.students().count()
        data = str(pupil.id) + '-'
        num_of_mark = pupil.mark_set.count()
        response = self.client.post(
            reverse('move_students'),
            {
                'target':move_cl.id,
                'data':data,
                'request_type':u'move'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        num_of_std_3 = cl.students().count()
        num_of_std_4 = move_cl.students().count()
        self.assertEqual(num_of_std_1,num_of_std_3+1)
        self.assertEqual(num_of_std_2+1,num_of_std_4)
        history_count_2 = pupil.attend_set.count()
        self.assertEqual(history_count+1,history_count_2)
        num_of_mark_2 = pupil.mark_set.count()
        self.assertGreater(num_of_mark_2,num_of_mark)
        mark = pupil.mark_set.get(subject_id__name = u'Lịch sử',term_id = current_term)
        subject = move_cl.subject_set.get(name = u'Lịch sử')
        self.assertEqual(mark.current,True)
        self.assertEqual(mark.diem,'1*2|3*4*5|6*7*8')
        self.assertEqual(mark.ck,9)
        self.assertEqual(mark.subject_id,subject)
        mark = pupil.mark_set.get(subject_id__name = u'Mĩ thuật test',term_id = current_term)
        subject = move_cl.subject_set.get(name = u'Mĩ thuật test')
        self.assertEqual(mark.current,True)
        self.assertEqual(mark.subject_id,subject)

    def phase15_add_mark_to_new_sub(self):
        school = self.school
        current_term = school.year_set.latest('time').term_set.get(number = school.status)
        block = self.school.block_set.latest('id')
        class_name = str(block.number) + ' Test 3'
        cl = self.school.get_current_year().class_set.get(name = class_name)
        sub = cl.subject_set.get(name = u'Mĩ thuật test')
        pupil = cl.students().get(first_name=u'Nguyễn Thị',
            last_name=u'Xuân',
            birthday=u'1995-10-22')
        mark = pupil.mark_set.get(subject_id = sub, term_id = current_term)
        data = u'1//0/false/%s:1*2*9*10*11*17*18*19*25*26:1*2*3*9*8*6*7*8*9' % (mark.id)
        response = self.client.post(
            reverse('save_mark'),
            {
                'data':data,
                },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        mark = pupil.mark_set.get(subject_id = sub, term_id = current_term)
        self.assertEqual(mark.diem,'1*2|3*9*8|6*7*8')
        self.assertEqual(mark.ck,9)

    def phase16_move_student_back(self):
        school = self.school
        current_term = school.year_set.latest('time').term_set.get(number = school.status)
        block = self.school.block_set.latest('id')
        class_name = str(block.number) + ' Test 3'
        cl = self.school.get_current_year().class_set.get(name = class_name)
        pupil = cl.students().get(first_name=u'Nguyễn Thị',
            last_name=u'Xuân',
            birthday=u'1995-10-22')
        history_count = pupil.attend_set.count()
        num_of_std_1 = cl.students().count()
        class_name = str(block.number) + ' Test 1'
        move_cl = self.school.get_current_year().class_set.get(name = class_name)
        num_of_std_2 = move_cl.students().count()
        data = str(pupil.id) + '-'
        response = self.client.post(
            reverse('move_students'),
            {
                'target':move_cl.id,
                'data':data,
                'request_type':u'move'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        num_of_std_3 = cl.students().count()
        num_of_std_4 = move_cl.students().count()
        self.assertEqual(num_of_std_1,num_of_std_3+1)
        self.assertEqual(num_of_std_2+1,num_of_std_4)
        history_count_2 = pupil.attend_set.count()
        self.assertEqual(history_count+1,history_count_2)
        mark = pupil.mark_set.get(subject_id__name = u'Lịch sử',term_id = current_term)
        subject = move_cl.subject_set.get(name = u'Lịch sử')
        self.assertEqual(mark.current,True)
        self.assertEqual(mark.diem,'1*2|3*4*5|6*7*8')
        self.assertEqual(mark.ck,9)
        self.assertEqual(mark.subject_id,subject)
        mark = pupil.mark_set.get(subject_id__name = u'Mĩ thuật test',term_id = current_term)
        subject = cl.subject_set.get(name = u'Mĩ thuật test')
        self.assertEqual(mark.current,False)
        self.assertEqual(mark.subject_id,subject)
        self.assertEqual(mark.diem,'1*2|3*9*8|6*7*8')
        self.assertEqual(mark.ck,9)