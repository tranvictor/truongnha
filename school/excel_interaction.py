# coding=utf-8
import os
from datetime import date
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.db.models.query import QuerySet
from django.core.exceptions import ObjectDoesNotExist
import simplejson
import re
from utils import to_en1
import xlrd
from xlrd.formula import cellname
from xlwt.Formatting import Font, Borders
from xlwt.Style import XFStyle
from xlwt.Workbook import Workbook
from app.models import SystemLesson, SUBJECT_CHOICES
from decorators import school_function, need_login, operating_permission, year_started
from school.models import Class, Subject, SchoolLesson, validate_phone, Lesson, TKB
from school.models import this_year, StartYear
from school.templateExcel import *
from school.utils import get_latest_startyear, get_current_year, in_school,\
                            get_permission , gvcn, get_level, get_school, to_date,\
                            get_current_term, add_many_students, add_teacher, \
                            get_lower_bound
import settings
#Exporting session
@school_function
def class_generate(request, class_id, object):
    try:
        get_latest_startyear(request)
        year = get_current_year(request)
        if not in_school(request,year.school_id):
            return HttpResponseRedirect(reverse("school_index"))

    except Exception as e:
        print e
        return HttpResponseRedirect(reverse("school_index"))

    try:
        _class = Class.objects.get(id=class_id)
    except Exception as e:
        print e
        return HttpResponse()

    permission = get_permission(request)
    cn = gvcn(request, _class)

    if (not permission in [u'HIEU_TRUONG', u'HIEU_PHO']) and ( not cn) and (get_level(request)=='T'):
        return HttpResponseRedirect(reverse('school_index'))

    if object == 'student_list':
        student_list = _class.pupil_set.all().order_by('index')
        book = Workbook(encoding='utf-8')
        #renderring xls file
        sheet = book.add_sheet(u'Danh sách học sinh')
        sheet.write_merge(0, 1,0,4, u'DANH SÁCH HỌC SINH LỚP %s' % unicode(_class).upper(), h40)
        sheet.row(0).height = 350

        sheet.col(0).width = 1500
        sheet.col(1).width = 7000
        sheet.col(2).width = 4500
        sheet.col(3).width = 7000
        sheet.col(4).width = 3000
        sheet.col(5).width = 4000
        sheet.col(6).width = 7000
        sheet.col(7).width = 4500
        sheet.col(8).width = 7000
        sheet.col(9).width = 3000
        sheet.row(4).height = 350

        sheet.write(4, 0, 'STT',h4)
        sheet.write(4, 1, 'Họ và tên', h4)
        sheet.write(4, 2, 'Ngày sinh', h4)
        sheet.write(4, 3, 'Nơi sinh', h4)
        sheet.write(4, 4, 'Giới tính',h4)
        sheet.write(4, 5, 'Dân tộc', h4)
        sheet.write(4, 6, 'Chỗ ở hiện tại', h4)
        sheet.write(4, 7, 'Số điện thoại', h4)
        sheet.write(4, 8, 'Số điện thoại nhắn tin',h4)
        sheet.write(4, 9, 'Ghi chú', h4)
        row = 5
        for student in student_list:
            sheet.row(row).height = 350
            sheet.write(row, 0, row - 4, h7)
            sheet.write(row, 1, student.last_name + ' ' + student.first_name, h7)
            sheet.write(row, 2, student.birthday.strftime('%d/%m/%Y'), h7)
            sheet.write(row, 3, student.birth_place, h7)
            sheet.write(row, 4, student.sex, h7)
            sheet.write(row, 5, student.dan_toc, h7)
            sheet.write(row, 6, student.current_address, h7)
            sheet.write(row, 7, student.phone, h7)
            sheet.write(row, 8, student.sms_phone, h7)
            sheet.write(row, 9, '', h7)
            row += 1
            #return HttpResponse
        response = HttpResponse(mimetype='application/ms-excel')
        strstr = unicode(_class)
        strstr1 = strstr.replace(' ', '_')
        response['Content-Disposition'] = u'attachment; filename=ds_hoc_sinh_%s.xls' % strstr1
        book.save(response)
        return response
    else:
        raise Exception("PageDoesNotExist")

@school_function
def teacher_generate(request, type):
    school = get_school(request)
    try:
        get_latest_startyear(request)
        year = get_current_year(request)
        if not in_school(request,year.school_id):
            return HttpResponseRedirect(reverse('school_index'))
    except Exception as e:
        print e
        return HttpResponseRedirect(reverse("school_index"))

    permission = get_permission(request)
    if (not permission in [u'HIEU_TRUONG', u'HIEU_PHO']) and (get_level(request)=='T'):
        return HttpResponseRedirect(reverse('school_index'))

    if type == 'all':
#        file_name = request.session.session_key + unicode(school) + '_teacher_list.xls'
#        file_name = os.path.join(settings.TEMP_FILE_LOCATION, file_name)
        teacher_list = school.teacher_set.all().order_by('first_name', 'last_name', 'birthday')
        book = Workbook(encoding='utf-8')
        #renderring xls file

        fnt = Font()
        fnt.name = 'Arial'
        fnt.height = 240

        fnt_bold = Font()
        fnt_bold.name = 'Arial'
        fnt_bold.height = 240
        fnt_bold.bold = True

        borders = Borders()
        borders.left = Borders.THIN
        borders.right = Borders.THIN
        borders.top = Borders.THIN
        borders.bottom = Borders.THIN
        borders.left_colour = 0x17
        borders.right_colour = 0x17
        borders.top_colour = 0x17
        borders.bottom_colour = 0x17

        style = XFStyle()
        style.font = fnt
        style.borders = borders

        style_bold = XFStyle()
        style_bold.font = fnt_bold
        style_bold.borders = borders

        sheet = book.add_sheet('Danh sách giáo viên')
        sheet.write(0, 0, u'Danh sách giáo viên  %s' % unicode(school), style_bold)
        sheet.row(0).height = 350

        sheet.col(0).width = 1500
        sheet.col(1).width = 7000
        sheet.col(2).width = 4500
        sheet.col(3).width = 5000
        sheet.col(4).width = 7000
        sheet.col(5).width = 3000
        sheet.col(6).width = 4000
        sheet.col(7).width = 7000
        sheet.col(8).width = 7000
        sheet.row(4).height = 350

        sheet.write(4, 0, 'STT', style_bold)
        sheet.write(4, 1, 'Họ và Tên', style_bold)
        sheet.write(4, 2, 'Ngày sinh', style_bold)
        sheet.write(4, 3, 'Số điện thoại', style_bold)
        sheet.write(4, 4, 'Quê quán', style_bold)
        sheet.write(4, 5, 'Giới tính', style_bold)
        sheet.write(4, 6, 'Dạy môn', style_bold)
        sheet.write(4, 7, 'Tổ', style_bold)
        sheet.write(4, 8, 'Nhóm', style_bold)
        sheet.write(4, 9, 'Tài Khoản', style_bold)

        row = 5
        for teacher in teacher_list:
            sheet.row(row).height = 350
            sheet.write(row, 0, row - 4, style)
            sheet.write(row, 1, teacher.last_name + ' ' + teacher.first_name, style)
            if teacher.birthday:
                sheet.write(row, 2, teacher.birthday.strftime('%d/%m/%Y'), style)
            sheet.write(row, 3, teacher.sms_phone, style)
            sheet.write(row, 4, teacher.home_town, style)
            sheet.write(row, 5, teacher.sex, style)
            if teacher.major and teacher.major != '-1':
                sheet.write(row, 6, teacher.get_major_display(), style)
            else:
                sheet.write(row, 6, '', style)
            if teacher.team_id:
                sheet.write(row, 7, teacher.team_id.name, style)
            else:
                sheet.write(row, 7, '', style)
            if teacher.group_id:
                sheet.write(row, 8, teacher.group_id.name, style)
            else:
                sheet.write(row, 8, '', style)
            sheet.write(row, 9, teacher.user_id.username, style)
            row += 1
            #return HttpResponse
        response = HttpResponse(mimetype='application/ms-excel')
        response['Content-Disposition'] = u'attachment; filename=ds_giao_vien.xls'
        book.save(response)
        return response
    else:
        raise Exception('PageDoesNotExist')

