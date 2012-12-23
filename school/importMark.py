# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import transaction
from excel_interaction import save_file
from django.utils import simplejson
import xlrd
from xlrd import cellname
import os.path
import time
import datetime
from decorators import need_login
from school.models import Subject, Term, Mark, Pupil, TKMon
from school.templateExcel import MAX_COL, CHECKED_DATE
from school.utils import convertCharToDigit, in_school, get_position
import settings

LOCK_MARK = False
ENABLE_CHANGE_MARK = True

def validate(s, isNx):
    x = 11
    y = 4
    if isNx == False:
        for i in range(x, s.nrows):
            for j in range(4, s.ncols):
                try:
                    value = unicode(s.cell(i, j).value)
                    value = value.replace(' ', '')
                    value = value.replace(',', '.')
                    if len(value) != 0:
                        value1 = float(value)
                        if (value1 < 0) | (value1 > 10):
                            return  u'Điểm ở ô ' + cellname(i, j) + u' không nằm trong [0,10] '

                except Exception as e:
                #    print "aaaaaa"
                    return u'Điểm ở ô ' + cellname(i, j) + u' không hợp lệ'
    else:
        for i in range(x, s.nrows):
            for j in range(4, s.ncols):
                try:
                    value = unicode(s.cell(i, j).value)
                    value = value.replace(' ', '').lower()
                    if len(value) != 0:
                        if (value != u'đ') & (value != u'cđ') & (value != u'd') & (value != u'cd'):
                            return  u'Lỗi ở ô ' + cellname(i, j) + u'. Chỉ dùng các kí tự sau để cho điểm D,Đ,CD,CĐ.'

                except Exception as e:
                #    print e
                    return u'Lỗi ở ô ' + cellname(i, j) + u'. Chỉ dùng các kí tự sau để cho điểm D,Đ,CD,CĐ.'

    return ''


def getNumberCol(s):
    x = 10
    y = 4
    colMieng = 0
    col15Phut = 0
    colMotTiet = 0
    while colMieng + 1 == int(s.cell(x, y).value):
        colMieng += 1
        y += 1
    while col15Phut + 1 == int(s.cell(x, y).value):
        col15Phut += 1
        y += 1
    try:
        while colMotTiet + 1 == int(s.cell(x, y).value):
            colMotTiet += 1
            y += 1
    except Exception as e:
        print e
    return colMieng, col15Phut, colMotTiet


def isDifference(x, y):
    try:
        if  (x == "") and (y == ""):
            return False
        elif (x != "") and (y != ""):
            if (float(x) == float(y)):
                return False
    except Exception as e:
        return True
    return True


def process(s, x, y, mark, time, timeNow, timeToEdit, position, isNx, diffMessage):
    value = unicode(s.cell(x, y).value)
    value = value.replace(' ', '')
    value = value.replace(',', '.')
    if (len(value) == 0):
        return '', None, ""
    if isNx:
        value = convertCharToDigit(value)

    if (time != "") & (time != None ) & (position != 4):
        if (timeNow - int(time)) > timeToEdit:
            if isDifference(value, mark):
                return u" Ô " + cellname(x, y) + u' không được sửa điểm.'

    if isDifference(value, mark):
        if time != "":
            diffMessage[0] += cellname(x, y) + ' '
        return '', float(value), str(timeNow)
    else:
        return '', float(value), str(time)


def excelToArray(s, x, y, colMieng, col15Phut, colMotTiet, arrMark, arrTime, timeNow, timeToEdit, position, isNx,
                 diffMessage):
    lengthCol = [colMieng, col15Phut, colMotTiet]
    for t in range(3):
        for i in range(lengthCol[t]):
            value = unicode(s.cell(x, y + i).value)
            value = value.replace(' ', '')
            value = value.replace(',', '.')
            if isNx:
                value = convertCharToDigit(value)
            if (isDifference(value, arrMark[t * MAX_COL + i + 1])) & (arrTime[t * MAX_COL + i + 1] != ''):
                diffMessage[0] += cellname(x, y + i) + ' '

            if ((arrTime[t * MAX_COL + i + 1] != '') & (position != 4)):
                if (timeNow - int(arrTime[t * MAX_COL + i + 1])) > timeToEdit:
                    if isDifference(value, arrMark[t * MAX_COL + i + 1]):
                        return u" Ô " + cellname(x, y + i) + u' không được sửa điểm.'

            if (value == ""):
                arrTime[t * MAX_COL + i + 1] = ""
            elif isDifference(value, arrMark[t * MAX_COL + i + 1]):
                arrTime[t * MAX_COL + i + 1] = str(timeNow)
            arrMark[t * MAX_COL + i + 1] = value
        y += lengthCol[t]
    return ""


