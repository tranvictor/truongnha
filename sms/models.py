# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.conf import settings
from django.core import mail
from suds.client import Client
from celery.contrib.methods import task
from celery import Task


import xlrd
import os
import urllib
import re
import simplejson
import datetime


SMS_TYPES = (('TU DO', u'Tự do'), ('THONG_BAO', u'Thông báo'),)
#TEMP_FILE_LOCATION = os.path.join(os.path.dirname(__file__), 'uploaded')
def save_file(file):
    saved_file = open(os.path.join(settings.TEMP_FILE_LOCATION,
        'sms_input.xls'), 'wb+')
    for chunk in file.chunks():
        saved_file.write(chunk)
    saved_file.close()
    return 'sms_input.xls'

class customDateField(forms.DateField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('input_formats', ("%d.%m.%yY"))
        super(customDateField, self).__init__(*args, **kwargs)

MOBI_HEAD = ['90', '93', '122', '126', '121', '128', '120']
VINA_HEAD = ['91', '94', '123', '124', '125', '127', '129']
VIETTEL_HEAD = ['96', '97', '98', '162', '163', '164', '165', '166', '167', '168', '169']
EVN_HEAD = ['95']
VIETNAMMOBILE_HEAD = ['92', '188']
BEELINE_HEAD = ['199']
re_phone = re.compile('(84|\+84|0)(90|93|122|126|121|128|120|91|94|123|124|125|127|129\
        |97|98|162|163|164|165|166|167|168|169|96|95|92|199)(\d{7})$')
#this function check if phone number is valid or not
#return: True - valid, False - invalid
def regc(phone):
    return re_phone.match(phone)

def check_phone_number(phone):
    temp = regc(phone)
    if not temp: return None
    gr = temp.groups()
    if gr[0] == '0':
        return '%s%s' % ('84', ''.join(gr[1:]))
    else:
        return ''.join(gr)

def get_tsp(phone):
    temp = regc(phone)
    if not temp: return None
    head = temp.groups()[1]
    if head in VIETTEL_HEAD: return 'VIETTEL'
    if head in MOBI_HEAD: return 'MOBI'
    if head in VINA_HEAD: return 'VINA'
    if head in EVN_HEAD: return 'EVN'
    if head in VIETNAMMOBILE_HEAD: return 'VIETNAMMOBILE'
    if head in BEELINE_HEAD: return 'BEELINE'
    return None

REASON_DICT = {
        '500': u'Lỗi hệ thống',
        '21': u'Số điện thoại không hợp lệ',
        '25': u'Tài khoản trường bạn không đủ để thực hiện tin nhắn',
        '26': u'Lỗi ở cổng nhắn tin'
        }

# This task will recover sms when failure occurs
class SMSTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if self.max_retries == self.request.retries:
            sms = args[0]
            sms.recent = False
            sms.success = False
            sms.failed_reason = unicode(exc)
            sms.save()

class SMSEmailTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if self.max_retries == self.request.retries:
            sms = args[0]
            sms.recent = False
            sms.success = False
            sms.failed_reason = unicode(exc)
            sms.save()
            
            subject = kwargs['subject']
            message = kwargs['message']
            from_addr = kwargs['from_addr']
            to_addr = kwargs['to_addr']
            mail.send_mail(settings.EMAIL_SUBJECT_PREFIX + subject,
                    message,
                    from_addr,
                    to_addr)

class sms(models.Model):
    phone = models.CharField("Số điện thoại", max_length=20, blank=False)
    content = models.TextField("Nội dung")
    type = models.CharField("Loại tin nhắn", max_length=10,
            choices=SMS_TYPES, default='TU_DO')
    created = models.DateTimeField("Thời gian tạo")
    modified = models.DateTimeField("Thời gian sửa")
    sender = models.ForeignKey(User, related_name='sent_sms')
    receiver = models.ForeignKey(User, related_name='received_sms', null=True)
    #This field contains objects' ids those have to be updated after
    #sms sent successfully
    attachment = models.TextField("Liên quan", default='')
    recent = models.BooleanField(default=True)
    success = models.BooleanField(default=False)
    failed_reason = models.TextField("Lý do")
    
    class Meta:
        verbose_name_plural = "SMS"
        
    def createdFormat(self):
        return self.created.strftime('%d') + "/"\
                + self.created.strftime('%m') + " - "\
                + self.created.strftime('%H')+ ":"\
                + self.created.strftime('%M')

    def get_status(self):
        if self.recent:
            return u'Đang gửi'
        else:
            if self.success: return u'Đã gửi'
            else: return u'Thất bại'

    def get_failed_reason(self):
        if self.failed_reason in REASON_DICT:
            return REASON_DICT[self.failed_reason]
        else:
            return u'Lỗi hệ thống'

    def _send_iNET_sms(self):
        phone = self.phone
        if phone:
            data = urllib.urlencode({
                'mobile': phone,
                'brand': settings.INET_BRAND,
                'auth': settings.INET_AUTH,
                'message': self.content,
                'action': 'SEND',
                'content_type': '0'})
            return urllib.urlopen('http://brand.sms.vn/sendsms', data).read()
        else:
            raise Exception('InvalidPhoneNumber')

    def _send_Viettel_sms(self):
        phone = self.phone
        if phone:
            url = settings.SMS_WSDL_URL
            username = settings.WSDL_USERNAME
            password = settings.WSDL_PASSWORD
            mt_username = settings.MT_USERNAME
            mt_password = settings.MT_PASSWORD
            client = Client(url, username=username, password=password)
            message = \
    '''<?xml version="1.0" encoding="UTF-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
<soap12:Body>
<InsertMT xmlns="http://tempuri.org/">
  <User>%s</User>
  <Pass>%s</Pass>
  <CPCode>160</CPCode>
  <RequestID>4</RequestID>
  <UserID>%s</UserID>
  <ReceiveID>%s</ReceiveID>
  <ServiceID>8062</ServiceID>
  <CommandCode>CNHN1</CommandCode>
  <ContentType>0</ContentType>
<Info>%s</Info>
</InsertMT>
</soap12:Body>
</soap12:Envelope>''' % (mt_username, mt_password, phone, phone, self.content)
            return client.service.InsertMT(__inject= {'msg': str(message)})
        else:
            raise Exception("InvalidPhoneNumber")
        
    def _send_sms(self, school=None):
        if school and school.is_allowed_sms(): #school.id in [11, 10]:
            if self.sender.userprofile.is_allowed_sms():
                if get_tsp(self.phone) == 'VIETTEL':
                    result = self._send_Viettel_sms()
                else:
                    result = self._send_iNET_sms()
                if result == '1':
                    self.recent = False
                    self.success = True
                    self.save()
                    self.sender.userprofile.balance -=1 
                    self.sender.save()
                    return result
                else:
                    raise Exception('%s-SendFailed' % result)
            else:
                self.failed_reason = 'BalanceNotEnough'
                self.recent = False
                self.success = False
                self.save()
        else:
            #TODO: allow for teacher app, in this app
            # we don't have any school
            raise Exception('SMSNotAllowed')

    def _send_mark_sms(self, marks=None, dds=None, school=None):
        result = self._send_sms(school=school)
        if result == '1':
            #if not marks:
            #    attachs = simplejson.loads(self.attachment)
            #    ids = attachs['m']
            #    #marks = Mark.objects.filter(id__in=ids)
            for m in marks:
                m.update_sent()
            for dd in dds:
                dd.update_sent()
        else:
            attachs = {'m': [],'dd': []}
            for m in marks:
                attachs['m'].append(m.id)
            for dd in dds:
                attachs['dd'].append(dd.id)
            self.attachment = simplejson.dumps(attachs)
            self.save()

    @task(base=SMSTask, default_retry_delay=2, max_retries=3)
    def send_sms(self, *args, **kwargs):
        school = kwargs['school'] if 'school' in kwargs else None
        try:
            return self._send_sms(school=school)
        except Exception, e:
            raise self.send_sms.retry(exc=e)
        
    @task(base=SMSTask, default_retry_delay=2, max_retries=3)
    def send_mark_sms(self, *args, **kwargs): #marks=None, school=None):
        try:
            school = kwargs['school'] if 'school' in kwargs else None
            marks = kwargs['marks'] if 'marks' in kwargs else None
            dds = kwargs['dds'] if 'dds' in kwargs else None
            result = self._send_sms(school=school)
            if result == '1':
                #if not marks:
                #    attachs = simplejson.loads(self.attachment)
                #    ids = attachs['m']
                #    marks = Mark.objects.filter(id__in=ids)
                for m in marks:
                    m.update_sent()
                for dd in dds:
                    dd.update_sent()
            else:
                attachs = {'m': []}
                for m in marks:
                    attachs['m'].append(m.id)
                self.attachment = simplejson.dumps(attachs)
                self.save()
                return result
        except Exception, e:
            raise self.send_mark_sms.retry(exc=e)

    @task(base=SMSEmailTask, default_retry_delay=2, max_retries=3)
    def send_sms_then_email(self, *args, **kwargs):
        school = kwargs['school'] if 'school' in kwargs else None
        try:
            return self._send_sms(school=school)
        except Exception, e:
            raise self.send_sms_then_email.retry(exc=e)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.today()
        self.modified = datetime.datetime.today()
        super(sms, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.phone

CONTENT_TYPES = ['application/vnd.ms-excel']

class smsFromExcelForm(forms.Form):
    file  = forms.Field(label="Chọn file Excel:",
                        error_messages={
                            'required': 'Bạn chưa chọn file nào để tải lên.'},
                        widget=forms.FileInput())
    
    def clean_file(self):
        file = self.cleaned_data['file']
        save_file(file)            
        filepath = os.path.join(settings.TEMP_FILE_LOCATION, 'sms_input.xls')
        
        if not file.content_type in CONTENT_TYPES:
            os.remove(filepath)
            raise forms.ValidationError(
                    u'Bạn chỉ được phép tải lên file Excel.')
        elif not os.path.getsize(filepath):
            raise forms.ValidationError(
                    u'Hãy tải lên một file Excel đúng. File của bạn hiện đang trống.')
        elif not xlrd.open_workbook(filepath).sheet_by_index(0).nrows:
            raise forms.ValidationError(
                    u'Hãy tải lên một file Excel đúng. File của bạn hiện đang trống.')
        else:
            return file