@school_function
def export_agenda(request, subject_id):
    school = get_school(request)
    try:
        get_latest_startyear(request)
        get_current_year(request)
        sub = Subject.objects.get(id = subject_id)
    except Exception as e:
        print e
        return HttpResponseRedirect(reverse("school_index"))

    Lessons = sub.lesson_set.all().order_by('index')
#    file_name = request.session.session_key + unicode(school) + '_subject_agenda.xls'
#    file_name = os.path.join(settings.TEMP_FILE_LOCATION, file_name)
    book = Workbook(encoding='utf-8')
    #renderring xls file

    fnt = Font()
    fnt.name = 'Arial'
    fnt.height = 240

    fnt_bold = Font()
    fnt_bold.name = 'Arial'
    fnt_bold.height = 240
    fnt_bold.bold = True

    borders = Borders()
    borders.left = Borders.THIN
    borders.right = Borders.THIN
    borders.top = Borders.THIN
    borders.bottom = Borders.THIN
    borders.left_colour = 0x17
    borders.right_colour = 0x17
    borders.top_colour = 0x17
    borders.bottom_colour = 0x17

    style = XFStyle()
    style.font = fnt
    style.borders = borders

    style_bold = XFStyle()
    style_bold.font = fnt_bold
    style_bold.borders = borders

    sheet = book.add_sheet('Chương trình học')
    sheet.write(0, 1, u'%s' % unicode(school), style_bold)
    sheet.write(1, 1, u'Chương trình học môn ' + unicode(sub) + u' - lớp ' + unicode(sub.class_id), style_bold)
    sheet.row(0).height = 350
    sheet.col(0).width = 1500
    sheet.col(1).width = 15000
    sheet.col(2).width = 15000
    sheet.col(3).width = 5000
    sheet.row(4).height = 350

    sheet.write(4, 0, 'Tiết', style_bold)
    sheet.write(4, 1, 'Tiêu đề', style_bold)
    sheet.write(4, 2, 'Ghi chú', style_bold)



    row = 5
    for lesson in Lessons:
        sheet.row(row).height = 500
        sheet.write(row, 0, lesson.index, style)
        sheet.write(row, 1, lesson.title, style)
        sheet.write(row, 2, lesson.note, style)

        row += 1
        #return HttpResponse
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=Chuong_trinh_hoc.xls'
    book.save(response)
    return response

#noinspection PyUnusedLocal
@need_login
def export_system_agenda(request, subject, grade, term):

    Lessons = SystemLesson.objects.filter(subject = subject, grade = grade, term = term)
    book = Workbook(encoding='utf-8')
    #renderring xls file

    fnt = Font()
    fnt.name = 'Arial'
    fnt.height = 240

    fnt_bold = Font()
    fnt_bold.name = 'Arial'
    fnt_bold.height = 240
    fnt_bold.bold = True

    borders = Borders()
    borders.left = Borders.THIN
    borders.right = Borders.THIN
    borders.top = Borders.THIN
    borders.bottom = Borders.THIN
    borders.left_colour = 0x17
    borders.right_colour = 0x17
    borders.top_colour = 0x17
    borders.bottom_colour = 0x17

    style = XFStyle()
    style.font = fnt
    style.borders = borders

    style_bold = XFStyle()
    style_bold.font = fnt_bold
    style_bold.borders = borders

    sheet = book.add_sheet('Chương trình học')
    sheet.write(1, 1, u'Chương trình học' + u' môn ' + unicode(SUBJECT_CHOICES[int(subject)-1][1]) + u' khối ' + unicode(grade) + u' kì ' + unicode(term), style_bold)
    sheet.row(0).height = 350
    sheet.col(0).width = 1500
    sheet.col(1).width = 15000
    sheet.col(2).width = 15000
    sheet.col(3).width = 5000
    sheet.row(4).height = 350

    sheet.write(4, 0, 'Tiết', style_bold)
    sheet.write(4, 1, 'Tiêu đề', style_bold)
    sheet.write(4, 2, 'Ghi chú', style_bold)

    row = 5
    for lesson in Lessons:
        sheet.row(row).height = 500
        sheet.write(row, 0, lesson.index, style)
        sheet.write(row, 1, lesson.title, style)
        sheet.write(row, 2, lesson.note, style)

        row += 1

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=Chuong_trinh_hoc.xls'
    book.save(response)
    return response

@need_login
@school_function
def export_school_agenda(request, subject, grade, term):
    school = get_school(request)
    if not school.status:
        return HttpResponseRedirect(reverse('setup'))
    try:
        get_current_year(request)
    except Exception:
        return HttpResponseRedirect(reverse('setup'))

    user_type = get_permission(request)
    if not user_type in ['HIEU_TRUONG', 'HIEU_PHO']:
        return
    Lessons = SchoolLesson.objects.filter(subject = subject, grade = grade, term = term)
#    file_name = request.session.session_key + 'subject_agenda.xls'
#    file_name = os.path.join(settings.TEMP_FILE_LOCATION, file_name)
    book = Workbook(encoding='utf-8')
    #renderring xls file

    fnt = Font()
    fnt.name = 'Arial'
    fnt.height = 240

    fnt_bold = Font()
    fnt_bold.name = 'Arial'
    fnt_bold.height = 240
    fnt_bold.bold = True

    borders = Borders()
    borders.left = Borders.THIN
    borders.right = Borders.THIN
    borders.top = Borders.THIN
    borders.bottom = Borders.THIN
    borders.left_colour = 0x17
    borders.right_colour = 0x17
    borders.top_colour = 0x17
    borders.bottom_colour = 0x17

    style = XFStyle()
    style.font = fnt
    style.borders = borders

    style_bold = XFStyle()
    style_bold.font = fnt_bold
    style_bold.borders = borders

    sheet = book.add_sheet('Chương trình học')
    sheet.write(0, 1, unicode(school), style_bold)
    sheet.write(1, 1, u'Chương trình học' + u' môn ' + unicode(SUBJECT_CHOICES[int(subject)-1][1]) + u' khối ' + unicode(grade) + u' kì ' + unicode(term), style_bold)
    sheet.row(0).height = 350
    sheet.col(0).width = 1500
    sheet.col(1).width = 15000
    sheet.col(2).width = 15000
    sheet.col(3).width = 5000
    sheet.row(4).height = 350

    sheet.write(4, 0, 'Tiết', style_bold)
    sheet.write(4, 1, 'Tiêu đề', style_bold)
    sheet.write(4, 2, 'Ghi chú', style_bold)



    row = 5
    for lesson in Lessons:
        sheet.row(row).height = 500
        sheet.write(row, 0, lesson.index, style)
        sheet.write(row, 1, lesson.title, style)
        sheet.write(row, 2, lesson.note, style)

        row += 1
        #return HttpResponse
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=Chuong_trinh_hoc.xls'
    book.save(response)
    return response

#----------- Importing from Excel -------------------------------------

def save_file(import_file, session):
    import_file_name = import_file.name
    session_key = session.session_key
    save_file_name = session_key + import_file_name
    saved_file = open(os.path.join(settings.TEMP_FILE_LOCATION, save_file_name), 'wb+')
    for chunk in import_file.chunks():
        saved_file.write(chunk)
    saved_file.close()
    return save_file_name

