#! /usr/bin/env python
#encoding:UTF-8
from django.core.urlresolvers import reverse
from app.tests import BasicWorkFlow
from app.models import Organization
import simplejson

# This class will test the very first steps on a workflow
# 1. create a register
# 2. create a admin
# 3. create account for the register above
# 4. save username, password to self.user, self.password
# 5. delete the register above
# 6. login as school admin
# 7. get school index, check if system redirects to setup page,
#    check forms that's displayed to user
# 8. save school's setting
# 9. save school's class list
# 10. setup new school
# 11. check classes, school's status, classes' subjects
from school.models import Pupil

class SchoolSetupTest(BasicWorkFlow):
    def phase1_login_as_school_admin(self):
        logged = self.client.login(
                    username=self.username,
                    password=self.password)
        self.assertEqual(logged, True)

    def phase2_test_redirect_to_setup_page(self):
        res = self.client.get(reverse('index'), follow=True)
        print 'Going to check redirect to Setup page'
        self.assertRedirects(res, reverse('setup'))
        print 'Going to check response content'
        form = res.context['form']
        self.assertEqual(form.data['name'], str(self.school_name))
        self.assertEqual(form.data['email'], str(self.email))
        self.assertEqual(form.data['school_level'], str(self.school_level))
        self.assertEqual(form.data['phone'], str(self.phone))
        self.assertEqual(form.data['address'], str(self.address))
        
    def phase3_save_school_setting(self):
        self.school_name = 'test_school_new'
        res = self.client.post(reverse('setup'),{
                'name': self.school_name,
                'school_level': self.school_level,
                'address': self.address,
                'phone': self.phone,
                'email': self.email,
                'update_school_detail': True
                }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        print 'Going to check response status'
        self.assertEqual(res.status_code, 200)
        print 'Going to check response type'
        self.assertEqual(res['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(res.content)
        self.assertEqual(cont['status'], 'done')
    
    def phase4_save_school_class_list_nhanh(self):
        self.school_cl_list = u'Nhanh: A, B,C, D, Toán 1, Toán 2'
        res = self.client.post(reverse('setup'),{
                'labels': self.school_cl_list,
                'update_class_name': True
                }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        print 'Going to check response status'
        self.assertEqual(res.status_code, 200)
        print 'Going to check response type'
        self.assertEqual(res['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(res.content)
        self.assertEqual(cont['status'], True)
        res_cls = cont['classes']
        res_grades = cont['grades']
        if self.school_level == 2:
            actual_grades = {6: '', 7: '', 8: '', 9: ''}
        else:
            actual_grades = {10: '', 11: '', 12: ''}
        res_grades = res_grades.split('-')
        for res_grade in res_grades:
            temp = actual_grades.pop(int(res_grade), None)
            self.assertEqual(temp, '')
        res_cls = res_cls.split('-')
        if self.school_level == 2:
            actual_grades = {6: '', 7: '', 8: '', 9: ''}
        else:
            actual_grades = {10: '', 11: '', 12: ''}
        actual_labels = ['A', 'B', 'C', 'D', u'Toán 1', u'Toán 2']
        for res_cl in res_cls:
            grade = res_cl.split(' ')[0]
            label = ' '.join(res_cl.split(' ')[1:])
            self.assertEqual(int(grade) in actual_grades, True)    
            self.assertEqual(label in actual_labels, True)

    def phase5_save_school_class_list(self):
        if self.school_level == 3:
            self.school_cl_list = u'10 A, 10 B, 10 C, 11 A, 11 B, 11 C,\
                    12 A, 12 B, 12 Toán 1'
        else:
            self.school_cl_list = u'9 A, 9 B, 9 C, 8 A, 8 B, 8 C, 7 A,\
                    7 B, 7 Toán 1, 6 A, 6 B, 6 Văn'
        res = self.client.post(reverse('setup'),{
                'labels': self.school_cl_list,
                'update_class_name': True
                }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        print 'Going to check response status'
        self.assertEqual(res.status_code, 200)
        print 'Going to check response type'
        self.assertEqual(res['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(res.content)
        self.assertEqual(cont['status'], True)
        res_cls = cont['classes']
        res_grades = cont['grades']
        if self.school_level == 2:
            actual_grades = {6: '', 7: '', 8: '', 9: ''}
        else:
            actual_grades = {10: '', 11: '', 12: ''}
        res_grades = res_grades.split('-')
        for res_grade in res_grades:
            temp = actual_grades.pop(int(res_grade), None)
            self.assertEqual(temp, '')
        res_cls = res_cls.split('-')
        if self.school_level == 2:
            actual_grades = {6: '', 7: '', 8: '', 9: ''}
        else:
            actual_grades = {10: '', 11: '', 12: ''}
        for res_cl in res_cls:
            self.assertEqual(res_cl in self.school_cl_list, True)    

    def phase6_setup_new_school(self):
        res = self.client.post(reverse('setup'),{
                'start_year': True
                }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        print 'Going to check response status'
        self.assertEqual(res.status_code, 200)
        print 'Going to check response type'
        self.assertEqual(res['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(res.content)
        self.assertEqual(cont['status'], 'done')
        res = self.client.get(reverse('start_year'))
        print 'Going to check response status'
        self.assertRedirects(res, reverse('classes'))

    def phase7_check_new_school(self):
        print 'Going to get school'
        school = Organization.objects.filter(
                name=self.school_name,
                school_level=self.school_level,
                status=1
                )
        self.assertEqual(len(school), 1)
        self.school = school[0]
        years = self.school.year_set.all()
        print 'This school should have a Year object'
        self.assertEqual(len(years), 1)
        stys = self.school.startyear_set.all()
        print 'This school should have a StartYear objects'
        self.assertEqual(len(stys), 1)
        year = years[0]
        self.year = year
        self.sty = stys[0]
        terms = year.term_set.all()
        actual_term = {1: '', 2: '', 3: ''}
        print 'This school should have 3 terms 1, 2, 3'
        for term in terms:
            self.assertEqual(actual_term.pop(term.number, None), '')

class AddStudentTest(SchoolSetupTest):
    def phase8_get_a_class(self):
        classes = self.year.class_set.all() 
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        res = self.client.get(reverse('class_detail', args=[cl.id]))
        print 'Going to check response status code'
        self.assertEqual(res.status_code, 200)

    def phase9_add_a_student(self):
        classes = self.year.class_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        response = self.client.post(
            reverse('class_detail',args=[cl.id]),
                {
                'request_type':u'add',
                'first_name': u'Nguyễn',
                'last_name': u'Xuân',
                'birthday': u'20/3/1995',
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
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        print cont
        self.assertEqual(cont['success'], True)
        self.assertEqual(cont['message'],u'Bạn vừa thêm 1 học sinh')
        pupil = Pupil.objects.get(first_name=u'Nguyễn',
                last_name=u'Xuân',
                birthday=u'1995-03-20')
        print 'Check if student in the right class'
        self.assertEqual(pupil.current_class().id,cl.id)
        subject_num = cl.subject_set.count()
        marks_num = pupil.mark_set.count()
        print 'Check if student have enough mark table'
        self.assertEqual(marks_num,subject_num*2)
        tbhk_num = pupil.tbhocky_set.count()
        print 'Check if student have enough TBHocky'
        self.assertEqual(tbhk_num,2)
        tbnam_num = pupil.tbnam_set.count()
        print 'Check if student have enough TBNam'
        self.assertEquals(tbnam_num,1)
        tkdh_num = pupil.tkdiemdanh_set.count()
        print 'Check if student have enough TKDiemDanh'
        self.assertEqual(tkdh_num,2)
        tkmon_num = pupil.tkmon_set.count()
        print 'Check if student have enough TKMon'
        self.assertEqual(tkmon_num, subject_num)

    def phase10_empty_node(self):
        pass

    def phase10_add_a_student_fail_sex(self):
        classes = self.year.class_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        response = self.client.post(
            reverse('class_detail',args=[cl.id]),
                {
                'request_type':u'add',
                'first_name': u'Nguyễn',
                'last_name': u'Xuân',
                'birthday': u'20/20/1995',
                'sex': u'12903',
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
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(len(cont),1)
        return True

    def phase10_add_a_student_fail_birthday(self):
        classes = self.year.class_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        response = self.client.post(
            reverse('class_detail',args=[cl.id]),
                {
                'request_type':u'add',
                'first_name': u'Nguyễn',
                'last_name': u'Xuân',
                'birthday': u'20/20/1995',
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
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(len(cont),1)
        return True

    def phase10_add_a_student_duplicate_in_same_class(self):
        classes = self.year.class_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        response = self.client.post(
            reverse('class_detail',args=[cl.id]),
                {
                'request_type':u'add',
                'first_name': u'Nguyễn',
                'last_name': u'Xuân',
                'birthday': u'20/3/1995',
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
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(len(cont),1)
        return True

    def phase10_add_a_student_duplicate_in_other_class(self):
        classes = self.year.class_set.all()
        # get a class
        self.assertEqual(len(classes)>0, True)
        cl = classes[0]
        other = None
        # find another class in the same grade
        for other in cl.block_id.class_set.all():
            if other.id != cl.id:
                cl = other
                break
        self.assertEqual(other!=None, True)
        self.assertEqual(other.block_id, cl.block_id)
        response = self.client.post(
            reverse('class_detail',args=[other.id]),
                {
                'request_type':u'add',
                'first_name': u'Nguyễn',
                'last_name': u'Xuân',
                'birthday': u'20/3/1995',
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
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(response.content)
        self.assertEqual(len(cont),1)
        return True

