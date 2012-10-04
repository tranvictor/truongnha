# -*- coding: utf-8 -*-
from models import sms, check_phone_number, get_tsp
import settings
import os
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

# school parameter here is for hitting db avoidance purpose
def _send_sms(phone, content, user, save_to_db=True, school=None):
    phone = check_phone_number(phone)
    try:
        if not school:
            school = user.userprofile.organization
        if school.id in [42, 44]: raise Exception('NotAllowedSMS')
    except Exception:
        pass
    if phone:
        if school:
            content = to_ascii(u'Truong %s thong bao:\n%s' % (
                unicode(school), content))
        else:
            content = to_ascii(u'Truongnha.com thong bao:\n%s' % content)
        s = None
        s = sms(phone=phone, content=content,
                sender=user, recent=True, success=False)
        s.save()
        if not settings.DEBUG:
            return s.send_sms.delay(s, phone)
        else:
            return s._send_sms(phone)

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

def sendSMS(phone, content, user, save_to_db=True, school=None):
    if not settings.DEBUG:
        task = _send_sms(phone, content, user, save_to_db, school)
        if task: return '1'
        else: return None
    else:
        return _send_sms(phone, content, user, save_to_db, school)

from celery import task

@task()
def task_send_email(subject, message, from_addr=None, to_addr=[]):
    mail.send_mail(settings.EMAIL_SUBJECT_PREFIX + subject,
                message,
                settings.EMAIL_HOST_USER,
                to_addr)

@task()
def task_send_SMS_then_email(phone, content, user, save_to_db=True, school=None,
        subject=None, message=None, from_addr=None, to_addr=[]):
    smsed = False
    emailed = False
    try:
        smsed = _send_sms(phone, content, user, save_to_db) 
        if smsed: smsed = True
    except Exception:
        try:
            _send_email(subject, message, from_addr, to_addr)                
            emailed = True
        except Exception as e:
            print e
            pass
    return smsed, emailed

def send_SMS_then_email(phone, content, user, save_to_db=True, school=None,
        subject=None, message=None, from_addr=None, to_addr=[]):
    if not settings.DEBUG:
        temp = task_send_SMS_then_email.delay(
                phone, content, user, save_to_db, school,
                subject, message, from_addr, to_addr)
        return temp.get()
    else:
        try:
            smsed = sendSMS(phone, content, user, save_to_db, school)
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

def save_file(file):
    saved_file = open(os.path.join(settings.TEMP_FILE_LOCATION,
        'sms_input.xls'),
        'wb+')
    for chunk in file.chunks():
        saved_file.write(chunk)
    saved_file.close()
    return 'sms_input.xls'
