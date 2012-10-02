# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.conf import settings
from suds.client import Client
from celery.contrib.methods import task


import xlrd, os

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

    def _send_sms(self, phone):
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
            result = client.service.InsertMT(__inject= {'msg': str(message)})
            if result != '1':
                self.success = False
                self.recent = False
                self.save()
            else:
                self.success = True
                self.recent = False
            return result
        else:
            raise Exception("InvalidPhoneNumber")

    @task()
    def send_sms(self, phone):
        return self._send_sms(phone)

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
