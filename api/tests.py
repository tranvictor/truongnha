import cookielib
import simplejson
import urllib, urllib2
from django.utils import unittest

class LoginTestCase(unittest.TestCase):

    def setUp(self):
        pass
    def step_1(self):
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        #Login
        get_res = opener.open('http://localhost:8000/api/login/')
        print cj, 'cj'
        csrf = simplejson.loads(get_res.read())
        csrf = csrf['csrfmiddlewaretoken']
        print type(csrf), csrf, get_res.getcode()

        d = urllib.urlencode((('username', 'thunv'),
                              ('password', 'cruqha$531'),
                              ('csrfmiddlewaretoken', csrf)))
        req = opener.open('http://localhost:8000/api/login/', data=d)
        print cj
        logged_in = simplejson.loads(req.read())
        print logged_in, 'logged_in'

        student_list = opener.open('http://localhost:8000/api/getStudentList/631/')
        student_list = simplejson.loads(student_list.read())
        print student_list, 'student_list'
        print
        print
        print
        #diem_danh_data = urllib.urlencode({
        #    'classId': 25,
        #    'date': '23-04-2012',
        #    'list': '1315-P-20-04-2012%568-K-23-04-2012',
        #    'csrfmiddlewaretoken': csrf
        #})
        #print diem_danh_data, 'diem_danh_data'
        #diem_danh = opener.open('http://localhost:8000/api/attendance/', data=diem_danh_data)
        #print diem_danh.getcode(), 'diemdanh response code'
        print
        ds_dd = opener.open('http://localhost:8000/api/attendance/631/28/8/2012/')
        print ds_dd.read()
