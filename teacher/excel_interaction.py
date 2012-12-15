# -*- coding: utf-8 -*-
__author__ = 'Admin'
import xlrd
from xlrd.formula import cellname
from school.templateExcel import *
import os
import settings
from datetime import date
from validations import phone as validate_phone
from teacher.utils import to_date, to_en1
from django.http import HttpResponse
from teacher.models import Note
from xlwt.Workbook import Workbook

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
        c_cho_o_ht = -1
        c_ten_bo = -1
        c_ten_me = -1
        c_so_dt_bo = -1
        c_so_dt_me = -1
        c_so_dt_nt = -1
        number = 0
        number_ok = 0
        for c in range(0, sheet.ncols):
            value = sheet.cell_value(start_row, c).strip()
            if unicode(value).lower() == u'họ và tên':
                c_ten = c
            elif value == u'Ngày sinh':
                c_ngay_sinh = c
            elif value == u'Giới tính':
                c_gioi_tinh = c
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
            elif value == u'Số nhắn tin' or value == u'Số điện thoại nhắn tin':
                c_so_dt_nt = c
        for r in range(start_row + 1, sheet.nrows):
            gt = 'Nam'
            cho_o_ht = ''
            ten_bo = ''
            dt_bo = ''
            ten_me = ''
            dt_me = ''
            sms_phone = ''
            name = sheet.cell(r, c_ten).value.strip()
            temp = []
            for i in name.split(' '):
                if i: temp.append(i)
            name = ' '.join(temp)
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
                if not gt in [u'Nam', u'Nữ']: gt = 'Nam'
            if c_cho_o_ht > -1:
                cho_o_ht = sheet.cell(r, c_cho_o_ht).value.strip()
            if c_ten_bo > -1:
                ten_bo = normalize(sheet.cell(r, c_ten_bo).value)
            if c_so_dt_bo > -1:
                dt_bo = sheet.cell(r, c_so_dt_bo).value
                if dt_bo and (type(dt_bo)!= unicode or type(dt_bo)!=str):
                    dt_bo = unicode(int(dt_bo)).strip()
                if dt_bo and dt_bo[0] != '0' and dt_bo[0] != '+' and not dt_bo.startswith('84'): dt_bo = '0' + dt_bo
            if c_ten_me > -1:
                ten_me = normalize(sheet.cell(r, c_ten_me).value)
            if c_so_dt_me > -1:
                dt_me = sheet.cell(r, c_so_dt_me).value
                if dt_me and (type(dt_me)!= unicode or type(dt_me)!=str):
                    dt_me = unicode(int(dt_me)).strip()
                if dt_me and dt_me[0] != '0' and dt_me[0] != '+' and not dt_me.startswith('84'): dt_me = '0' + dt_me
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
                    'current_address': cho_o_ht,
                    'father_name': ten_bo,
                    'father_phone': dt_bo,
                    'mother_name': ten_me,
                    'mother_phone': dt_me,
                    'sms_phone': sms_phone}
            student_list.append(data)
            number_ok += 1
        message += u'</ul>'
        return student_list, message, number, number_ok

def student_export(cl):
    student_list = cl.students()
    student_id = [student.id for student in student_list]
    notes = Note.objects.filter(class_id__id = cl.id, student_id__id__in = student_id)
    notes_content = {}
    if len(notes):
        for note in notes:
            notes_content[note.class_id.id] = note.note
    book = Workbook(encoding='utf-8')
    #renderring xls file
    sheet = book.add_sheet(u'Danh sách học sinh')
    sheet.write_merge(0, 1,3,6, u'DANH SÁCH HỌC SINH LỚP %s' % unicode(cl).upper(), h40)
    sheet.row(0).height = 350

    sheet.col(0).width = 1500
    sheet.col(1).width = 7000
    sheet.col(2).width = 4500
    sheet.col(3).width = 3000
    sheet.col(4).width = 7000
    sheet.col(5).width = 4500
    sheet.col(6).width = 7000
    sheet.col(7).width = 4500
    sheet.col(8).width = 7000
    sheet.col(9).width = 4500
    sheet.col(10).width = 10000
    sheet.row(4).height = 350

    sheet.write(4, 0, u'STT',h4)
    sheet.write(4, 1, u'Họ và tên', h4)
    sheet.write(4, 2, u'Ngày sinh', h4)
    sheet.write(4, 3, u'Giới tính',h4)
    sheet.write(4, 4, u'Chỗ ở hiện tại', h4)
    sheet.write(4, 5, u'Số điện thoại nhắn tin',h4)
    sheet.write(4, 6, u'Họ tên bố',h4)
    sheet.write(4, 7, u'Số điện thoại của bố',h4)
    sheet.write(4, 8, u'Họ tên mẹ',h4)
    sheet.write(4, 9, u'Số điện thoại của mẹ',h4)
    sheet.write(4, 10, u'Ghi chú', h4)
    row = 5
    for student in student_list:
        sheet.row(row).height = 350
        sheet.write(row, 0, row - 4, h7)
        sheet.write(row, 1, student.last_name + ' ' + student.first_name, h7)
        sheet.write(row, 2, student.birthday.strftime('%d/%m/%Y'), h7)
        sheet.write(row, 3, student.sex, h7)
        sheet.write(row, 4, student.current_address, h7)
        sheet.write(row, 5, student.sms_phone, h7)
        sheet.write(row, 6, student.father_name, h7)
        sheet.write(row, 7, student.father_phone, h7)
        sheet.write(row, 8, student.mother_name, h7)
        sheet.write(row, 9, student.mother_phone, h7)
        if student.id in notes_content:
            sheet.write(row, 10, notes_content[student.id], h7)
        else:
            sheet.write(row, 10, "", h7)
        row += 1
    return book