def process_file(file_name, task):
    message = u'<ul>'
    if task == "import_student":
        student_list = []
        filepath = os.path.join(settings.TEMP_FILE_LOCATION, file_name)
        if not os.path.isfile(filepath):
            raise NameError, "%s is not a valid filename" % file_name
        try:
            book = xlrd.open_workbook(filepath)
            sheet = book.sheet_by_index(0)
        except Exception as e:
            print e
            return {'error': u'File tải lên không phải file Excel'}

        start_row = -1
        for c in range(0, sheet.ncols):
            flag = False
            for r in range(0, sheet.nrows):
                if unicode(sheet.cell_value(r, c)).lower() == u'họ và tên':
                    start_row = r
                    flag = True
                    break
            if flag: break
            #CHUA BIEN LUAN TRUONG HOP: start_row = -1, ko co cot ten: Mã học sinh
        if start_row == -1:
            return ({'error': u'File tải lên phải có cột "Họ và Tên".'},
                    u'File tải lên phải có cột "Họ và Tên".', 0, 0)
            # start_row != 0
        c_ten = -1
        c_ngay_sinh = -1
        c_gioi_tinh = -1
        c_noi_sinh = -1
        c_dan_toc = -1
        c_cho_o_ht = -1
        c_ten_bo = -1
        c_ten_me = -1
        c_so_dt_bo = -1
        c_so_dt_me = -1
        c_nguyen_vong = -1
        c_so_dt_nt = -1
        number = 0
        number_ok = 0
        for c in range(0, sheet.ncols):
            value = sheet.cell_value(start_row, c)
            if unicode(value).lower() == u'họ và tên':
                c_ten = c
            elif value == u'Ngày sinh':
                c_ngay_sinh = c
            elif value == u'Giới tính':
                c_gioi_tinh = c
            elif value == u'Nơi sinh':
                c_noi_sinh = c
            elif value == u'Dân tộc':
                c_dan_toc = c
            elif value == u'Chỗ ở hiện tại':
                c_cho_o_ht = c
            elif value == u'Họ tên bố':
                c_ten_bo = c
            elif value == u'Số điện thoại của bố':
                c_so_dt_bo = c
            elif value == u'Họ tên mẹ':
                c_ten_me = c
            elif value == u'Số điện thoại của mẹ':
                c_so_dt_me = c
            elif value == u'Ban đăng ký':
                c_nguyen_vong = c
            elif value == u'Số nhắn tin' or value == u'Số điện thoại nhắn tin':
                c_so_dt_nt = c
        for r in range(start_row + 1, sheet.nrows):
            gt = 'Nam'
            dan_toc = u'Kinh'
            noi_sinh = ''
            cho_o_ht = ''
            ten_bo = ''
            dt_bo = ''
            ten_me = ''
            dt_me = ''
            ban_dk = u'CB'
            sms_phone = ''
            name = sheet.cell(r, c_ten).value.strip()
            name = ' '.join([i.capitalize() for i in name.split(' ')])
            if not name.strip():
                message += u'<li>Ô ' + unicode(cellname(r, c_ten)) + u':Trống. </li>'
                continue
            number += 1
            birthday = sheet.cell(r, c_ngay_sinh).value
            if not birthday:
                message += u'<li>Ô ' + unicode(
                    cellname(r, c_ngay_sinh)) + u':Trống. Học sinh: ' + name + u' không đủ thông tin.</li>'
                continue
            if c_gioi_tinh > -1:
                gt = sheet.cell(r, c_gioi_tinh).value.strip().capitalize()
                if not gt: gt = 'Nam'
            if c_noi_sinh > -1:
                noi_sinh = sheet.cell(r, c_noi_sinh).value.strip()
            if c_dan_toc > -1:
                dan_toc = sheet.cell(r, c_dan_toc).value.strip()
                if not dan_toc.strip(): dan_toc = 'Kinh'
            if c_cho_o_ht > -1:
                cho_o_ht = sheet.cell(r, c_cho_o_ht).value.strip()
            if c_ten_bo > -1:
                ten_bo = sheet.cell(r, c_ten_bo).value.strip().capitalize()
            if c_so_dt_bo > -1:
                dt_bo = sheet.cell(r, c_so_dt_bo).value
                if dt_bo and (type(dt_bo)!= unicode or type(dt_bo)!=str):
                    dt_bo = unicode(int(dt_bo)).strip()
                if dt_bo and dt_bo[0] != '0' and dt_bo[0] != '+' and not dt_bo.startswith('84'): dt_bo = '0' + dt_bo
            if c_ten_me > -1:
                ten_me = sheet.cell(r, c_ten_me).value.strip().capitalize()
            if c_so_dt_me > -1:
                dt_bo = sheet.cell(r, c_so_dt_me).value
                if dt_me and (type(dt_me)!= unicode or type(dt_me)!=str):
                    dt_me = unicode(int(dt_me)).strip()
                if dt_me and dt_me[0] != '0' and dt_me[0] != '+' and not dt_me.startswith('84'): dt_me = '0' + dt_me
            if c_nguyen_vong > -1:
                ban_dk = sheet.cell(r, c_nguyen_vong).value.strip()
                if not ban_dk.strip(): ban_dk = 'CB'

            if c_so_dt_nt > -1:
                sms_phone = sheet.cell(r, c_so_dt_nt).value
                if type(sms_phone)!= unicode and type(sms_phone)!=str:
                    sms_phone = unicode(int(sms_phone)).strip()
                if sms_phone and sms_phone[0] != '0' and sms_phone[0] != '+' and not sms_phone.startswith('84'): sms_phone = '0' + sms_phone
                if sms_phone:
                    try:
                        validate_phone(sms_phone)
                    except Exception as e:
                        message += u'<li>Ô ' + unicode(
                            cellname(r, c_ngay_sinh)) + u':   Số điện thoại không hợp lệ ' + u'</li>'
                        sms_phone = ''
                        print e
            try:
                if isinstance(birthday, unicode) or isinstance(birthday, str):
                    birthday = to_date(birthday)
                else:
                    date_value = xlrd.xldate_as_tuple(sheet.cell(r, c_ngay_sinh).value, book.datemode)
                    birthday = date(*date_value[:3])
            except Exception as e:
                print e
                message += u'<li>Ô ' + unicode(
                    cellname(r, c_ngay_sinh)) + u':Không đúng định dạng "ngày/tháng/năm" ' + u'</li>'
                continue
            data = {'fullname': name,
                    'birthday': birthday,
                    'sex': gt,
                    'dan_toc': dan_toc,
                    'birth_place': noi_sinh,
                    'current_address': cho_o_ht,
                    'father_name': ten_bo,
                    'father_phone': dt_bo,
                    'mother_name': ten_me,
                    'mother_phone': dt_me,
                    'ban_dk': ban_dk,
                    'sms_phone': sms_phone}
            student_list.append(data)
            number_ok += 1
        message += u'</ul>'
        return student_list, message, number, number_ok
    elif task == u"import_teacher":
        teacher_list = {}
        filepath = os.path.join(settings.TEMP_FILE_LOCATION, file_name)
        if not os.path.isfile(filepath):
            raise NameError, "%s is not a valid filename" % file_name
        try:
            book = xlrd.open_workbook(filepath)
            sheet = book.sheet_by_index(0)
        except Exception as e:
            print e
            return {'error': u'File tải lên không phải file Excel'}

        start_row = -1
        for c in range(0, sheet.ncols):
            flag = False
            for r in range(0, sheet.nrows):
                if sheet.cell_value(r, c) in [u'Họ và Tên', u'Họ Tên', u'Tên']:
                    start_row = r
                    flag = True
                    break
            if flag: break
            #CHUA BIEN LUAN TRUONG HOP: start_row = -1, ko co cot ten: Mã học sinh
        if start_row == -1:
            return ({'error': u'File tải lên phải có cột "Họ và Tên".'},
                    u'File tải lên phải có cột "Họ và Tên".', 0, 0)
            # start_row != 0
        c_ten = -1
        c_ngay_sinh = -1
        c_gioi_tinh = -1
        c_que_quan = -1
        c_dan_toc = -1
        c_cho_o_ht = -1
        c_to = -1
        c_nhom = -1
        c_chuyen_mon = -1
        c_phone = -1
        c_pccm = -1
        c_cn = -1

        number = 0
        number_ok = 0
        for c in range(0, sheet.ncols):
            value = sheet.cell_value(start_row, c)
            if value == u'Họ và Tên':
                c_ten = c
            elif value == u'Ngày sinh':
                c_ngay_sinh = c
            elif value == u'Giới tính':
                c_gioi_tinh = c
            elif value == u'Quê quán':
                c_que_quan = c
            elif value == u'Dân tộc':
                c_dan_toc = c
            elif value == u'Chỗ ở hiện tại':
                c_cho_o_ht = c
            elif value == u'Tổ':
                c_to = c
            elif value == u'Nhóm':
                c_nhom = c
            elif value in [u'Dạy môn', u'Chuyên môn']:
                c_chuyen_mon = c
            elif value in [u'Số điện thoại', u'Điện thoại']:
                c_phone = c
            elif value == u'Lớp chủ nhiệm':
                c_cn = c
            elif value == u'Phân công chuyên môn':
                c_pccm = c
        start_row += 1
        #Search for class columns
        c_classes = {}
        re_class = re.compile('(?P<grade>6|7|8|9|10|11|12)\s*(?P<label>.+)',
                flags=re.U)
        if c_pccm != -1:
            for c in range(c_pccm, sheet.ncols):
                value = sheet.cell_value(start_row, c) 
                temp = re_class.match(value)
                if not temp: message += u'<li>Ô %s: Tên lớp không đúng.</li>' \
                                        % unicode(cellname(start_row, c))
                else:
                    cl_n = ' '.join(temp.groups()) 
                    if cl_n in c_classes:
                        message += u'<li>2 Ô %s và %s: Trùng nhau' \
                                    % (unicode(cellname(start_row,c)),
                                       unicode(cellname(start_row, c_classes[cl_n])))
                    else:
                        c_classes[cl_n] = c
        for r in range(start_row + 1, sheet.nrows):
            gt = ''
            dan_toc = ''
            que_quan = ''
            cho_o_ht = ''
            to = ''
            nhom = ''
            chuyen_mon = ''
            phone = ''
            lop_cn = ''
            lop_cmon = []
            name = sheet.cell(r, c_ten).value.strip()
            name = ' '.join([i.capitalize() for i in name.split(' ')])
            if not name.strip():
                message += u'<li>Ô ' + unicode(cellname(r, c_ten)) + u':Trống. </li>'
                continue
            number += 1
            birthday = sheet.cell(r, c_ngay_sinh).value
            if not birthday:
                message += u'<li>Ô ' + unicode(cellname(r, c_ngay_sinh)) + u':Trống. </li>'
                birthday = None
            if c_gioi_tinh > -1:
                gt = sheet.cell(r, c_gioi_tinh).value.strip().capitalize()
                if not gt: gt = 'Nam'
            if c_que_quan > -1:
                que_quan = sheet.cell(r, c_que_quan).value.strip()
            if c_dan_toc > -1:
                dan_toc = sheet.cell(r, c_dan_toc).value.strip()
                if not dan_toc.strip(): dan_toc = 'Kinh'
            if c_cho_o_ht > -1:
                cho_o_ht = sheet.cell(r, c_cho_o_ht).value.strip()
            if c_to > -1:
                to = sheet.cell(r, c_to).value.strip()
            if c_nhom > -1:
                nhom = sheet.cell(r, c_nhom).value.strip()
            if c_chuyen_mon > -1:
                chuyen_mon = sheet.cell(r, c_chuyen_mon).value.strip()
            if c_phone > -1:
                phone = sheet.cell(r, c_phone).value
                if type(phone) != unicode and type(phone) != str:
                    phone = unicode(int(phone)).strip()
                if phone and phone[0] != '0' and phone[0] != '+':
                    phone = '0' + phone
            if birthday:
                try:
                    if type(birthday) == unicode or type(birthday) == str:
                        birthday = to_date(birthday)
                    else:
                        date_value = xlrd.xldate_as_tuple(
                                sheet.cell(r, c_ngay_sinh).value,
                                book.datemode)
                        birthday = date(*date_value[:3])
                except Exception as e:
                    print e
                    message += u'<li>Ô ' + unicode( cellname(r, c_ngay_sinh)) \
                            + u':Không đúng định dạng "ngày/tháng/năm" ' + u'</li>'
                    continue
            if c_cn:
                lop_cn = sheet.cell(r, c_cn).value
                if not re_class.match(lop_cn): lop_cn = ''
                else:
                    lop_cn = ' '.join(re_class.match(lop_cn).groups())

            if chuyen_mon:
                for ele in c_classes.iteritems():
                    cl_n = ele[0]
                    c = int(ele[1])
                    value = sheet.cell(r, c).value
                    if unicode(value).strip():
                        lop_cmon.append('-'.join([cl_n, chuyen_mon]))
             
            data = {'fullname': name,
                    'birthday': birthday,
                    'sex': gt,
                    'dan_toc': dan_toc,
                    'home_town': que_quan,
                    'current_address': cho_o_ht,
                    'team': to,
                    'group': nhom,
                    'major': chuyen_mon,
                    'sms_phone': phone,
                    'lop_cn': lop_cn,
                    'lop_cmon': lop_cmon}
            identifier = name + '-' + unicode(birthday)
            if identifier in teacher_list:
                teacher_list[identifier]['lop_cmon'].extend(lop_cmon)
            else:
                teacher_list[identifier] = data
                number_ok += 1
        message += u'</ul>'
        return teacher_list, message, number, number_ok
    return None

