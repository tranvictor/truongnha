# -*- coding: utf-8 -*-
from datetime import date
import re

from django.core.exceptions import ValidationError


LAST_NAME_MAX_LENGTH = 30
FIRST_NAME_MAX_LENGTH = 30
FULL_NAME_MAX_LENGTH = 60
HOME_TOWN_MAX_LENGTH = 250
SEX_MAX_LENGTH = 10
SMS_PHONE_MAX_LENGTH = 13 # because of region code: 84, +84
CURRENT_ADDRESS_MAX_LENGTH = 250
CLASS_NAME_MAX_LENGTH = 250
RECEIVABLES_NAME_MAX_LENGTH = 500
STATUS_MAX_LENGTH = 150
USERNAME_MAX_LENGTH = 150
PASSWORD_MAX_LENGTH = 150

def birthday(value):
    if value < date(1900, 1, 1) or value > date.today():
        raise ValidationError(u'Ngày nằm ngoài khoảng cho phép.')

MOBI_HEAD = ['90', '93', '122', '126', '121', '128', '120']
VINA_HEAD = ['91', '94', '123', '125', '127', '129']
VIETTEL_HEAD = ['97', '98', '162', '163', '164', '165', '166', '167', '168', '169']
EVN_HEAD = ['96', '95']
VIETNAMMOBILE_HEAD = ['92', '188']
BEELINE_HEAD = ['199']
re_phone = re.compile('(84|\+84|0)(90|93|122|126|121|128|120|91|94|123|125|127|129\
        |97|98|162|163|164|165|166|167|168|169|96|95|92|199)(\d{7})$')

def phone(value):
    if not re_phone.match(value):
        raise ValidationError(u'Số điện thoại không đúng')

def mark(value):
    if not 0 <= value <= 10:
        raise ValidationError(u'Điểm ngoài khoảng cho phép')

def hs(value):
    if 0 > value:
        raise ValidationError(u'Hệ số ngoài khoảng cho phép')

def amount(value):
    if 0 > value:
        raise ValidationError(u'Số tiền ngoài khoảng cho phép')

def deadline(value):
    if value < date.today():
        raise ValidationError(u'Hạn nộp ngoài khoảng cho phép')
