# -*- coding: utf-8 -*-

from django import template
from school.templateExcel import MAX_COL
register = template.Library()


@register.filter
def convertHlToVietnamese(x):
    if x=='G':
        return u'Giỏi'
    elif x=='K':
        return u'Khá'
    elif x=='TB':
        return u'TB'
    elif x=='Y':
        return u'Yếu'
    elif x=='Kem':
        return u'Kém'
    else:
        return u''    
@register.filter
def convertMarkToCharacter(x):
    if x>=5:
        return u'Đ'
    else:
        return  u'CĐ'
@register.filter
def convertHKToVietnamese(x):
    if x=='T':
        return u'Tốt' 
    elif x=='K':
        return u'Khá'
    elif x=='TB':
        return u'TB'
    elif x=='Y':
        return u'Yếu'
    else:
        return u''    
@register.filter
def convertDHToVietnamese(x):
    if x=='G':
        return u'HSG' 
    elif x=='TT':
        return u'HSTT'
    else:
        return u''

@register.filter
def filterNote(content,userId):
    contentList = content.split("/")
    for c in contentList:
        cs = c.split("##")
        if (cs[0]==str(userId)):
            return cs[1]
    return ""

@register.filter
def getMark(markStr,x):
    return "chao"

@register.filter
def toNumber(x,y):
    return int(x)*MAX_COL + int(y)

@register.filter
def toPercent(x,y):
    if y == 0:
        return str(0.00)
    else:
        return round(float(x)*100.0/float(y),2)

@register.filter
def plus(x,y):
    return int(x)+int(y)