#noinspection PyUnusedLocal
def processFileAgenda(request, subject_id, file_name):
    filepath = os.path.join(settings.TEMP_FILE_LOCATION, file_name)
    if not os.path.isfile(filepath):
        raise NameError, "%s is not a valid filename" % file_name
    try:
        book = xlrd.open_workbook(filepath)
        sheet = book.sheet_by_index(0)
    except Exception as e:
        print e
        return {'error': u'File tải lên không phải file Excel'}, u'File tải lên không phải file Excel'

    start_col = -1
    start_row = -1
    try:
        for c in range(0, sheet.ncols):
            flag = False
            for r in range(0, sheet.nrows):
                if sheet.cell_value(r, c) == u'Tiết':
                    start_col = c
                    start_row = r
                    flag = True
                    break
            if flag: break
    except Exception as e:
        print e
        return {'error': u'File tải lên không phải file Excel'}, u'File tải lên không phải file Excel'

    if start_col == -1:
        return {'error': u'File tải lên phải có cột "Tiết".'}, u'File tải lên phải có cột "Tiết".'
    sub = Subject.objects.get(id=subject_id)
    try:
        lessons = sub.lesson_set.all()
        for iLesson in lessons:
            iLesson.delete()
    except Exception:
        pass
    sub.max = 0
    sub.save()
    message = u'<ul>'

    for r in range(start_row+1, sheet.nrows):
        try:
            try:
                index = int(sheet.cell_value(r, 0))
            except Exception as ie:
                print ie
                message += u'<ul>Tiết trống hoặc không đúng ở ô (' + str(r) + ', 1).</ul>'
                continue
            title = sheet.cell_value(r, 1).strip()
            if not title:
                message += u'<ul>Tiêu đề ở tiết thứ ' + str(index) + u' bị trống</ul>'
                continue
            note = sheet.cell_value(r, 2).strip()
        except Exception as e:
            print str(e)
            return {'error': u'File tải lên không phải file Excel'}, message
        less = Lesson()
        less.index = index
        less.subject_id = sub
        less.note = note
        less.title = title
        less.save()
        sub.max += 1
        sub.save()

    message += u'</ul>'
    result = {'Thành công': u'Dữ liệu được tải thành công'}
    return result, message

