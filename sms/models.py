# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.conf import settings
from suds.client import Client
from celery.contrib.methods import task


import xlrd
import os
import urllib
import re

#TEMP_FILE_LOCATION = os.path.join(os.path.dirname(__file__), 'uploaded')
def save_file(file):
    saved_file = open(os.path.join(settings.TEMP_FILE_LOCATION,
        'sms_input.xls'),
        'wb+')
    for chunk in file.chunks():
        saved_file.write(chunk)
    saved_file.close()
    return 'sms_input.xls'

class customDateField(forms.DateField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('input_formats', ("%d.%m.%yY"))
        super(customDateField, self).__init__(*args, **kwargs)

MOBI_HEAD = ['90', '93', '122', '126', '121', '128', '120']
VINA_HEAD = ['91', '94', '123', '125', '127', '129']
VIETTEL_HEAD = ['97', '98', '162', '163', '164', '165', '166', '167', '168', '169']
EVN_HEAD = ['96', '95']
VIETNAMMOBILE_HEAD = ['92', '188']
BEELINE_HEAD = ['199']
re_phone = re.compile('(84|\+84|0)(90|93|122|126|121|128|120|91|94|123|125|127|129\
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

class sms(models.Model):
    phone = models.CharField("Số điện thoại", max_length=20, blank=False)
    content = models.TextField("Nội dung")
    created = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    sender = models.ForeignKey(User)
    receiver = models.CharField("Người nhận", max_length=64, blank=False)
    recent = models.BooleanField(default=True)
    success = models.BooleanField(default=False)
    
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
        
    def _send_sms(self):
        phone = self.phone
        tsp = get_tsp(phone)
        try:
            # 2 id user nay de cap phep nhan tin cho chi Van va account sensive
            if tsp != 'VIETTEL' and int(self.sender_id) in [904, 16742]:
                result = self._send_iNET_sms()
            else:
                result = self._send_Viettel_sms()
            if result != '1':
                self.success = False
                self.recent = False
                self.save()
            else:
                self.success = True
                self.recent = False
                self.save()
            return result
        except Exception:
            self.recent= False
            self.success = False
            self.save()
        
    def _send_mark_sms(self, marks):
        result = self._send_sms()
        if result == '1':
            for m in marks:
                m.update_sent()

    @task()
    def send_sms(self, phone):
        return self._send_sms()
        
    @task()
    def send_mark_sms(self, marks):
        result = self._send_sms()
        if result == '1':
            for m in marks:
                m.update_sent()

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
