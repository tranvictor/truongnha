#! /usr/bin/env python
#encoding:UTF-8
from django.core.urlresolvers import reverse
from base_tests import SchoolSetupTest,AddStudentTest
from school.models import Mark
import simplejson
from datetime import date

class MarkTest(AddStudentTest):
    def phase31_add_mark(self):
        print "helll"
        classes = self.year.class_set.all()
        for c in classes:
            if c.number_of_pupils() > 0:
                break
        s = c.subject_set.all()[0]
        mark_list = Mark.objects.filter(subject_id=s)
        for m in mark_list:
            data = '4//0/false/' + str(m.id) + ':1*2*9*10*11*17*18*19*25*26:1*2*3*4*5*6*7*8*9'
            response = self.client.post(
                reverse('save_mark'),
                    {
                    'request_type':u'sms',
                    'data':data,
                },
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')
        mark_list = Mark.objects.filter(subject_id=s)
        for m in mark_list:
            self.assertEqual(m.diem,'1*2|3*4*5|6*7*8')
            self.assertEqual(m.ck,9)

