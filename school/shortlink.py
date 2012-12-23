from datetime import date
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from school.utils import get_current_term, get_current_class 

__author__ = 'ACDC'


def viewClassDetail(request):
    cl = get_current_class(request)
    return HttpResponseRedirect(reverse('class_detail', args=[cl.id]))

def diemdanh(request):
    cl = get_current_class(request)
    day = date.today()
    return HttpResponseRedirect(reverse('dd',args=[cl.id,day.day,day.month,day.year]))

def hanhkiem(request):
    cl = get_current_class(request)
    return HttpResponseRedirect(reverse('hanh_kiem',args=[cl.id]))

def subjectPerClass(request):
    cl = get_current_class(request)
    return HttpResponseRedirect(reverse('subject_per_class',args=[cl.id]))

def timeTable(request):
    cl = get_current_class(request)
    return HttpResponseRedirect(reverse('timetable',args=[cl.id]))

def xepLoaiHlTheoLop(request):
    cl = get_current_class(request)
    term = get_current_term(request)
    return HttpResponseRedirect(reverse('xep_loai_hl_theo_lop',args=[cl.id,term.id]))

def xlCaNamTheoLop(request):
    cl = get_current_class(request)
    return HttpResponseRedirect(reverse('xl_ca_nam_theo_lop',args=[cl.id,1]))

#def sendSMSResult(request):
#    cl = get_current_class(request)
#    return HttpResponseRedirect(reverse('send_sms_result',args=[cl.id]))