@need_login
@operating_permission(['SUPER_USER__system', 'HIEU_TRUONG__school', 'HIEU_PHO__school'])
@year_started
def processFileSystemAgenda(request, subject, grade, term, file_name, request_type = u'system'):
    school = None
    try:
        school = get_school(request)
    except Exception as e:
        print e
        pass
    filepath = None
    try:
        filepath = os.path.join(settings.TEMP_FILE_LOCATION, file_name)
        if not os.path.isfile(filepath):
            raise NameError, "%s is not a valid filename" % file_name
    except Exception as e:
        print e

    try:
        book = xlrd.open_workbook(filepath)
        sheet = book.sheet_by_index(0)
    except Exception as e:
        print e
        return {'error': u'File tải lên không phải file Excel'}, u'File tải lên không phải file Excel'
    start_col = -1
    start_row = -1
    try:
        for c in range(0, sheet.ncols):
            flag = False
            for r in range(0, sheet.nrows):
                if sheet.cell_value(r, c) == u'Tiết':
                    start_col = c
                    start_row = r
                    flag = True
                    break
            if flag: break
    except Exception as e:
        print e
        return {'error': u'File tải lên không phải file Excel'}, u'File tải lên không phải file Excel'


    if start_col == -1:
        return {'error': u'File tải lên phải có cột "Tiết".'}, u'File tải lên phải có cột "Tiết".'
    if request_type == u'system':
        try:
            lessons = SystemLesson.objects.filter(subject = subject, grade = grade, term = term)
            for iLesson in lessons:
                iLesson.delete()
        except Exception:
            pass
    else:
        try:
            lessons = SchoolLesson.objects.filter(school = school.id, subject = subject, grade = grade, term = term)
            for iLesson in lessons:
                iLesson.delete()
        except Exception:
            pass
    message = u'<ul>'
    for r in range(start_row+1, sheet.nrows):
        try:
            try:
                index = int(sheet.cell_value(r, 0))
            except Exception as ie:
                print ie
                message += u'<ul>Tiết trống hoặc không đúng ở ô (' + str(r) + u', 1).</ul>'
                continue

            title = sheet.cell_value(r, 1).strip()
            if not title:
                message += u'<ul>Tiêu đề ở tiết thứ ' + str(index) + u' bị trống</ul>'
                continue
            note = sheet.cell_value(r, 2).strip()

        except Exception as e:
            print str(e)
            return {'error': u'File tải lên không phải file Excel'}, message
        try:
            if request_type == u'system':
                less = SystemLesson()
                less.index = index
                less.subject = subject
                less.term = term
                less.grade = grade
                less.note = note
                less.title = title
                less.save()
            else:
                less = SchoolLesson()
                less.school = school
                less.index = index
                less.subject = subject
                less.term = term
                less.grade = grade
                less.note = note
                less.title = title
                less.save()
        except Exception as e:
            print e

    message += u'</ul>'
    result = {'Thành công': u'Dữ liệu được tải thành công'}
    return result, message

def match_subject (subject, subject_name):
    sub_type = to_en1(subject.type).strip().lower()
    sub_name =to_en1(subject.name).strip().lower()
    subject_name = to_en1(subject_name).strip().lower()
    try:
#        print sub_type + u' ' + sub_name + u' ' + subject_name + '11111'
        sub_list = {}
        sub_list[1] = [u'toan']
        sub_list[2] = [u'vat ly', u'vat li', u'ly', u'li']
        sub_list[3] = [ u'dia ly', u'dia li']
        sub_list[4] = [u'van', u'ngu van', u'van hoc']
        sub_list[5] = [u'sinh', u'sinh hoc', u'sinh vat']
        sub_list[6] = [u'hoa hoc', u'hoa']
        sub_list[7] = [u'ngoai ngu', u'tieng anh', u'anh van', u'anh']
        sub_list[8] = [u'gdcd']
        sub_list[9] = [u'cong nghe']
        sub_list[10] = [u'the duc']
        sub_list[11] = [u'am nhac']
        sub_list[12] = [u'mi thuat', u'my thuat', u've']
        sub_list[13] = [u'tin hoc']
        sub_list[14] = [u'gdqp-an',u'quan su', u'gdqpan']
        sub_list[15] = [u'nn2', u'ngoai ngu 2']
        sub_list[16] = [u'lich su', u'su']

        for i in range (1, 17):
            if (sub_type in sub_list[i] and subject_name in sub_list[i]) or (sub_name in sub_list[i] and subject_name in sub_list[i]):
                return True
        return False
    except Exception as e:
        print e
    return False

def processFileTKB(request, file_name):
    filepath = os.path.join(settings.TEMP_FILE_LOCATION, file_name)
    if not os.path.isfile(filepath):
        raise NameError, "%s is not a valid filename" % file_name
    try:
        book = xlrd.open_workbook(filepath)
        sheet = book.sheet_by_index(0)
    except Exception as e:
        print e
        return {'error': u'File tải lên không phải file Excel'}

    start_col = -1
    start_row = -1
    try:
        for c in range(0, sheet.ncols):
            flag = False
            for r in range(0, sheet.nrows):
                if sheet.cell_value(r, c) == u'Thứ':
                    start_col = c
                    start_row = r
                    flag = True
                    break
            if flag: break
    except Exception as e:
        print e
        return {'error': u'File tải lên không phải file Excel'}, u'File tải lên không phải file Excel'

    if start_col == -1:
        return {'error': u'File tải lên phải có cột "Thứ".'}, u'File tải lên phải có cột "Thứ".'
        # start_row != 0

    school = get_school(request)
    year = get_current_year(request)
    class_list = year.class_set.all()
    for cl in class_list:
        all_t = cl.tkb_set.all().delete()

    message = u'<ul>'

    for c in range(start_col + 2, sheet.ncols):
        try:
            className = sheet.cell(start_row, c).value.strip().lower().replace(' ', '')
            cls = year.class_set.all()
            cl = None
            for _cl in cls:
                if _cl.strip_name() == className:
                    cl = _cl
                    break

            if not cl:
                message += u'<li>Không tồn tại lớp ' + sheet.cell(start_row, c).value.strip() + u'</li>'
                continue
        except Exception as e:
            print e
            return {'error': u'File tải lên không phải file Excel'}

        for d in range(2, 8):
            try:
                t = TKB()
                t.day = d
                t.class_id = cl
            except Exception as e:
                print e
                return {'error': u'File tải lên không phải file Excel'}

            r = start_row + 10 * (d - 2) + 1
            sbj = cl.subject_set.all()
            for i in range(0, 10):
                sb = None
                subjectName = sheet.cell(r + i, c).value
                for _sb in sbj:
                    if match_subject(_sb, subjectName):
                        sb = _sb
                        break
                setattr(t, 'period_' + str(i+1), sb)
                if not sb and subjectName:
                    convert_subjectName = to_en1(subjectName).strip().lower()
                    if convert_subjectName == u'chao co':
                        setattr(t, 'chaoco', i+1)
                    elif convert_subjectName == u'sinh hoat':
                        setattr(t, 'sinhhoat', i+1)
                    else:
                        message += u'<li>Không tồn tại môn ' + sheet.cell(r+i, c).value + u' trong lớp ' + sheet.cell(start_row,
                        c).value.strip() + u'</li>'
            t.save()

    #get warning for duplications
    try:
        teachers = school.teacher_set.all()
        for iteacher in teachers:
            list_work = []
            warnings = []
            subs = iteacher.subject_set.all()
            for sub in subs:
                cl = sub.class_id
                tkbs = cl.tkb_set.all()
                for tkb in tkbs:
                    nlesson = tkb.get_numbers(sub)
                    for ilesson in nlesson:
                        if (tkb.day, ilesson) in list_work:
                            if not (tkb.day, ilesson) in warnings:
                                warnings.append((tkb.day, ilesson))
                        else:
                            list_work.append((tkb.day, ilesson))
            for u, v in warnings:
                print iteacher
                message += u'<li>CHÚ Ý: Giáo viên ' + iteacher.full_name() + u' dạy nhiều hơn một lớp vào tiết ' + str(v) + u', thứ ' + str(u) + u'</li>'
    except Exception as e:
        print e
    message += u'</ul>'
    result = {'Thành công': u'Dữ liệu được tải thành công'}
    return result, message

