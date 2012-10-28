#! /usr/bin/env python
#encoding:UTF-8
from django.middleware.csrf import get_token
from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from app.models import Register
from django.core import mail 
import random
import simplejson
import re
import sys, traceback
from cStringIO import StringIO

# This class will test the very first steps on a workflow
# 1. create a register
# 2. create a admin
# 3. create account for the register above
# 4. save username, password to self.user, self.password
# 5. delete the register above
from sms.utils import send_email

class BasicWorkFlow(TestCase):
    step_chain = []
    def setUp(self):
        #username, password for school's admin
        self.user = None
        self.password = None
        #register's fields
        self.name = 'test_user'
        self.email = 'testEmail@truongnha.com'
        self.email_pwd = 'truongnhadotcom'
        self.school_name = 'test_school'
        self.school_level = random.randint(2,3)
        self.province = '1'
        self.phone = ''
        self.address = 'test_address'
        self.client = Client()
        self.factory = RequestFactory()
        self.request = self.factory.get(reverse('register'))
        self.csrf = get_token(self.request)
        #some attributes for further tests
        self.school = None
        self.year = None
        self.sty = None #StartYear
        #create superuser
        self.hashed_pwd ='pbkdf2_sha256$10000$dmOhauthwSqI$s4RDmecWbR1y04/S0r+dH5SCBovz791MUXDSxsQ48Y4='
        self.admin_uname = 'admin'
        self.admin_pwd = '123456'
        User.objects.create(
                username=self.admin_uname,
                password=self.hashed_pwd,
                is_superuser=True)

    def _step1_register(self):
        res = self.client.post(reverse('register'), {
            'register_name': self.name,
            'register_email': self.email,
            'school_name': self.school_name,
            'school_level': self.school_level,
            'school_province': self.province,
            'register_phone': self.phone,
            'school_address': self.address,
            'csrfmiddlewaretoken': self.csrf},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        print 'Going to check response status'
        self.assertEqual(res.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(res['Content-Type'], 'json')
        print 'Going to check response content'
        content = simplejson.loads(res.content)
        self.assertEqual(content['success'], True)
        self.assertEqual(content['redirect'], reverse('login'))
        print 'OK, response correctly'
        print 'Going to check database for saved register'
        reg = Register.objects.filter(
                register_name=self.name,
                register_email=self.email)
        self.assertEqual(len(reg), 1)
        reg = reg[0]
        self.assertEqual(reg.status, 'CHUA_CAP')
        self.assertEqual(reg.register_name, self.name)
        self.assertEqual(reg.register_email, self.email)
        self.assertEqual(reg.school_name, self.school_name)
        self.assertEqual(reg.school_level, str(self.school_level))
        self.assertEqual(reg.school_province, self.province)
        self.assertEqual(reg.register_phone, self.phone)
        self.assertEqual(reg.school_address, self.address)
        print "OK, register's saved to database correctly"
        self.register_id = reg.id
        print 'Check email sent'
        print mail.outbox
        self.assertEqual(len(mail.outbox), 1)
        mail.outbox = []

    def _step2_login_as_admin(self):
        logged = self.client.login(
                username=self.admin_uname,
                password=self.admin_pwd)
        print 'Going to check user'
        self.assertEqual(logged, True)

    def _step3_create_account_for_register(self):
        res = self.client.post(reverse('manage_register'),{
            'request_type': 'create_acc',
            'data': str(self.register_id) + '-',
            'csrfmiddlewaretoken': self.csrf
            }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        print 'Going to check response status'
        self.assertEqual(res.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(res['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(res.content)
        self.assertEqual(cont['success'], True)
        acc_info = cont['account_info']
        acc_info = acc_info.split(',')[0].split('-')
        self.username = acc_info[1]
        self.password = acc_info[2]
        print 'Going to check sent email'
        self.assertEqual(len(mail.outbox), 1)

        self.client.logout()
        print 'Going to log in as registered account'
        logged = self.client.login(
                username=self.username,
                password=self.password)
        self.assertEqual(logged, True)

    def _step4_remove_register(self):
        print 'Going to log in as admin'
        logged = self.client.login(
                username=self.admin_uname,
                password=self.admin_pwd)
        self.assertEqual(logged, True)
        print 'Going to remove register'
        res = self.client.post(reverse('manage_register'),{
            'request_type': 'del',
            'data': str(self.register_id) + '-',
            'csrfmiddlewaretoken': self.csrf
            }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        print 'Going to check response status'
        self.assertEqual(res.status_code, 200)
        print 'Going to check response content type'
        self.assertEqual(res['Content-Type'], 'json')
        print 'Going to check response content'
        cont = simplejson.loads(res.content)
        self.assertEqual(cont['success'], True)
        print 'Going to check database'
        reg = Register.objects.filter(id=self.register_id)
        self.assertEqual(len(reg), 0)

    @classmethod
    def get_step_groups(cls):
        result = []
        steps = re.compile('_step(\d+)_(\w+)')
        names = []
        for name in dir(cls):
            if steps.match(name):
                names.append(name)
        current_id = None
        current_group = []
        for name in sorted(names,
                key=lambda key: int(steps.match(key).groups()[0])):
            groups = steps.match(name).groups()
            id = groups[0]
            if current_id != id:
                if current_group:
                    result.append(current_group)
                current_group = [name]
                current_id = id
            else:
                current_group.append(name)
        if current_group: result.append(current_group)

        phases = []
        steps = re.compile('phase(\d+)_(\w+)')
        for name in dir(cls):
            if steps.match(name):
                phases.append(name)
        current_id = None
        current_group = []
        for name in sorted(phases,
                key=lambda key: int(steps.match(key).groups()[0])):
            groups = steps.match(name).groups()
            id = groups[0]
            if current_id != id:
                if current_group:
                    result.append(current_group)
                current_group = [name]
                current_id = id
            else:
                current_group.append(name)
        if current_group: result.append(current_group)
        return result

    def _steps(self):
        steps = re.compile('(_step|phase|_teardown)(\d+)_(\w+)')
        for name in self.step_chain:
            if name:
                yield steps.match(name).groups()[2], getattr(self, name)

   # def tearDown(self):
   #     #dump the db via commandline
   #     fixt_name = [self.__class__.__name__]
   #     fixt_name.extend([a.__name__ for a in self.step_chain])
   #     fixt_name = ''.join(fixt_name)
   #     print fixt_name
   #     #TODO: make the path more flexible
   #     os.system('python manage.py sqlitedumpdata app school sms\
   #             > school/unittests/%s.json' % fixt_name)
        
    def test_run(self):
        number = 0
        old_stdout = sys.stdout
        try:
            for name, method in self._steps():
                number += 1
                sys.stdout.write('_')
                sys.stdout = self.stdout = StringIO()
                print "\nRUN STEP %d: %s" % (number, name)
                failed_scenario = method()
                sys.stdout = old_stdout
                if failed_scenario: break
        except Exception as e:
            sys.stdout = old_stdout
            sys.stdout.write(self.stdout.getvalue())
            traceback.print_exc(file=sys.stdout)
            self.fail("%s failed (%s: %s)" % (method, type(e), e))

class SendEmailTest(TestCase):
    def setUp(self):
        import string
        def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
            return ''.join(random.choice(chars) for x in range(size))
        self.ID = id_generator(size=12)
        self.subject = 'Test: SendEmail?ID=' + self.ID
        self.message = 'Test: Unittest for SendEmailTest'
        self.to_addr = 'testEmail@truongnha.com'
        self.client = Client()

    def test_sendEmail(self):
        send_email(subject= self.subject,
                message=self.message,
                to_addr=[self.to_addr])
        self.assertEqual(self.subject in mail.outbox[0].subject, True)

    def test_feedback_on_anonymous(self):
        content = 'This is feedback unittest'
        userName= 'UnitTest'
        userEmail= 'support@truongnha.com'
        href = 'unittest.truongnha.com/'
        response = self.client.post(
            reverse('feedback'),
            {
                'content': content,
                'username': userName,
                'userEmail': userEmail,
                'subject': self.subject,
                'feedback_url': href
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200) # server runs OK
        # now, check the email box if it receives the email correctly
        from time import sleep
        sleep(1) # sleep for 5s to ensure that receiver received the email, better solution?
        print 'Going to check sent email'
        self.assertEqual(self.subject in mail.outbox[0].subject, True)

