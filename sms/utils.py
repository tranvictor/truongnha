# -*- coding: utf-8 -*-
from models import sms
import settings
import os
import re
from django.core import mail

def to_ascii(string):
    result = ''
    uni_a = u'ăắẳẵặằâầấẩẫậàáảãạ'
    uni_A = u'ĂẮẲẴẶẰÂẦẤẨẪẬÀÁẢÃẠ'
    uni_o = u'óòỏõọơớờởỡợôốồỗộổ'
    uni_O = u'ÓÒỎÕỌƠỚỜỞỠỢÔỐỒỖỘỔ'
    uni_i = u'ìĩịỉí'
    uni_I = u'ÌĨỊỈÍ'
    uni_u = u'ủùũụúưừứựữử'
    uni_U = u'ỦÙŨỤÚƯỪỨỰỮỬ'
    uni_e = u'éèẽẻẹêếềễệể'
    uni_E = u'ÉÈẼẺẸÊẾỀỄỆỂ'
    uni_y = u'ýỳỷỹỵ'
    uni_Y = u'ÝỲỶỸỴ'
    uni_d = u'đ'
    uni_D = u'Đ'

    for c in string:
        for cc in ['a','o','i','u','e','d','y','A','O','I','U','E','D','Y']:
            exec("if c in uni_" + cc + ": c = " + "'" + cc + "'" )
        result += c
    return result

def _send_email(subject, message, from_addr=None, to_addr=[]):
    mail.send_mail(settings.EMAIL_SUBJECT_PREFIX + subject,
            message,
            settings.EMAIL_HOST_USER,
            to_addr)

def _send_sms(phone, content, user, save_to_db=True):
    phone = checkValidPhoneNumber(phone)
    school = None
    try:
        school = user.userprofile.organization
        if school.id in [42, 44]: raise Exception('NotAllowedSMS')
    except Exception:
        pass
    if phone:
        if school:
            content = to_ascii(u'Truong %s thong bao:\n %s' % (
                unicode(school), content))
        else:
            content = to_ascii(u'truongnha.com thong bao:\n %s' % content)
        s = None
        s = sms(phone=phone, content=content,
                sender=user, recent=True, success=False)
        s.save()
        s.send_sms(phone)

def send_email(subject, message, from_addr=None, to_addr=[]):
    #msg = MIMEText(message.encode('utf-8'), _charset='utf-8')
    #server = smtplib.SMTP('smtp.gmail.com',587) #port 465 or 587
    #server.ehlo()
    #server.starttls()
    #server.ehlo()
    #server.login(GMAIL_LOGIN,GMAIL_PASSWORD)
    #for to_address in to_addr:
    #    msg['Subject'] = subject
    #    msg['From'] = from_addr
    #    msg['To'] = to_address
    #    server.sendmail(from_addr, to_address, msg.as_string())
    #server.close()
    if not settings.DEBUG:
        return task_send_email.delay(subject, message,  from_addr, to_addr)
    else:
        _send_email(subject, message, from_addr, to_addr)

def sendSMS(phone, content, user, save_to_db=True):
    if not settings.DEBUG:
        task = task_send_sms.delay(phone, content, user, save_to_db)
        if task: return '1'
        else: return None
    else:
        return _send_sms(phone, content, user, save_to_db)

from celery import task

@task()
def task_send_email(subject, message, from_addr=None, to_addr=[]):
    mail.send_mail(settings.EMAIL_SUBJECT_PREFIX + subject,
                message,
                settings.EMAIL_HOST_USER,
                to_addr)

def task_send_sms(phone, content, user, save_to_db=True):
    return _send_sms(phone, content, user, save_to_db) 

@task()
def task_send_SMS_then_email(phone, content, user, save_to_db=True,
        subject=None, message=None, from_addr=None, to_addr=[]):
    smsed = False
    emailed = False
    try:
        smsed = _send_sms(phone, content, user, save_to_db) 
        if smsed == '1': smsed = True
    except Exception:
        try:
            _send_email(subject, message, from_addr, to_addr)                
            emailed = True
        except Exception:
            pass
    return smsed, emailed

def send_SMS_then_email(phone, content, user, save_to_db=True,
        subject=None, message=None, from_addr=None, to_addr=[]):
    if not settings.DEBUG:
        temp =  task_send_SMS_then_email.delay(
                    phone, content, user, save_to_db,
                    subject, message, from_addr, to_addr)
        return temp.get()
    else:
        try:
            smsed = sendSMS(phone, content, user, save_to_db)
        except Exception:
            smsed = None
        if smsed != '1':
            if to_addr and to_addr[0]:
                send_email(subject, message, from_addr, to_addr)
                return False, True
            else:
                return False, False
        else:
            return True, False

MOBI_HEAD = ['90', '93', '122', '126', '121', '128', '120']
VINA_HEAD = ['91', '94', '123', '125', '127', '129']
VIETTEL_HEAD = ['97', '98', '162', '163', '164', '165', '166', '167', '168', '169']
EVN_HEAD = ['96', '95']
VIETNAMMOBILE_HEAD = ['92', '188']
BEELINE_HEAD = ['199']
re_phone = re.compile('(84|\+84|0)(90|93|122|126|121|128|120|91|94|123|125|127|97|98|165|166|167|168|169|96|95|92|199)(\d{7})')
#this function check if phone number is valid or not
#return: True - valid, False - invalid
def regc(phone):
    return re_phone.match(phone)

def checkValidPhoneNumber(phone):
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

def save_file(file):
    saved_file = open(os.path.join(settings.TEMP_FILE_LOCATION,
        'sms_input.xls'),
        'wb+')
    for chunk in file.chunks():
        saved_file.write(chunk)
    saved_file.close()
    return 'sms_input.xls'