@need_login
@require_POST
@school_function
@operating_permission([u'HIEU_TRUONG', u'HIEU_PHO'])
def student_import( request, class_id, request_type='' ):
    school = get_school(request)
    if request.is_ajax():
        if request_type == u'update':
            chosen_class = Class.objects.get(id=int(class_id))
            lb = get_lower_bound(school)
            syear = this_year() - chosen_class.block_id.number + lb
            year, temp = StartYear.objects.get_or_create(time=syear,
                                                           school_id=school)
            current_year = get_current_year(request)
            term = get_current_term(request)
            saving_import_student = request.session.pop('saving_import_student')
            number_of_change = add_many_students(student_list=saving_import_student,
                _class=chosen_class,
                start_year=year, year=current_year,
                term=term, school=school,
                force_update=True)
            if number_of_change:
                data = simplejson.dumps(
                        {'success': True,
                        'message': u'Đã cập nhật %s học sinh.' % number_of_change})
            else:
                data = simplejson.dumps(
                        {'success': True,
                        'message': u'Thông tin không thay đổi'})
            return HttpResponse(data, mimetype='json')
            # AJAX Upload will pass the filename in the querystring if it is the "advanced" ajax upload
        try:
            file = request.FILES.get('files[]')
        except KeyError:
            return HttpResponseBadRequest("AJAX request not valid")
            # not an ajax upload, so it was the "basic" iframe version with submission via form
    else:
        if len(request.FILES) == 1:
        # FILES is a dictionary in Django but Ajax Upload gives the uploaded file an
        # ID based on a random number, so it cannot be guessed here in the code.
        # Rather than editing Ajax Upload to pass the ID in the querystring,
        # observer that each upload is a separate request,
        # so FILES should only have one entry.
        # Thus, we can just grab the first (and only) value in the dict.
            file = request.FILES.values()[0]
        else:
            raise Exception('BadUpload')

    filename = save_file(request.FILES.get('files[]'), request.session)
    result, process_file_message, number, number_ok = process_file(filename,
                                                                   "import_student")
    if 'error' in result:
        success = False
        message = result['error']
        data = [{'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'success': success,
                 'message': message,
                 'process_message': process_file_message,
                 'error': u'File excel không đúng định dạng'}]
    else:
        chosen_class = Class.objects.get(id=int(class_id))
        #year = school.startyear_set.latest('time')
        lb = get_lower_bound(school)
        syear = this_year() - chosen_class.block_id.number + lb
        year, temp = StartYear.objects.get_or_create(time=syear,
                                                    school_id=school)
        current_year = get_current_year(request)
        term = get_current_term(request)
        existing_student = add_many_students(student_list=result,
                                             _class=chosen_class,
                                             start_year=year, year=current_year,
                                             term=term, school=school)
        student_confliction = ''
        if existing_student:
            student_confliction = u'Có %s học sinh không được nhập do đã tồn tại trong hệ thống' % len(existing_student)
            request.session['saving_import_student'] = existing_student
        data = [{'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'process_message': process_file_message,
                 'student_confliction': student_confliction,
                 'number': number,
                 'number_ok': number_ok - len(existing_student),
                 'message': u'Nhập dữ liệu thành công'}]
    return HttpResponse(simplejson.dumps(data))

@need_login
@require_POST
@school_function
@operating_permission([u'HIEU_TRUONG', u'HIEU_PHO'])
def teacher_import( request, request_type=''):
    school = get_school(request)
    year = get_current_year(request)
    if request.is_ajax():
        if request_type == u'update':
            saving_import_teacher = request.session.pop('saving_import_teacher')
            number_of_updated = 0
            for teacher in saving_import_teacher:
                try:
                    added_t = add_teacher(full_name=teacher['fullname'],
                                birthday=teacher['birthday'],
                                sex=teacher['sex'],
                                dan_toc=teacher['dan_toc'],
                                home_town=teacher['home_town'],
                                current_address=teacher['current_address'],
                                team_id=teacher['team'],
                                group_id=teacher['group'],
                                major=teacher['major'],
                                sms_phone=teacher['sms_phone'],
                                school=school,
                                force_update=True)
                    number_of_updated += 1
                    try:
                        home_cl = year.class_set.get(name=teacher['lop_cn'])
                        home_cl.teacher_id = added_t
                        home_cl.save()
                    except ObjectDoesNotExist:
                        pass
                    lop_cmons = teacher['lop_cmon']
                    for l in lop_cmons:
                        ele = l.split('-')
                        try:
                            lop = year.class_set.get(name=ele[0])
                            sub = lop.subject_set.get(type=ele[1])
                            sub.teacher_id = added_t
                            sub.save()
                        except ObjectDoesNotExist:
                            pass
                except Exception as e:
                    print e
            data = simplejson.dumps({'success': True,
                                     'message': u'Đã cập nhật ' + unicode(number_of_updated) + u' giáo viên.'})
            return HttpResponse(data, mimetype='json')
        try:
            file = request.FILES.get('files[]')
        except KeyError:
            return HttpResponseBadRequest("AJAX request not valid")
            # not an ajax upload, so it was the "basic" iframe version with submission via form
    else:
        if len(request.FILES) == 1:
        # FILES is a dictionary in Django but Ajax Upload gives the uploaded file an
        # ID based on a random number, so it cannot be guessed here in the code.
        # Rather than editing Ajax Upload to pass the ID in the querystring,
        # observer that each upload is a separate request,
        # so FILES should only have one entry.
        # Thus, we can just grab the first (and only) value in the dict.
            file = request.FILES.values()[0]
        else:
            raise Exception('BadUpload')
    filename = save_file(request.FILES.get('files[]'), request.session)
    result, process_file_message, number, number_ok = process_file(filename, "import_teacher")
    existing_teacher = []
    saving_import_teacher = []
    if 'error' in result:
        success = False
        message = result['error']
        data = [{'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'success': success,
                 'message': message,
                 'process_message': process_file_message,
                 'error': u'File excel không đúng định dạng'}]
    else:
        try:
            teacher_list = result
            for teacher in teacher_list.iteritems():
                teacher = teacher[1]
                try:
                    added_t = add_teacher(full_name=teacher['fullname'],
                        birthday=teacher['birthday'],
                        sex=teacher['sex'],
                        dan_toc=teacher['dan_toc'],
                        home_town=teacher['home_town'],
                        current_address=teacher['current_address'],
                        team_id=teacher['team'],
                        group_id=teacher['group'],
                        major=teacher['major'],
                        sms_phone=teacher['sms_phone'],
                        school=school)
                    if isinstance(added_t, QuerySet):
                        existing_teacher.append(added_t)
                        saving_import_teacher.append(teacher)
                    else:
                        # update lop_cn, lop_cmon
                        print teacher['lop_cn']
                        print year
                        try:
                            home_cl = year.class_set.get(name=teacher['lop_cn'])
                            home_cl.teacher_id = added_t
                            home_cl.save()
                        except ObjectDoesNotExist:
                            pass
                        lop_cmons = teacher['lop_cmon']
                        for l in lop_cmons:
                            ele = l.split('-')
                            print ele, ele[0]
                            try:
                                lop = year.class_set.get(name=ele[0])
                                sub = lop.subject_set.get(type=ele[1])
                                sub.teacher_id = added_t
                                sub.save()
                            except ObjectDoesNotExist:
                                pass
                except Exception as e:
                    print e
        except Exception as e:
            print e
            #TODO: should have a way to notice user about saving interruption
        teacher_confliction = ''
        if existing_teacher:
            teacher_confliction = u'Có %s giáo viên không được nhập do đã tồn tại trong hệ thống' % len(
                existing_teacher)
            request.session['saving_import_teacher'] = saving_import_teacher
        data = [{'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'process_message': process_file_message,
                 'teacher_confliction': teacher_confliction,
                 'number': number,
                 'number_existing': len(existing_teacher),
                 'number_ok': number_ok - len(existing_teacher),
                 'message': 'Hoàn tất'}]
    return HttpResponse(simplejson.dumps(data))

