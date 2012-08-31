# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.files import File
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.views.generic.list import ListView
from models import sms, smsFromExcelForm
from utils import *

import os
import urllib
import urllib2
import xlrd
import xlwt

#TEMP_FILE_LOCATION = os.path.join(os.path.dirname(__file__), 'uploaded')
#MANUAL_SMS = os.path.join('sms', 'manual_sms.html')
#
#def manual_sms(request):
#    try:
#        school = get_school(request)
#        user = request.user
#    except Exception as e:
#        return HttpResponseRedirect( reverse('index'))
#    permission = get_permission(request)
#    if not permission in [u'HIEU_TRUONG',u'HIEU_PHO', u'GIAO_VIEN']:
#        return HttpResponseRedirect(reverse('school_index'))
#    teachers = User.objects.filter(userprofile__organization = school,
#                                   userprofile__position__in = ['GIAO_VIEN', 'HIEU_PHO', 'HIEU_TRUONG'] )
#    students = User.objects.filter(userprofile__organization = school,
#                                   userprofile__position = 'HOC_SINH' )
#    context = RequestContext(request)
#    return render_to_response(MANUAL_SMS, {'teachers':teachers,
#                                    'students':students,
#                                    'user': user},
#                       context_instance = context)
#
#def excel_sms(request):
#    if request.method == 'POST':
#        if 'upload' in request.POST:
#            form = smsFromExcelForm(request.POST, request.FILES)
#            if form.is_valid():
#                form.clean_file()
#                filepath = os.path.join(TEMP_FILE_LOCATION, 'sms_input.xls')
#                list = xlrd.open_workbook(filepath)
#                sheet = list.sheet_by_index(0)
#                data = []
#                for r in range(1, sheet.nrows):
#                    data.append({'number': sheet.cell_value(r,0),
#                                 'content': sheet.cell_value(r,1)})
#                t = loader.get_template('sms/excel_sms.html')
#                c = RequestContext(request, {'data' : data})
#                return HttpResponse(t.render(c))
#            else:
#                if request.FILES:
#                    file = request.FILES['file']
#                    filepath = os.path.join(TEMP_FILE_LOCATION, 'sms_input.xls')
#                    if not file.content_type in CONTENT_TYPES:
#                        error = 'Bạn chỉ được phép tải lên file Excel.'
#                    elif os.path.getsize(filepath) == 0:
#                        os.remove(filepath)
#                        error = 'Hãy tải lên một file Excel đúng. File của bạn hiện đang trống.'
#                    elif xlrd.open_workbook(filepath).sheet_by_index(0).nrows == 0:
#                        os.remove(filepath)
#                        error = 'Hãy tải lên một file Excel đúng. File của bạn hiện đang trống.'
#                    t = loader.get_template('sms/excel_sms.html')
#                    c = RequestContext(request, {'error' : error})
#                    return HttpResponse(t.render(c))
#                else:
#                    t = loader.get_template('sms/excel_sms.html')
#                    c = RequestContext(request)
#                    return HttpResponse(t.render(c))
#
#        elif 'delete' in request.POST:
#            filepath = os.path.join(TEMP_FILE_LOCATION, 'sms_input.xls')
#            os.remove(filepath)
#            t = loader.get_template('sms/excel_sms.html')
#            c = RequestContext(request)
#            return HttpResponse(t.render(c))
#
#        elif 'send' in request.POST:
#            # update all record in sms db: recent = false
#            all_sms = sms.objects.filter(sender=request.user)
#            for s in all_sms:
#                s.recent = False
#                s.save()
#            filepath = os.path.join(TEMP_FILE_LOCATION, 'sms_input.xls')
#            list = xlrd.open_workbook(filepath)
#            sheet = list.sheet_by_index(0)
#
#            open = urllib2.build_opener(urllib2.HTTPCookieProcessor())
#            urllib2.install_opener(open)
#
#            para = urllib.urlencode({'u': 'VT_username', 'p': 'VT_password'})
#
##            f = open.open('http://viettelvas.vn:7777/fromcp.asmx', para)
##            f.close();
#            for r in range(1, sheet.nrows):
#                if checkValidPhoneNumber(sheet.cell_value(r,0)):
#                    '''Save to db'''
#                    s = sms(phone=sheet.cell_value(r,0), receiver=getUserFromPhone(sheet.cell_value(r,0)), content=sheet.cell_value(r,1), sender=request.user, recent=True, success=True)
#                    s.save()
#
#                    '''Send sms via Viettel system'''
#                    data = urllib.urlencode({
#                                'RequestID'     : '4',
#                                'CPCode'        : '',
#                                'UserID'        : '',
#                                'ReceiverID'    : sheet.cell_value(r,0),
#                                'ServiceID'     : '',
#                                'CommandCode'   : '',
#                                'Content'       : sheet.cell_value(r,1),
#                                'ContentType'   : '',
#                                })
##                    f = open.open('http://viettelvas.vn:7777/fromcp.asmx', data)
#                else:
#                    '''Save to db'''
#                    s = sms(phone=sheet.cell_value(r,0), receiver=getUserFromPhone(sheet.cell_value(r,0)), content=sheet.cell_value(r,1), sender=request.user, recent=True, success=False)
#                    s.save()
#
#            os.remove(filepath)
#            return HttpResponseRedirect('/sms/sent_sms/')
#    else:
#        if os.path.lexists(os.path.join(TEMP_FILE_LOCATION, 'sms_input.xls')):
#            filepath = os.path.join(TEMP_FILE_LOCATION, 'sms_input.xls')
#            list = xlrd.open_workbook(filepath)
#            sheet = list.sheet_by_index(0)
#            data = []
#            for r in range(1, sheet.nrows):
#                data.append({'number': sheet.cell_value(r,0),
#                            'content': sheet.cell_value(r,1)})
#            t = loader.get_template('sms/excel_sms.html')
#            c = RequestContext(request, {'data' : data})
#            return HttpResponse(t.render(c))
#        else:
#            t = loader.get_template('sms/excel_sms.html')
#            c = RequestContext(request)
#            return HttpResponse(t.render(c))
#
##def export_excel(request):
##    response = HttpResponse(mimetype="application/ms-excel")
##    response['Content-Disposition'] = 'attachment; filename=Thống kê tin nhắn.xls'
##
##    wb = xlwt.Workbook(encoding='utf-8')
##    ws = wb.add_sheet('Thống kê tin nhắn')
##
##    queryset=sms.objects.all()
##
##    ws.write(0, 0, 'Số điện thoại người nhận')
##    ws.write(0, 1, 'Nội dung tin nhắn')
##    ws.write(0, 2, 'Thời gian tạo')
##    ws.write(0, 4, 'Người gửi')
##    begin = 1;
##    for q in queryset:
##        ws.write(begin, 0, q.phone)
##        ws.write(begin, 1, q.content)
##        ws.write(begin, 2, q.created)
##        ws.write(begin, 4, q.sender.username)
##        begin = begin+1
##
##    wb.save(response)
##    return response
#
#def sent_sms(request):
#    sms_list = sms.objects.filter(sender=request.user,recent=True,success=True)
#    t = loader.get_template('sms/sent_sms.html')
#    c = RequestContext(request, {'sms_list': sms_list})
#    return HttpResponse(t.render(c))
#
#def failed_sms(request):
#    sms_list = sms.objects.filter(sender=request.user,recent=True,success=False)
#    t = loader.get_template('sms/failed_sms.html')
#    c = RequestContext(request, {'sms_list': sms_list})
#    return HttpResponse(t.render(c))
