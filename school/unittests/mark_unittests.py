#! /usr/bin/env python
#encoding:UTF-8
from django.core.urlresolvers import reverse
from base_tests import SchoolSetupTest,AddStudentTest
from school.models import *
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
        m = Mark.objects.get(subject_id=s, term_id__number=1)
        print m
        #print "ok1"
        data = '4//0/false/' + str(m.id) + ':1*2*:2*1.9*'
        response = self.client.post(
            reverse('save_mark'),
                {
                'request_type':u'sms',
                'data':data,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        #m1 = Mark.objects.get(subject_id=s, term_id__number=1)
        #print m1.diem
        #print m1.toArrayMark()
        self.assertEqual(response.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(response['Content-Type'], 'json')