@need_login
@require_POST
@school_function
@year_started
@operating_permission([u'HIEU_TRUONG', u'HIEU_PHO'])
def import_school_agenda(request, subject, grade, term):
    if request.is_ajax():
        try:
            file = request.FILES.get('files[]')
        except KeyError:
            return HttpResponseBadRequest("AJAX request not valid")
    else:
        if len(request.FILES) == 1:
            file = request.FILES.values()[0]
        else:
            raise Exception('BadUpload')
    filename = save_file(request.FILES.get('files[]'), request.session)
    result, process_file_message = processFileSystemAgenda(request, subject, grade, term, filename, u'school')
    if 'error' in result:
        success = False
        message = result['error']
        data = [{'success': success,
                 'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'process_message': process_file_message,
                 'message': message,
                 'error': u'File excel không đúng định dạng'}]
    else:
        data = [{'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'process_message': process_file_message,
                 'message': u'Nhập dữ liệu thành công'}]
    return HttpResponse(simplejson.dumps(data))

@need_login
@require_POST
@operating_permission(['SUPER_USER'])
def import_system_agenda(request, subject, grade, term):
    if request.is_ajax():
        try:
            file = request.FILES.get('files[]')
        except KeyError:
            return HttpResponseBadRequest("AJAX request not valid")
    else:
        if len(request.FILES) == 1:
            file = request.FILES.values()[0]
        else:
            raise Exception("BadUpload")
    filename = save_file(request.FILES.get('files[]'), request.session)
    result, process_file_message = processFileSystemAgenda(request, subject, grade, term, filename, 'system')

    if 'error' in result:
        success = False
        message = result['error']
        data = [{'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'success': success,
                 'message': message,
                 'process_message': process_file_message,
                 'error': u'File excel không đúng định dạng'}]

    else:
        data = [{'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'process_message': process_file_message,
                 'message': u'Nhập dữ liệu thành công'}]
    return HttpResponse(simplejson.dumps(data))

@need_login
@require_POST
@school_function
@operating_permission([u'GIAO_VIEN', u'HIEU_PHO', u'HIEU_TRUONG'])
def import_agenda(request, subject_id):
    if request.is_ajax():
        try:
            file = request.FILES.get('files[]')
        except KeyError:
            return HttpResponseBadRequest("AJAX request not valid")
    else:
        if len(request.FILES) == 1:
            file = request.FILES.values()[0]
        else:
            raise Exception("BadUpload")
    filename = save_file(request.FILES.get('files[]'), request.session)
    result, process_file_message = processFileAgenda(request, subject_id, filename)
    print 'done processing', result, process_file_message
    if 'error' in result:
        success = False
        message = result['error']
        data = [{'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'message': message,
                 'success': success,
                 'process_message': process_file_message,
                 'error': u'File excel không đúng định dạng'}]

    else:
        data = [{'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'process_message': process_file_message,
                 'message': u'Nhập dữ liệu thành công'}]
    return HttpResponse(simplejson.dumps(data))

@need_login
@require_POST
@school_function
@operating_permission([u'GIAO_VU', u'GIAO_VIEN', u'HIEU_PHO', u'HIEU_TRUONG'])
def import_timeTable(request):
    if request.is_ajax():
        try:
            file = request.FILES.get('files[]')
        except KeyError:
            return HttpResponseBadRequest("AJAX request not valid")
    else:
        if len(request.FILES) == 1:
            file = request.FILES.values()[0]
        else:
            raise Exception("BadUpload")
    filename = save_file(request.FILES.get('files[]'), request.session)
    result, process_file_message = processFileTKB(request, filename)

    if 'error' in result:
        success = False
        message = result['error']
        data = [{'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'success': success,
                 'message': message,
                 'process_message': process_file_message,
                 'error': u'File excel không đúng định dạng'}]

    else:
        data = [{'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'process_message': process_file_message,
                 'message': u'Nhập dữ liệu thành công'}]
    return HttpResponse(simplejson.dumps(data))

@need_login
@school_function
def export_hanh_kiem(request, class_id):
    school = get_school(request)
    cl = Class.objects.get(id = class_id)
    book = Workbook(encoding='utf-8')
    #renderring xls file
    fnt = Font()
    fnt.name = 'Arial'
    fnt.height = 240

    fnt_bold = Font()
    fnt_bold.name = 'Arial'
    fnt_bold.height = 240
    fnt_bold.bold = True

    borders = Borders()
    borders.left = Borders.THIN
    borders.right = Borders.THIN
    borders.top = Borders.THIN
    borders.bottom = Borders.THIN
    borders.left_colour = 0x17
    borders.right_colour = 0x17
    borders.top_colour = 0x17
    borders.bottom_colour = 0x17

    style = XFStyle()
    style.font = fnt
    style.borders = borders

    style_bold = XFStyle()
    style_bold.font = fnt_bold
    style_bold.borders = borders

    sheet = book.add_sheet('Hạnh kiểm')
    sheet.set_portrait(0)
    sheet.write_merge(0, 0, 0, 15, u'%s' % unicode(school), h9)
    sheet.write_merge(1, 1, 0, 15, u'Hạnh kiểm lớp ' + unicode(cl), h9)
    sheet.row(0).height = 240
    sheet.col(0).width = 1500
    sheet.col(1).width = 5000
    sheet.col(2).width = 2500
    sheet.col(3).width = 5000
    month_width = 2000
    sheet.col(4).width = month_width
    sheet.col(5).width = month_width
    sheet.col(6).width = month_width
    sheet.col(7).width = month_width
    sheet.col(8).width = month_width
    sheet.col(9).width = month_width
    sheet.col(10).width = month_width
    sheet.col(11).width = month_width
    sheet.col(12).width = month_width
    sheet.col(13).width = month_width
    sheet.col(14).width = month_width
    sheet.col(15).width = 2500
    sheet.col(16).width = 1000
    sheet.col(18).width = 2500
    sheet.col(17).width = 5000

    #documentation
    sheet.write(4, 17, 'Trung Bình', h5)
    sheet.write(4, 18, 'TB', h5)
    sheet.write(3, 17, 'Yếu', h5)
    sheet.write(3, 18, 'Y', h5)
    sheet.write(5, 17, 'Khá', h5)
    sheet.write(5, 18, 'K', h5)
    sheet.write(6, 17, 'Tốt', h5)
    sheet.write(6, 18, 'T', h5)

    #title
    sheet.row(4).height = 350
    sheet.write(4, 0, 'STT', h4)
    sheet.write_merge(4, 4, 1, 2, 'Họ tên', h4)
    sheet.write(4, 3, 'Ngày sinh', h4)
    sheet.write(4, 4, 'Th. 9', h4)
    sheet.write(4, 5, 'Th. 10', h4)
    sheet.write(4, 6, 'Th. 11', h4)
    sheet.write(4, 7, 'Th. 12', h4)
    sheet.write(4, 8, 'Th. 1', h4)
    sheet.write(4, 9, 'Th. 2', h4)
    sheet.write(4, 10, 'Th. 3', h4)
    sheet.write(4, 11, 'Th. 4', h4)
    sheet.write(4, 12, 'Th. 5', h4)
    sheet.write(4, 13, 'Kì 1', h4)
    sheet.write(4, 14, 'Kì 2', h4)
    sheet.write(4, 15, 'Cả năm', h4)

    irow = 5
    year = get_current_year(request)
    pupilList = cl.student_set.filter(attend__leave_time=None).order_by('index')
    for ipupil in pupilList:
        TK = ipupil.tbnam_set.get(year_id__exact=year.id)
        if irow % 5 !=4:
            h=h61
        else        :
            h=h71
        sheet.row(irow).height = 500
        sheet.write(irow, 0, irow - 4, h)
        if irow%5 != 4:
            sheet.write(irow, 1,  ipupil.last_name, last_name)
            sheet.write(irow, 2, ipupil.first_name, first_name)
        else:
            sheet.write(irow, 1,  ipupil.last_name, last_name1)
            sheet.write(irow, 2, ipupil.first_name, first_name1)

        sheet.write(irow, 3, ipupil.birthday.strftime('%d/%m/%Y'), h)
        sheet.write(irow, 4, TK.hk_thang_9, h)
        sheet.write(irow, 5, TK.hk_thang_10, h)
        sheet.write(irow, 6, TK.hk_thang_11, h)
        sheet.write(irow, 7, TK.hk_thang_12, h)
        sheet.write(irow, 8, TK.hk_thang_1, h)
        sheet.write(irow, 9, TK.hk_thang_2, h)
        sheet.write(irow, 10, TK.hk_thang_3, h)
        sheet.write(irow, 11, TK.hk_thang_4, h)
        sheet.write(irow, 12, TK.hk_thang_5, h)
        sheet.write(irow, 13, TK.term1, h)
        sheet.write(irow, 14, TK.term2, h)
        sheet.write(irow, 15, TK.year, h)

        irow += 1
        #return HttpResponse
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=hanh_kiem.xls'
    book.save(response)
    return response