@transaction.commit_on_success
@need_login
def importMark(request, term_id, subject_id, checkDiff=1):
    print request.session.session_key
    user = request.user
    selectedSubject = Subject.objects.get(id=subject_id)

    try:
        if in_school(request, selectedSubject.class_id.year_id.school_id) == False:
            return HttpResponseRedirect('/school')

    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    position = get_position(request)
    if position == 4:
        pass
    elif position == 3:
        if (selectedSubject.teacher_id.id != request.user.teacher.id):
            return HttpResponseRedirect('/school')
    else:
        return HttpResponseRedirect('/school')
    t1 = time.time()
    absentMessage = ''
    editMarkMessage = ''
    diffMessage = ['']
    message = u'Lỗi'
    numberOk = 0
    if checkDiff == '0':
        message = request.session['message_mark']
        name = subject_id + "import_mark"
        markList = request.session[name]
        for m in markList:
            m.save()

        data = simplejson.dumps({'message': message})
        return HttpResponse(data, mimetype='json')

    timeToEdit = int(selectedSubject.class_id.year_id.school_id.get_setting('lock_time')) * 60
    timeNow = int((datetime.datetime.now() - CHECKED_DATE).total_seconds() / 60)
    selectedTerm = Term.objects.get(id=term_id)
    if request.method == 'POST':
        filename = save_file(request.FILES.get('files[]'), request.session)
        filepath = os.path.join(settings.TEMP_FILE_LOCATION, filename)
        book = xlrd.open_workbook(filepath)
        s = book.sheet_by_index(0)
        validateMessage = validate(s, selectedSubject.nx)
        colMieng, col15Phut, colMotTiet = getNumberCol(s)
        isNx = selectedSubject.nx
        if validateMessage == '':
            markList = Mark.objects.filter(subject_id=subject_id, term_id=term_id, current=True).order_by(
                'student_id__index', 'student_id__first_name', 'student_id__last_name', 'student_id__birthday')
            pupilList = Pupil.objects.filter(classes=selectedSubject.class_id, attend__is_member=True).order_by('index',
                'first_name', 'last_name', 'birthday').distinct()
            if (isNx & (selectedTerm.number == 2)):
                tkMonList = TKMon.objects.filter(subject_id=subject_id, current=True).order_by('student_id__index',
                    'student_id__first_name', 'student_id__last_name', 'student_id__birthday')
            x = 11
            y = 0
            list = zip(pupilList, markList)
            for p, m in list:
                pass

            for i in range(x, s.nrows):
                lastName = s.cell(i, y + 1).value
                firstName = s.cell(i, y + 2).value
                birthday = s.cell(i, y + 3).value

                #p=pupilList.filter()
                ok = False
                for p, m in list:
                    if (p.last_name == lastName) & (p.first_name == firstName) & (
                    p.birthday.strftime('%d/%m/%Y') == birthday):
                        ok = True
                        arrMark = m.toArrayMark()
                        arrTime = m.toArrayTime()
                        editMarkMessage = excelToArray(s, i, y + 4, colMieng, col15Phut, colMotTiet, arrMark, arrTime,
                            timeNow, timeToEdit, position, isNx, diffMessage)
                        if editMarkMessage != "": break;

                        editMarkMessage, m.ck, arrTime[3 * MAX_COL + 1] = process(s, i,
                            y + colMieng + col15Phut + colMotTiet + 4, m.ck, arrTime[3 * MAX_COL + 1], timeNow,
                            timeToEdit, position, isNx, diffMessage)

                        if editMarkMessage != '': break
                        if isNx:
                            if selectedTerm.number == 1:
                                editMarkMessage, m.tb, arrTime[3 * MAX_COL + 2] = process(s, i,
                                    y + colMieng + col15Phut + colMotTiet + 5, m.tb, arrTime[3 * MAX_COL + 2], timeNow,
                                    timeToEdit, position, isNx, diffMessage)
                            else:
                                editMarkMessage, m.tb, arrTime[3 * MAX_COL + 2] = process(s, i,
                                    y + colMieng + col15Phut + colMotTiet + 6, m.tb, arrTime[3 * MAX_COL + 2], timeNow,
                                    timeToEdit, position, isNx, diffMessage)
                                for p, tkMon in zip(pupilList, tkMonList):
                                    if (p.last_name == lastName) & (p.first_name == firstName) & (
                                    p.birthday.strftime('%d/%m/%Y') == birthday):
                                        editMarkMessage, tkMon.tb_nam, tempTime = process(s, i,
                                            y + colMieng + col15Phut + colMotTiet + 7, tkMon.tb_nam, tkMon.time, timeNow
                                            , timeToEdit, position, isNx, diffMessage)
                                        if (tempTime == "") | (tempTime == "None"):
                                            tkMon.time = None
                                        else:
                                            tkMon.time = int(tempTime)
                                        tkMon.save()
                                        break

                        m.saveMark(arrMark)
                        m.saveTime(arrTime)
                        break

                if (editMarkMessage != ''): break
                if not ok:
                    absentMessage += '<tr>' + u'<td>' + lastName + ' ' + firstName + u'</td>' + u'<td>' + unicode(
                        birthday) + u'</td>' + '</tr>'
                else:
                    numberOk += 1

            if (editMarkMessage == ''):
                if numberOk == len(markList):
                    message = "Đã nhập thành công cả lớp"
                else:
                    message = "Đã nhập được " + str(numberOk) + "/" + str(len(markList)) + " học sinh."

            if (editMarkMessage == '') &\
               ((checkDiff == 0) | ((checkDiff == 1) & (diffMessage[0] == ''))):
                for m in markList:
                    m.save()
            elif (editMarkMessage == ''):
                name = subject_id + "import_mark"
                request.session[name] = markList
                request.session['message_mark'] = message
    temp = diffMessage[0].split(' ')
    numberDiff = len(temp) - 1
    diffMessage[0] = ''
    for x in range(min(30, numberDiff)):
        diffMessage[0] += temp[x] + ' '
    if numberDiff > 100:
        diffMessage[0] += "..."
    file = request.FILES.values()[0]
    t2 = time.time()
    print (t2 - t1)
    data = [{"absentMessage": absentMessage,
             'validateMessage': validateMessage,
             'editMarkMessage': editMarkMessage,
             'diffMessage': diffMessage,
             'numberDiff': numberDiff,
             'checkDiff': checkDiff,
             'message': message,
             'name': file.name,
             'url': reverse('user_upload', args=[filename]),
             }]
    #print (t2-t1)

    return HttpResponse(simplejson.dumps(data))