@need_login
@require_POST
@school_function
@operating_permission([u'GIAO_VU', u'GIAO_VIEN', u'HIEU_PHO', u'HIEU_TRUONG'])
def import_hanh_kiem(request, class_id):
    if request.is_ajax():
        try:
            file = request.FILES.get('files[]')
        except KeyError:
            return HttpResponseBadRequest("AJAX request not valid")
    else:
        if len(request.FILES) == 1:
            file = request.FILES.values()[0]
        else:
            raise Exception("BadUpload")
    filename = save_file(request.FILES.get('files[]'), request.session)
    result, process_file_message = process_file_hanh_kiem(request, filename, class_id)

    if 'error' in result:
        success = False
        message = result['error']
        data = [{'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'success': success,
                 'message': message,
                 'process_message': process_file_message,
                 'error': u'File excel không đúng định dạng'}]

    else:
        data = [{'name': file.name,
                 'url': reverse('user_upload', args=[filename]),
                 'sizef': file.size,
                 'process_message': process_file_message,
                 'message': u'Nhập dữ liệu thành công'}]
    return HttpResponse(simplejson.dumps(data))

def process_file_hanh_kiem(request, file_name, class_id):
    filepath = os.path.join(settings.TEMP_FILE_LOCATION, file_name)

    if not os.path.isfile(filepath):
        raise NameError, "%s is not a valid filename" % file_name
    try:
        book = xlrd.open_workbook(filepath)
        sheet = book.sheet_by_index(0)
    except Exception as e:
        print e
        return {'error': u'File tải lên không phải file Excel'}, u'File tải lên không phải file Excel'
    start_col = -1
    start_row = -1
    year = get_current_year(request)
    try:
        for c in range(0, sheet.ncols):
            flag = False
            for r in range(0, sheet.nrows):
                if sheet.cell_value(r, c) == u'STT':
                    start_col = c
                    start_row = r
                    flag = True
                    break
            if flag: break
    except Exception as e:
        print e
        return {'error': u'File tải lên không phải file Excel'}, u'File tải lên không phải file Excel'
    print '22222'
    if start_col == -1:
        return {'error': u'File tải lên phải có cột "STT".'}, u'File tải lên phải có cột "STT".'
    cl = Class.objects.get(id=class_id)
    message = u'<ul>'

    for r in range(start_row+1, sheet.nrows):
        try:
            p_last_name = sheet.cell_value(r, 1).strip()
            p_first_name = sheet.cell_value(r, 2).strip()
            if len(p_last_name.strip()) == 0 and len(p_first_name.strip()) == 0:
                message += u'<ul>Họ và tên ở hàng thứ ' + str(r) + u' bị trống</ul>'
                continue

            try:
                p = cl.pupil_set.get(first_name__exact = p_first_name, last_name__exact = p_last_name)
                print p
            except Exception as ex:
                message += u'<ul>Không tồn tại học sinh ' + unicode(p_last_name + p_first_name) + u' </ul>'
                continue

            TK = p.tbnam_set.get(year_id__exact=year.id)
            attr_list = {4: 'hk_thang_9', 5: 'hk_thang_10', 6: 'hk_thang_11', 7: 'hk_thang_12', 8: 'hk_thang_1', 9: 'hk_thang_2', 10: 'hk_thang_3', 11: 'hk_thang_4', 12: 'hk_thang_5', 13: 'term1', 14: 'term2', 15: 'year'}

            for num, attr in attr_list.iteritems():
                try:
                    setattr(TK, attr, sheet.cell_value(r, num).strip())
                except Exception as ex:
                    message += u'<ul>Gía trị tại ô ' + str(r) + u' ' + str(num) + u' không hợp lệ</ul>'
            TK.save()
        except Exception as e:
            print str(e)
            return {'error': u'File tải lên không phải file Excel'}, message


    message += u'</ul>'
    result = {'Thành công': u'Dữ liệu được tải thành công'}
    return result, message


@need_login
@school_function
def export_gvcn_list(request):
    year = get_current_year(request)
    school = get_school(request)
    classes = year.class_set.order_by('block_id__number','name')
    book = Workbook(encoding='utf-8')

    sheet = book.add_sheet('GVCN')
    width = (A4_WIDTH - STT_WIDTH - 2 * LASTNAME_WIDTH - FIRSTNAME_WIDTH-BIRTHDAY_WIDTH)/4
    sheet.col(0).width = STT_WIDTH
    sheet.col(1).width = LASTNAME_WIDTH
    sheet.col(2).width = width
    sheet.col(3).width = LASTNAME_WIDTH
    sheet.col(4).width = FIRSTNAME_WIDTH
    sheet.col(5).width = BIRTHDAY_WIDTH
    sheet.col(6).width = width
    sheet.col(7).width = width
    sheet.col(8).width = width

    #title
    printHeader(sheet,0,0,school,3)
    printCongHoa(sheet,0,3,6)
    sheet.write_merge(4, 4, 0, 8, u'DANH SÁCH GIÁO VIÊN CHỦ NHIỆM', h9)
    sheet.write_merge(5, 5, 0, 8, u'NĂM HỌC ' +unicode(year), h9)

    irow = 7
    sheet.write(irow, 0, 'STT', h4)
    sheet.write(irow, 1, u'Lớp', h4)
    sheet.write(irow, 2, u'Sĩ số', h4)
    sheet.write_merge(irow,irow,3,4, u'Giáo viên chủ nhiệm', h4)
    sheet.write(irow, 5, u'Ngày sinh', h4)
    sheet.write_merge(irow,irow,6,8, u'Ghi chú', h4)
    irow+=1
    for cl in classes:
        sheet.write(irow, 0, irow - 7, h6)
        sheet.write(irow, 1, unicode(cl), h6)
        sheet.write(irow, 2, cl.number_of_pupils(), h6)
        if cl.teacher_id != None:
            sheet.write(irow, 3, unicode(cl.teacher_id.last_name), last_name)
            sheet.write(irow, 4, unicode(cl.teacher_id.first_name), first_name)
            if cl.teacher_id.birthday != None:
                sheet.write(irow, 5, unicode(cl.teacher_id.birthday.strftime('%d/%m/%Y')), h6)
            else:
                sheet.write(irow, 5,"", h6)
        else:
            sheet.write(irow, 3, "", last_name)
            sheet.write(irow, 4, "", first_name)
            sheet.write(irow, 5, "", h6)
        sheet.write_merge(irow,irow,6,8, "", h6)

        irow += 1
        #return HttpResponse
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=danh_sach_gvcn.xls'
    book.save(response)
    return response
