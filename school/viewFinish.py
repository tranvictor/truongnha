# author: luulethe@gmail.com 

# -*- coding: utf-8 -*-
import time
import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.db import transaction
from django.utils import simplejson
import os.path
from school.models import TBNam, TBHocKy, TKDiemDanh, Class, Term, DiemDanh, Subject, Mark, Year, TKMon, Pupil
from decorators import need_login
from school.templateExcel import convertMarkToCharacter1, convertMarkToCharacter
from school.utils import in_school, get_current_term, get_position, get_level, get_current_year, get_school, to_en1,\
    convertHlToVietnamese, convertHkToVietnamese, convertDanhHieu
from school.viewCount import countDanhHieuInYear, countTotalLearningInYear, countTotalPractisingInYear,\
    countDanhHieuInTerm, countTotalLearningInTerm, countTotalPractisingInTerm
from sms.utils import sendSMS

ENABLE_CHANGE_MARK = True
e = 0.00000001

@need_login
def finish(request, active_term=0, term_number=None, year_number=None, is_calculate=0):
    user = request.user
    current_term = get_current_term(request)
    try:
        if in_school(request, current_term.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request) == 'T' ):
        return HttpResponseRedirect('/school')

    message = None
    if int(active_term) != 0:
        request.user.userprofile.organization.status = int(active_term)
        request.user.userprofile.organization.save()
        #year  = Year.objects.filter(school_id = request.user.userprofile.organization, time = term[1])
    if (term_number != None) & (is_calculate == '1'):
        if int(term_number) < 3:
            term = Term.objects.get(year_id__school_id=request.user.userprofile.organization, year_id__time=year_number,
                number=term_number)
            finishTermInSchool(term.id)
            message = "Đã tính tổng kết xong. Mời bạn xem kết quả phía dưới."
        else:
            year = Year.objects.get(school_id=request.user.userprofile.organization, time=year_number)
            finishYearInSchool(year.id)
            message = "Đã tính tổng kết xong. Mời bạn xem kết quả phía dưới."

    current_term = get_current_term(request)
    #year_list = Year.objects.filter(school_id = request.user.userprofile.organization).order_by("time")
    list = []
    if term_number == None:
        current_year = get_current_year(request)
    else:
        current_year = Year.objects.get(school_id=request.user.userprofile.organization, time=year_number)

    term1 = Term.objects.get(year_id=current_year, number=1)
    term2 = Term.objects.get(year_id=current_year, number=2)
    number_pupil = TBNam.objects.filter(year_id=current_year, student_id__disable=False).count()
    # get term 1
    finish_learning1, not_finish_learning1, finish_practising1, not_finish_practising1, finish_all1, not_finish_all1 = countDetailTerm(
        term1.id)
    number_finish_learning1 = number_pupil - TBHocKy.objects.filter(term_id=term1, student_id__disable=False,
        hl_hk=None).count()
    number_finish_practising1 = number_pupil - TBNam.objects.filter(year_id=current_year, student_id__disable=False,
        term1=None).count()
    number_finish_title1 = number_pupil - TBHocKy.objects.filter(term_id=term1, student_id__disable=False,
        danh_hieu_hk=None).count()

    list.append((number_finish_learning1, number_finish_practising1, number_finish_title1, not_finish_learning1,
                 not_finish_practising1, not_finish_all1))

    # get term 2
    finish_learning2, not_finish_learning2, finish_practising2, not_finish_practising2, finish_all2, not_finish_all2 = countDetailTerm(
        term2.id)
    number_finish_learning2 = number_pupil - TBHocKy.objects.filter(term_id=term2, student_id__disable=False,
        hl_hk=None).count()
    number_finish_practising2 = number_pupil - TBNam.objects.filter(year_id=current_year, student_id__disable=False,
        term2=None).count()
    number_finish_title2 = number_pupil - TBHocKy.objects.filter(term_id=term2, student_id__disable=False,
        danh_hieu_hk=None).count()
    list.append((number_finish_learning2, number_finish_practising2, number_finish_title2, not_finish_learning2,
                 not_finish_practising2, not_finish_all2))
    #get year
    finish_learning3, not_finish_learning3, finish_practising3, not_finish_practising3, finish_all3, not_finish_all3 = countDetailYear(
        current_year.id)
    number_finish_learning3 = number_pupil - TBNam.objects.filter(year_id=current_year, student_id__disable=False,
        hl_nam=None).count()
    number_finish_practising3 = number_pupil - TBNam.objects.filter(year_id=current_year, student_id__disable=False,
        year=None).count()
    number_finish_title3 = number_pupil - TBNam.objects.filter(year_id=current_year, student_id__disable=False,
        danh_hieu_nam=None).count()

    list.append((number_finish_learning3, number_finish_practising3, number_finish_title3, not_finish_learning3,
                 not_finish_practising3, not_finish_all3))
    school = get_school(request)
    grades = school.block_set.all()
    cy_time = datetime.datetime.now().year
    t = loader.get_template(os.path.join('school/finish', 'finish.html'))
    c = RequestContext(request, {'message': message,
                                 'current_term': current_term,
                                 'number_pupil': number_pupil,
                                 'list': list,
                                 'grades': grades,
                                 'school': school,
                                 'year': current_year,
                                 'year_time': cy_time,
                                 #'year_list':year_list,
    }
    )
    return HttpResponse(t.render(c))

# tinh diem tong ket cho 1 lop theo hoc ky
def defineHl(tb, monChuyen, monToan, monVan, minMark, minComment):
    if monToan < monVan:
        firstMark = monVan + e
    else:
        firstMark = monToan + e
    if monChuyen == None:
        monChuyen = 10
    type = None
    if  (tb >= 8.0) & (firstMark >= 8.0) & (monChuyen >= 8) & (minMark >= 6.5) & (minComment >= 5):
        type = 'G'
    elif (tb >= 6.5) & (firstMark >= 6.5) & (monChuyen >= 6.5) & (minMark >= 5) & (minComment >= 5):
        type = 'K'
    elif (tb >= 5) & (firstMark >= 5) & (monChuyen >= 5) & (minMark >= 3.5) & (minComment >= 5):
        type = 'TB'
    elif (tb >= 3.5) & (minMark >= 2):
        type = 'Y'
    else:
        type = 'Kem'
    if   (tb >= 8) & (type == 'TB'):
        type = 'K'
    elif (tb >= 8) & (type == 'Y'):
        type = 'TB'
    elif (tb >= 6.5) & (type == 'Y'):
        type = 'TB'
    elif (tb >= 6.5) & (type == 'Kem'):
        type = 'Y'
    return type

#tinh diem tong ket cua mot lop theo hoc ky
#def overallForAStudentInTerm(markList,tbHocKy,vtMonChuyen,vtMonToan,vtMonVan):
@transaction.commit_on_success
def calculateOverallMarkTerm(class_id, termNumber):
    selectedClass = Class.objects.get(id=class_id)
    selectedTerm = Term.objects.get(year_id=selectedClass.year_id, number=termNumber)
    ddhkList = TKDiemDanh.objects.filter(student_id__classes=class_id, term_id=selectedTerm,
        student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
        'student_id__last_name', 'student_id__birthday').distinct()
    for ddhk in ddhkList:
        ddhk.co_phep = DiemDanh.objects.filter(student_id=ddhk.student_id, term_id=selectedTerm, loai='P').count()
        ddhk.khong_phep = DiemDanh.objects.filter(student_id=ddhk.student_id, term_id=selectedTerm, loai='K').count()
        ddhk.tong_so = ddhk.co_phep + ddhk.khong_phep
        ddhk.save()

    pupilNoSum = 0
    subjectList = Subject.objects.filter(class_id=class_id, primary__in=[0, termNumber]).order_by('index', 'name')
    markList = Mark.objects.filter(subject_id__class_id=class_id, term_id=selectedTerm, current=True,
        subject_id__primary__in=[0, termNumber]).order_by('student_id__index', 'student_id__first_name',
        'student_id__last_name', 'student_id__birthday', 'subject_id__index', 'subject_id__name')
    tbHocKyList = TBHocKy.objects.filter(student_id__classes=class_id, term_id=selectedTerm,
        student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
        'student_id__last_name', 'student_id__birthday').distinct()
    hkList = TBNam.objects.filter(year_id=selectedClass.year_id, student_id__classes=class_id,
        student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
        'student_id__last_name', 'student_id__birthday').distinct()
    length = len(subjectList)
    i = 0
    vtMonChuyen = -1
    checkComment = [0] * len(subjectList)
    for s in subjectList:
        if s.hs == 3:  vtMonChuyen = i

        if    s.name.lower().__contains__(u'toán'):
            vtMonToan = i
        elif  s.name.lower().__contains__(u'văn'):
            vtMonVan = i
        if s.nx:
            checkComment[i] = 1
        i += 1
    i = 0
    j = 0
    # cam xoa dong nay
    for tt in tbHocKyList:
        pass

    for m in markList:
        #print i
        t = i % length
        if t == 0:
            ok = True
            monChuyen = None
            monToan = None
            monVan = None
            minMark = 10
            minComment = 10
            markSum = 0
            factorSum = 0
            tbHocKy = tbHocKyList[j]
            j += 1

        if t == vtMonChuyen:
            monChuyen = m.tb
        if   t == vtMonToan:
            monToan = m.tb
        elif t == vtMonVan:
            monVan = m.tb
        if (m.tb != None):
            if m.mg == False:
                if checkComment[t] == 0:
                    markSum += m.tb * subjectList[t].hs
                    factorSum += subjectList[t].hs
                    if m.tb < minMark:
                        minMark = m.tb
                elif m.tb < minComment:
                    minComment = m.tb

        else:
            if m.mg == False:
                ok = False
        if (t == length - 1):
            if  ok:
                if factorSum == 0:
                    tbHocKy.tb_hk = None
                    tbHocKy.hl_hk = None
                    pupilNoSum += 1
                else:
                    tbHocKy.tb_hk = round(markSum / factorSum + e, 1)
                    tbHocKy.hl_hk = defineHl(tbHocKy.tb_hk + e, monChuyen, monToan, monVan, minMark + e, minComment + e)
            else:
                tbHocKy.tb_hk = None
                tbHocKy.hl_hk = None
                pupilNoSum += 1

                #tbHocKy.save()
        i += 1
    NN2List = Mark.objects.filter(subject_id__class_id=class_id, term_id__number=termNumber, subject_id__primary=3,
        current=True).order_by('student_id__index', 'student_id__first_name', 'student_id__last_name',
        'student_id__birthday')
    if len(NN2List) > 0:
        for nn2, tbHocKy in zip(NN2List, tbHocKyList):
            if (nn2.tb is not None) & (tbHocKy.tb_hk is not None):
                if    nn2.tb + e >= 8: tbHocKy.tb_hk += 0.3
                elif  nn2.tb + e >= 6.5: tbHocKy.tb_hk += 0.2
                elif  nn2.tb + e >= 5: tbHocKy.tb_hk += 0.1

    for hk in hkList:
        pass

    noHanhKiem = 0
    for hk, tbHocKy in zip(hkList, tbHocKyList):
        if termNumber == 1: loaiHk = hk.term1
        else: loaiHk = hk.term2

        if loaiHk == None: noHanhKiem += 1
        if (loaiHk == None) | (tbHocKy.hl_hk == None):
            tbHocKy.danh_hieu_hk = None
        elif (loaiHk == 'T') & (tbHocKy.hl_hk == 'G'):
            tbHocKy.danh_hieu_hk = 'G'
        elif ((loaiHk == 'T') | (loaiHk == 'K')) & ((tbHocKy.hl_hk == 'G') | (tbHocKy.hl_hk == 'K')):
            tbHocKy.danh_hieu_hk = 'TT'
        else: tbHocKy.danh_hieu_hk = 'K'

    for tb in tbHocKyList:
        tb.save()

    return pupilNoSum, noHanhKiem


@transaction.commit_on_success
def calculateTKMon(class_id):
    cnList = TKMon.objects.filter(subject_id__class_id=class_id, subject_id__primary=1, current=True).order_by(
        'student_id__index', 'student_id__first_name', 'student_id__last_name', 'student_id__birthday',
        'subject_id__index', 'subject_id__name')
    hk1List = Mark.objects.filter(subject_id__class_id=class_id, term_id__number=1, subject_id__primary=1,
        current=True).order_by('student_id__index', 'student_id__first_name', 'student_id__last_name',
        'student_id__birthday', 'subject_id__index', 'subject_id__name')

    #print cnList
    for hk1, cn in zip(hk1List, cnList):
        cn.tb_nam = hk1.tb

    cn1List = TKMon.objects.filter(subject_id__class_id=class_id, subject_id__primary=2, current=True).order_by(
        'student_id__index', 'student_id__first_name', 'student_id__last_name', 'student_id__birthday',
        'subject_id__index', 'subject_id__name')
    hk2List = Mark.objects.filter(subject_id__class_id=class_id, term_id__number=2, subject_id__primary=2,
        current=True).order_by('student_id__index', 'student_id__first_name', 'student_id__last_name',
        'student_id__birthday', 'subject_id__index', 'subject_id__name')

    #print cn1List
    for hk2, cn in zip(hk2List, cn1List):
        cn.tb_nam = hk2.tb

    for cn in cnList:
        cn.save()

    for cn in cn1List:
        cn.save()

    mgList = Mark.objects.filter(subject_id__class_id=class_id, mg=True, current=True).order_by('student_id__index',
        'student_id__first_name', 'student_id__last_name', 'student_id__birthday', 'subject_id__index',
        'subject_id__name')

    for m in mgList:
        anotherMark = Mark.objects.get(subject_id=m.subject_id, student_id=m.student_id,
            term_id__number=3 - m.term_id.number)
        if not anotherMark.mg:
            tbcn = TKMon.objects.get(subject_id=m.subject_id, student_id=m.student_id)
            tbcn.tb_nam = anotherMark.tb
            tbcn.save()


@transaction.commit_on_success
def calculateOverallMarkYear(class_id=7):
    selected_class = Class.objects.get(id=class_id)
    selected_year = selected_class.year_id
    pupilNoSum = 0
    subjectList = Subject.objects.filter(class_id=class_id, primary__in=[0, 1, 2]).order_by("index", 'name')
    markList = TKMon.objects.filter(subject_id__class_id=class_id, subject_id__primary__in=[0, 1, 2],
        current=True).order_by('student_id__index', 'student_id__first_name', 'student_id__last_name',
        'student_id__birthday', 'subject_id__index', 'subject_id__name')
    tbNamList = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id,
        student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
        'student_id__last_name', 'student_id__birthday').distinct()
    #calculateTKMon(class_id)

    length = len(subjectList)
    i = 0
    vtMonChuyen = -1
    checkComment = [0] * len(subjectList)
    for s in subjectList:
        if s.hs == 3:  vtMonChuyen = i

        if    s.name.lower().__contains__(u'toán'):
            vtMonToan = i
        elif  s.name.lower().__contains__(u'văn'):
            vtMonVan = i
        if s.nx:
            checkComment[i] = 1
        i += 1
    i = 0
    j = 0
    # cam xoa dong nay
    for t in tbNamList:
        pass
    for m in markList:
        t = i % length
        if t == 0:
            ok = True
            monChuyen = None
            monToan = None
            monVan = None
            minMark = 10
            minComment = 10
            markSum = 0
            factorSum = 0
            tbNam = tbNamList[j]
            j += 1

        if t == vtMonChuyen:
            monChuyen = m.tb_nam

        if   t == vtMonToan:
            monToan = m.tb_nam
        elif t == vtMonVan:
            monVan = m.tb_nam

        if m.tb_nam != None:
            if m.mg == False:
                if checkComment[t] == False:
                    markSum += m.tb_nam * subjectList[t].hs
                    factorSum += subjectList[t].hs
                    if m.tb_nam < minMark:
                        minMark = m.tb_nam

                elif minComment > m.tb_nam:
                    minComment = m.tb_nam
        else:
            if m.mg == False:
                ok = False
        if (t == length - 1):
            if  ok:
                if factorSum == 0:
                    tbNam.tb_nam = None
                    tbNam.hl_nam = None
                else:
                    tbNam.tb_nam = round(markSum / factorSum + e, 1)
                    tbNam.hl_nam = defineHl(tbNam.tb_nam + e, monChuyen, monToan, monVan, minMark + e, minComment + e)
            else:
                tbNam.tb_nam = None
                tbNam.hl_nam = None
                pupilNoSum += 1
        i += 1
    NN2List = TKMon.objects.filter(subject_id__class_id=class_id, subject_id__primary=3, current=True).order_by(
        'student_id__index', 'student_id__first_name', 'student_id__last_name', 'student_id__birthday',
        'subject_id__index', 'subject_id__name')

    if len(NN2List) > 0:
        for nn2, tbNam in zip(NN2List, tbNamList):
            if (nn2.tb_nam != None) & (tbNam.tb_nam != None):
                if  nn2.tb_nam + e >= 8: tbNam.tb_nam += 0.3
                elif  nn2.tb_nam + e >= 6.5: tbNam.tb_nam += 0.2
                elif  nn2.tb_nam + e >= 5: tbNam.tb_nam += 0.1

    noHanhKiem = 0
    for tbNam in tbNamList:
        loaiHk = tbNam.year

        if loaiHk == None: noHanhKiem += 1

        if (loaiHk == None) | (tbNam.hl_nam == None):
            tbNam.danh_hieu_nam = None
        elif (loaiHk == 'T') & (tbNam.hl_nam == 'G'):
            tbNam.danh_hieu_nam = 'G'
        elif ((loaiHk == 'T') | (loaiHk == 'K')) & ((tbNam.hl_nam == 'G') | (tbNam.hl_nam == 'K')):
            tbNam.danh_hieu_nam = 'TT'
        else: tbNam.danh_hieu_nam = 'K'

    for tb in tbNamList:
        tb.save()

    return pupilNoSum, noHanhKiem

# xep loai hoc ky cua mot lop

@need_login
def xepLoaiHlTheoLop(request, class_id, termNumber, isCalculate=0):
    t1 = time.time()
    user = request.user
    selectedClass = Class.objects.get(id__exact=class_id)

    try:
        if in_school(request, selectedClass.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    ok = False
    position = get_position(request)
    isSchool = True
    if position == 4: ok = True
    #kiem tra xem giao vien nay co phai chu nhiem lop nay khong
    if position == 3:
        if selectedClass.teacher_id != None:
            if selectedClass.teacher_id.user_id.id == request.user.id:
                ok = True
        if get_level(request) != 'T':
            ok = True
            isSchool = False

    if (not ok):
        return HttpResponseRedirect('/school')

    message = None
    selectedYear = selectedClass.year_id
    pupilList = Pupil.objects.filter(classes=class_id, attend__is_member=True).order_by('index', 'first_name',
        'last_name', 'birthday').distinct()

    yearString = str(selectedYear.time) + "-" + str(selectedYear.time + 1)
    tempList = []
    list = []
    # neu la hk1 hoac hk2
    termNumber = int(termNumber)

    if isCalculate:
        if termNumber < 3: noHl, noHk = calculateOverallMarkTerm(class_id, termNumber)
        else:
            noHl, noHk = calculateOverallMarkYear(class_id)
            noHl, noHk = xepLoaiLop(class_id)

        if (noHl == 0) & (noHk == 0):
            message = "Đã có đủ điểm và hạnh kiểm của cả lớp"
        elif (noHl == 0):
            message = "Còn " + str(noHk) + " học sinh chưa có hạnh kiểm"
        elif (noHk == 0):
            message = "Còn " + str(noHl) + " học sinh chưa đủ điểm "
        else:
            message = "Còn " + str(noHl) + " học sinh chưa đủ điểm và " + str(noHk) + " học sinh chưa có hạnh kiểm"

    if termNumber < 3:
        selectedTerm = Term.objects.get(year_id=selectedYear, number=termNumber)
        subjectList = Subject.objects.filter(class_id=class_id, primary__in=[0, termNumber, 3, 4]).order_by("index",
            'name')
        markList = Mark.objects.filter(subject_id__class_id=class_id, term_id=selectedTerm,
            subject_id__primary__in=[0, termNumber, 3, 4], current=True).order_by('student_id__index',
            'student_id__first_name', 'student_id__last_name', 'student_id__birthday', 'subject_id__index',
            'subject_id__name')
        tbHocKyList = TBHocKy.objects.filter(student_id__classes=class_id, term_id=selectedTerm,
            student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
            'student_id__last_name', 'student_id__birthday').distinct()
        hkList = TBNam.objects.filter(year_id=selectedYear, student_id__classes=class_id,
            student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
            'student_id__last_name', 'student_id__birthday').distinct()
        hkList1 = []

        if termNumber == 1:
            for hk in hkList:
                hkList1.append(hk.term1)
        else:
            for hk in hkList:
                hkList1.append(hk.term2)

        length = len(subjectList)

        i = 0
        for m in markList:
            t = i % length
            if t == 0:
                markOfAPupil = []
            if m.mg:
                markOfAPupil.append("MG")
            elif m.tb == None:
                markOfAPupil.append("")
            elif subjectList[t].nx:
                markOfAPupil.append(convertMarkToCharacter1(m.tb))
            else:
                markOfAPupil.append(m.tb)

            if t == 0:
                tempList.append(markOfAPupil)
            i += 1

        list = zip(pupilList, tempList, tbHocKyList, hkList1)
    else:
        calculateTKMon(class_id)
        idYear = selectedYear.id
        subjectList = Subject.objects.filter(class_id=class_id).order_by("index", 'name')
        markList = TKMon.objects.filter(subject_id__class_id=class_id, current=True).order_by('student_id__index',
            'student_id__first_name', 'student_id__last_name', 'student_id__birthday', 'subject_id__index',
            'subject_id__name')
        tbNamList = TBNam.objects.filter(year_id=selectedYear, student_id__classes=class_id,
            student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
            'student_id__last_name', 'student_id__birthday').distinct()
        length = len(subjectList)

        i = 0
        for m in markList:
            t = i % length
            if t == 0:
                markOfAPupil = []

            if m.mg:
                markOfAPupil.append("MG")
            elif m.tb_nam == None:
                markOfAPupil.append("")
            elif subjectList[t].nx:
                markOfAPupil.append(convertMarkToCharacter1(m.tb_nam))
            else:
                markOfAPupil.append(m.tb_nam)

            if t == 0:
                tempList.append(markOfAPupil)
            i += 1
        list = zip(pupilList, tempList, tbNamList, tbNamList)

    t = loader.get_template(os.path.join('school/finish', 'xep_loai_hl_theo_lop.html'))

    t2 = time.time()
    print (t2 - t1)
    c = RequestContext(request, {"message": message,
                                 "subjectList": subjectList,
                                 "list": list,
                                 "selectedClass": selectedClass,
                                 "termNumber": termNumber,
                                 "yearString": yearString,
                                 #"classList" :classList,
                                 'isSchool': isSchool,
                                 }
    )

    return HttpResponse(t.render(c))


@transaction.commit_on_success
def xepLoaiLop(class_id):
    selected_class = Class.objects.get(id=class_id)
    selected_year = selected_class.year_id
    term1 = Term.objects.get(year_id=selected_year, number=1)
    term2 = Term.objects.get(year_id=selected_year, number=2)
    tbNamList = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id,
        student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
        'student_id__last_name', 'student_id__birthday').distinct()
    ddhk1List = TKDiemDanh.objects.filter(student_id__classes=class_id, term_id=term1,
        student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
        'student_id__last_name', 'student_id__birthday').distinct()
    ddhk2List = TKDiemDanh.objects.filter(student_id__classes=class_id, term_id=term2,
        student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
        'student_id__last_name', 'student_id__birthday').distinct()
    #repr(tbNamList)
    noHk = 0
    noHl = 0
    i = 0
    for tbNam, ddhk1, ddhk2 in zip(tbNamList, ddhk1List, ddhk2List):
        i += 1
        ddhk1.tong_so = DiemDanh.objects.filter(student_id=tbNam.student_id, term_id=term1).count()
        ddhk2.tong_so = DiemDanh.objects.filter(student_id=tbNam.student_id, term_id=term2).count()
        if tbNam.year == None: noHk += 1
        if tbNam.hl_nam == None: noHl += 1

        if (ddhk1.tong_so != None) & (ddhk2.tong_so != None):
            tbNam.tong_so_ngay_nghi = ddhk1.tong_so + ddhk2.tong_so
        if tbNam.tong_so_ngay_nghi == None:
            continue
        if (tbNam.hl_nam == None) | (tbNam.year == None):
            tbNam.danh_hieu_nam = None

            if tbNam.tong_so_ngay_nghi > 45:
                tbNam.len_lop = False
                tbNam.thi_lai = None
                tbNam.ren_luyen_lai = None

                tbNam.hk_ren_luyen_lai = None
                tbNam.tb_thi_lai = None
                tbNam.hl_thi_lai = None
            else:
                tbNam.len_lop = None
                tbNam.thi_lai = None
                tbNam.ren_luyen_lai = None
                tbNam.hk_ren_luyen_lai = None
                tbNam.tb_thi_lai = None
                tbNam.hl_thi_lai = None

        else:
            if (tbNam.hl_nam == 'G') & (tbNam.year == 'T'):
                tbNam.danh_hieu_nam = 'G'
            elif ((tbNam.hl_nam == 'G') | (tbNam.hl_nam == 'K') ) & ((tbNam.year == 'T') | (tbNam.year == 'K')):
                tbNam.danh_hieu_nam = 'TT'
            else:
                tbNam.danh_hieu_nam = 'K'

            if tbNam.tong_so_ngay_nghi > 45:
                tbNam.len_lop = False
                tbNam.ren_luyen_lai = None
                tbNam.thi_lai = None
                tbNam.hk_ren_luyen_lai = None
                tbNam.tb_thi_lai = None
                tbNam.hl_thi_lai = None
                continue

            if (tbNam.hl_nam != 'Y') & (tbNam.hl_nam != 'Kem') & (tbNam.year != 'Y'):
                tbNam.len_lop = True
                tbNam.thi_lai = None
                tbNam.ren_luyen_lai = None

                tbNam.hk_ren_luyen_lai = None
                tbNam.tb_thi_lai = None
                tbNam.hl_thi_lai = None
                continue

            if ((tbNam.year != 'Y') & (tbNam.hl_nam == 'Y')):
                tbNam.len_lop = None
                tbNam.thi_lai = True
                tbNam.ren_luyen_lai = None
                tbNam.hk_ren_luyen_lai = None
                tbNam.tb_thi_lai = None
                tbNam.hl_thi_lai = None

            elif  ((tbNam.year == 'Y') & (tbNam.hl_nam != 'Y') & (tbNam.hl_nam != 'Kem')):
                tbNam.thi_lai = None
                tbNam.len_lop = None
                tbNam.ren_luyen_lai = True
                tbNam.hk_ren_luyen_lai = None
                tbNam.tb_thi_lai = None
                tbNam.hl_thi_lai = None

            else:
                tbNam.len_lop = False
                tbNam.thi_lai = None
                tbNam.ren_luyen_lai = None
                tbNam.hk_ren_luyen_lai = None
                tbNam.tb_thi_lai = None
                tbNam.hl_thi_lai = None

    for tb in tbNamList:
        tb.save()
    for dd in ddhk1List:
        dd.save()
    for dd in ddhk2List:
        dd.save()
    return noHl, noHk


@transaction.commit_on_success
@need_login
def xlCaNamTheoLop(request, class_id, type, xepLoai=0):
    t1 = time.time()
    user = request.user

    selectedClass = Class.objects.get(id__exact=class_id)
    try:
        if in_school(request, selectedClass.year_id.school_id) == False:
            return HttpResponseRedirect('/school')

    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    ok = False
    isSchool = True
    position = get_position(request)
    if position == 4: ok = True
    #kiem tra xem giao vien nay co phai chu nhiem lop nay khong
    if position == 3:
        if selectedClass.teacher_id != None:
            if selectedClass.teacher_id.user_id.id == request.user.id:
                ok = True
        if get_level(request) != 'T':
            ok = True
            isSchool = False

    if (not ok):
        return HttpResponseRedirect('/school')

    message = None
    selected_year = selectedClass.year_id
    pupilNoSum = 0
    pupilList = Pupil.objects.filter(classes=class_id, attend__is_member=True).order_by('index', 'first_name',
        'last_name', 'birthday').distinct()
    tbNamList = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id,
        student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
        'student_id__last_name', 'student_id__birthday').distinct()

    pupilList1 = []
    tbNamList1 = []
    type = int(type)

    for p, tbNam in zip(pupilList, tbNamList):
        ok = False
        if   type == 1: ok = True
        elif type == 2:
            if (tbNam.len_lop == None) & (tbNam.thi_lai == None) & (tbNam.ren_luyen_lai == None): ok = True
        elif type == 3:
            if tbNam.danh_hieu_nam == 'G': ok = True
        elif type == 4:
            if tbNam.danh_hieu_nam == 'TT': ok = True
        elif type == 5:
            if tbNam.len_lop == True: ok = True
        elif type == 6:
            if tbNam.len_lop == False: ok = True
        elif type == 7:
            if tbNam.thi_lai == True: ok = True
        elif type == 8:
            if tbNam.ren_luyen_lai == True: ok = True
        if ok:
            pupilList1.append(p)
            tbNamList1.append(tbNam)
            #hanhKiemList1.append(hk)

    list = zip(pupilList1, tbNamList1)

    number_no_calculated = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id,
        student_id__attend__is_member=True, len_lop=None, thi_lai=None, ren_luyen_lai=None).distinct().count()
    number_good_title = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id,
        student_id__attend__is_member=True, danh_hieu_nam='G').distinct().count()
    number_advanced_title = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id,
        student_id__attend__is_member=True, danh_hieu_nam='TT').distinct().count()
    number_passed = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id,
        student_id__attend__is_member=True, len_lop=True).distinct().count()
    number_no_passed = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id,
        student_id__attend__is_member=True, len_lop=False).distinct().count()
    number_exam_again = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id,
        student_id__attend__is_member=True, thi_lai=True).distinct().count()
    number_practising_again = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id,
        student_id__attend__is_member=True, ren_luyen_lai=True).distinct().count()

    #print list
    yearString = str(selectedClass.year_id.time) + "-" + str(selectedClass.year_id.time + 1)
    t = loader.get_template(os.path.join('school/finish', 'xl_ca_nam_theo_lop.html'))
    t2 = time.time()
    print (t2 - t1)

    c = RequestContext(request, {"message": message,
                                 "selectedClass": selectedClass,
                                 "yearString": yearString,
                                 "list": list,
                                 'isSchool': isSchool,
                                 'type': type,

                                 'number_no_calculated': number_no_calculated,
                                 'number_good_title': number_good_title,
                                 'number_advanced_title': number_advanced_title,
                                 'number_passed': number_passed,
                                 'number_no_passed': number_no_passed,
                                 'number_exam_again': number_exam_again,
                                 'number_practising_again': number_practising_again,
                                 }
    )

    return HttpResponse(t.render(c))

#------------------------------------------------------------------------------

# tong ket hoc ky, tinh lai toan bo hoc luc cua hoc sinh trong toan truong
# xem xet lop nao da tinh xong, lop nao chua xong de hieu truong co the chi dao
# co chuc nang ket thuc hoc ky
#-----------------------------------------------------------------------------



# liet ke danh sach cac lop da tinh xong hoc luc va cac  lop chua xong
def finishTermInSchool(term_id):
    selectedTerm = Term.objects.get(id=term_id)
    classList = Class.objects.filter(year_id=selectedTerm.year_id)
    termNumber = selectedTerm.number
    for c in classList:
        calculateOverallMarkTerm(c.id, termNumber)


def countDetailTerm(term_id):
    finishLearning = []
    notFinishLearning = []
    finishPractising = []
    notFinishPractising = []
    finishAll = []
    notFinishAll = []

    selectedTerm = Term.objects.get(id=term_id)
    classList = Class.objects.filter(year_id=selectedTerm.year_id)

    for c in classList:
        number = TBHocKy.objects.filter(term_id=term_id, student_id__classes=c.id, hl_hk=None,
            student_id__attend__is_member=True).distinct().count()
        if number == 0:   finishLearning.append(c)
        else:  notFinishLearning.append([c, number])

        if selectedTerm.number == 1:
            number = TBNam.objects.filter(year_id=selectedTerm.year_id, student_id__classes=c.id, term1=None,
                student_id__attend__is_member=True).distinct().count()
            if number == 0:  finishPractising.append(c)
            else:  notFinishPractising.append([c, number])
        else:
            number = TBNam.objects.filter(year_id=selectedTerm.year_id, student_id__classes=c.id, term2=None,
                student_id__attend__is_member=True).distinct().count()
            if number == 0:  finishPractising.append(c)
            else:  notFinishPractising.append([c, number])

        number = TBHocKy.objects.filter(term_id=term_id, student_id__classes=c.id, danh_hieu_hk=None,
            student_id__attend__is_member=True).distinct().count()
        if number == 0:  finishAll.append(c)
        else:  notFinishAll.append([c, number])
    return  finishLearning, notFinishLearning, finishPractising, notFinishPractising, finishAll, notFinishAll

#@transaction.commit_on_success                                                                                  
@need_login
def finishTerm(request, term_id=None):
    t1 = time.time()
    user = request.user

    selectedTerm = Term.objects.get(id__exact=term_id)
    try:
        if in_school(request, selectedTerm.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request) == 'T' ):
        return HttpResponseRedirect('/school')

    message = None
    print request.method

    if request.method == 'POST':
        finishTermInSchool(term_id)
        message = "Đã tính tổng kết xong. Mời bạn xem kết quả phía dưới."

    selectedTerm = Term.objects.get(id=term_id)
    yearString = str(selectedTerm.year_id.time) + "-" + str(selectedTerm.year_id.time + 1)

    finishLearning, notFinishLearning, finishPractising, notFinishPractising, finishAll, notFinishAll = countDetailTerm(
        term_id)

    hlList, pthlList = countTotalLearningInTerm(term_id)
    hkList, pthkList = countTotalPractisingInTerm(term_id)
    ddList, ptddList = countDanhHieuInTerm(term_id)

    currentTerm = get_current_term(request)
    t = loader.get_template(os.path.join('school/finish', 'finish_term.html'))

    t2 = time.time()
    print (t2 - t1)
    c = RequestContext(request, {"message": message,
                                 "selectedTerm": selectedTerm,
                                 "currentTerm": currentTerm,
                                 "yearString": yearString,

                                 "finishLearning": finishLearning,
                                 "notFinishLearning": notFinishLearning,
                                 "finishPractising": finishPractising,
                                 "notFinishPractising": notFinishPractising,
                                 "finishAll": finishAll,
                                 "notFinishAll": notFinishAll,

                                 "hlList": hlList,
                                 "pthlList": pthlList,
                                 "hkList": hkList,
                                 "pthkList": pthkList,
                                 "ddList": ddList,
                                 "ptddList": ptddList,
                                 }
    )
    return HttpResponse(t.render(c))


def finishYearInSchool(year_id):
    classList = Class.objects.filter(year_id=year_id)
    for c in classList:
        calculateOverallMarkYear(c.id)
        xepLoaiLop(c.id)


def countDetailYear(year_id):
    finishLearning = []
    notFinishLearning = []
    finishPractising = []
    notFinishPractising = []
    finishAll = []
    notFinishAll = []

    classList = Class.objects.filter(year_id=year_id)

    for c in classList:
        number = TBNam.objects.filter(year_id=year_id, student_id__classes=c.id, hl_nam=None,
            student_id__attend__is_member=True).distinct().count()
        if number == 0:   finishLearning.append(c)
        else:  notFinishLearning.append([c, number])

        number = TBNam.objects.filter(year_id=year_id, student_id__classes=c.id, year=None,
            student_id__attend__is_member=True).distinct().count()
        if number == 0:  finishPractising.append(c)
        else:  notFinishPractising.append([c, number])

        number = TBNam.objects.filter(year_id=year_id, student_id__classes=c.id, danh_hieu_nam=None,
            student_id__attend__is_member=True).distinct().count()
        if number == 0:  finishAll.append(c)
        else:  notFinishAll.append([c, number])

    return  finishLearning, notFinishLearning, finishPractising, notFinishPractising, finishAll, notFinishAll


@need_login
def finishYear(request, year_id):
    t1 = time.time()
    user = request.user

    selectedTerm = Term.objects.get(year_id=year_id, number=2)
    try:
        if in_school(request, selectedTerm.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request) == 'T' ):
        return HttpResponseRedirect('/school')

    message = None
    if request.method == 'POST':
        finishYearInSchool(year_id)
        print "ddđdddddd"
        message = "Đã tính tổng kết xong. Mời bạn xem kết quả phía dưới."

    yearString = str(selectedTerm.year_id.time) + "-" + str(selectedTerm.year_id.time + 1)
    finishLearning, notFinishLearning, finishPractising, notFinishPractising, finishAll, notFinishAll = countDetailYear(
        year_id)

    hkList, pthkList = countTotalPractisingInYear(year_id)
    hlList, pthlList = countTotalLearningInYear(year_id)
    ddList, ptddList = countDanhHieuInYear(year_id)

    currentTerm = get_current_term(request)

    t2 = time.time()
    print (t2 - t1)
    t = loader.get_template(os.path.join('school/finish', 'finish_year.html'))
    c = RequestContext(request, {"message": message,
                                 "currentTerm": currentTerm,
                                 "yearString": yearString,
                                 "finishLearning": finishLearning,
                                 "notFinishLearning": notFinishLearning,
                                 "finishPractising": finishPractising,
                                 "notFinishPractising": notFinishPractising,
                                 "finishAll": finishAll,
                                 "notFinishAll": notFinishAll,

                                 "hlList": hlList,
                                 "pthlList": pthlList,
                                 "hkList": hkList,
                                 "pthkList": pthkList,
                                 "ddList": ddList,
                                 "ptddList": ptddList,
                                 }
    )
    return HttpResponse(t.render(c))


@transaction.commit_on_success
@need_login
def thilai(request, class_id):
    t1 = time.time()
    user = request.user

    selectedClass = Class.objects.get(id__exact=class_id)
    try:
        if in_school(request, selectedClass.year_id.school_id) == False:
            return HttpResponseRedirect('/school')

    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    ok = False
    position = get_position(request)
    if position == 4: ok = True
    #kiem tra xem giao vien nay co phai chu nhiem lop nay khong
    if position == 3:
        if selectedClass.teacher_id != None:
            if selectedClass.teacher_id.user_id.id == request.user.id:
                ok = True

    if (not ok):
        return HttpResponseRedirect('/school')

    message = None
    selected_year = selectedClass.year_id
    tbNamList = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id, thi_lai=True,
        student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
        'student_id__last_name', 'student_id__birthday').distinct()
    tbMonList = []
    aTKMonList = []
    for tbNam in tbNamList:
        aTKMonList = TKMon.objects.filter(subject_id__class_id=class_id, student_id=tbNam.student_id,
            subject_id__primary__in=[0, 1, 2, 3], current=True).order_by('subject_id__index', 'subject_id__name')
        for tbMon in aTKMonList:
            if tbMon.tb_nam == None: message = "Chưa tổng kết xong điểm của cả lớp"

            elif (tbMon.tb_nam < 5) & (tbMon.mg == False):
                tbMon.thi_lai = True
            else:
                tbMon.thi_lai = False

        tbMonList.append(aTKMonList)
        """
        if   tbNam.hl_thi_lai=='G'  : tbNam.hl_thi_lai='Giỏi'
        elif tbNam.hl_thi_lai=='K'  : tbNam.hl_thi_lai='Khá'
        elif tbNam.hl_thi_lai=='TB' : tbNam.hl_thi_lai='TB'
        elif tbNam.hl_thi_lai=='Y'  : tbNam.hl_thi_lai=u'Yếu'
        elif tbNam.hl_thi_lai=='Kem' : tbNam.hl_thi_lai='Kém'
        """

    vtMonChuyen = -1
    vtMonToan = -1
    vtMonVan = -1

    i = 0
    for tkMon in aTKMonList:
        if tkMon.subject_id.hs == 3: vtMonChuyen = i
        if    tkMon.subject_id.name.lower().__contains__(u'toán'):
            vtMonToan = i
        elif  tkMon.subject_id.name.lower().__contains__(u'văn'):
            vtMonVan = i
        i += 1

    list = zip(tbMonList, tbNamList)

    if request.method == 'POST':
        for aTKMonList, tbNam in list:
            ok = True

            sum = 0
            sumFactor = 0

            monChuyen = None
            monToan = None
            monVan = None
            minMark = 10
            minComment = 10

            for (i, tbMon) in enumerate(aTKMonList):
                if tbMon.thi_lai:
                    value = request.POST[str(tbMon.id)]
                    if len(value) != 0:
                        value1 = float(value)
                        if value1 == -1:
                            value1 = None
                        tbMon.diem_thi_lai = value1
                        tbMon.save()
                    else:
                        tbMon.diem_thi_lai = None
                        tbMon.save()
                if tbMon.thi_lai:
                    if tbMon.diem_thi_lai != None:
                        if not tbMon.subject_id.nx:
                            sumFactor += tbMon.subject_id.hs
                            sum += tbMon.diem_thi_lai * tbMon.subject_id.hs

                            if minMark > tbMon.diem_thi_lai:
                                minMark = tbMon.diem_thi_lai
                        else:
                            if minComment > tbMon.diem_thi_lai:
                                minComment = tbMon.diem_thi_lai

                if (tbMon.diem_thi_lai == None) & ( tbMon.mg == False ):
                    if not tbMon.subject_id.nx:
                        sumFactor += tbMon.subject_id.hs
                        sum += tbMon.tb_nam * tbMon.subject_id.hs
                        if minMark > tbMon.tb_nam:
                            minMark = tbMon.tb_nam
                    else:
                        if minComment > tbMon.tb_nam:
                            minComment = tbMon.tb_nam

                if i == vtMonChuyen:
                    if tbMon.diem_thi_lai != None:
                        monChuyen = tbMon.diem_thi_lai
                    else:
                        monChuyen = tbMon.tb_nam

                if i == vtMonToan:
                    if tbMon.diem_thi_lai != None:
                        monToan = tbMon.diem_thi_lai
                    else:
                        monToan = tbMon.tb_nam

                elif  i == vtMonVan:
                    if tbMon.diem_thi_lai != None:
                        monVan = tbMon.diem_thi_lai
                    else:
                        monVan = tbMon.tb_nam

            tbNam.tb_thi_lai = round(float(sum) / sumFactor, 1)
            tbNam.hl_thi_lai = defineHl(tbNam.tb_thi_lai, monChuyen, monToan, monVan, minMark, minComment)
            if (tbNam.hl_thi_lai != 'Y') & (tbNam.hl_thi_lai != 'Kem'):
                tbNam.len_lop = True
            else:
                tbNam.len_lop = False
            tbNam.save()

    lengthList = len(list)
    if lengthList == 0:
        message = "Lớp chưa tổng kết xong hoặc không có học sinh nào phải thi lại"
    numberSubject = len(aTKMonList)

    yearString = str(selectedClass.year_id.time) + "-" + str(selectedClass.year_id.time + 1)

    t = loader.get_template(os.path.join('school/finish', 'thi_lai.html'))
    t2 = time.time()
    print (t2 - t1)

    c = RequestContext(request, {"message": message,
                                 "selectedClass": selectedClass,
                                 "yearString": yearString,
                                 'lengthList': lengthList,
                                 'numberSubject': numberSubject,
                                 'aTKMonList': aTKMonList,
                                 'vtMonChuyen': vtMonChuyen,
                                 'vtMonToan': vtMonToan,
                                 'vtMonVan': vtMonVan,
                                 "list": list,
                                 }
    )

    return HttpResponse(t.render(c))


def updateHocLai(str):
    strs = str.split('*')
    if   (strs[0] == '0'):
        id = int(strs[1])
        tkMon = TKMon.objects.get(id=id)

        if strs[2] != '-1':
            tkMon.thi_lai = True
            tkMon.diem_thi_lai = float(strs[2])
        else:
            tkMon.thi_lai = False
            tkMon.diem_thi_lai = None

        tkMon.save()

    elif (strs[0] == '1'):
        id = int(strs[1])
        tbNam = TBNam.objects.get(id=id)

        if strs[2] != '-1':
            tbNam.tb_thi_lai = float(strs[2])
        else:
            tbNam.tb_thi_lai = None
        tbNam.save()
    else:
        id = int(strs[1])
        tbNam = TBNam.objects.get(id=id)

        if strs[2] != '-1':
            tbNam.hl_thi_lai = strs[2]
            if (strs[2] != 'Y') & (strs[2] != 'Kem'):
                tbNam.len_lop = True
            else:
                tbNam.len_lop = False
        else:
            tbNam.hl_thi_lai = None
            tbNam.len_lop = None

        tbNam.save()


@need_login
def saveHocLai(request):
    message = 'hello'
    if request.method == 'POST':
        str = request.POST['str']
        strs = str.split(':')
        length = len(strs)
        for i in range(1, length):
            updateHocLai(strs[i])

        message = 'ok'
        data = simplejson.dumps({'message': message})
        return HttpResponse(data, mimetype='json')


@need_login
def renluyenthem(request, class_id):
    t1 = time.time()
    user = request.user

    selectedClass = Class.objects.get(id__exact=class_id)
    try:
        if in_school(request, selectedClass.year_id.school_id) == False:
            return HttpResponseRedirect('/school')

    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    ok = False
    position = get_position(request)
    if position == 4: ok = True
    #kiem tra xem giao vien nay co phai chu nhiem lop nay khong
    if position == 3:
        if selectedClass.teacher_id != None:
            if selectedClass.teacher_id.user_id.id == request.user.id:
                ok = True

    if (not ok):
        return HttpResponseRedirect('/school')

    message = None
    selected_year = selectedClass.year_id
    hkList = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id, ren_luyen_lai=True,
        student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
        'student_id__last_name', 'student_id__birthday').distinct()

    lengthList = len(hkList)
    if lengthList == 0:
        message = "Lớp chưa có hạnh kiểm cuối năm hoặc không có học sinh nào phải rèn luyện thêm"

    yearString = str(selectedClass.year_id.time) + "-" + str(selectedClass.year_id.time + 1)

    t = loader.get_template(os.path.join('school/finish', 'ren_luyen_them.html'))
    t2 = time.time()
    print (t2 - t1)

    c = RequestContext(request, {"message": message,
                                 "selectedClass": selectedClass,
                                 "yearString": yearString,
                                 'lengthList': lengthList,
                                 "hkList": hkList,
                                 }
    )

    return HttpResponse(t.render(c))


@need_login
def saveRenLuyenThem(request):
    message = 'hello'
    if request.method == 'POST':
        str = request.POST['str']
        strs = str.split(':')
        id = int(strs[0])

        tbNam = TBNam.objects.get(id=id)
        if strs[1] != 'No':
            tbNam.hk_ren_luyen_lai = strs[1]
        else:
            tbNam.hk_ren_luyen_lai = None

        if strs[1] == 'No':
            tbNam.len_lop = None
        elif strs[1] == 'Y':
            tbNam.len_lop = False
        else:
            tbNam.len_lop = True

        tbNam.save()
        message = 'ok'
        data = simplejson.dumps({'message': message})
        return HttpResponse(data, mimetype='json')


def getContentSendSMSResult(class_id, termNumber):
    selected_class = Class.objects.get(id=class_id)
    selected_year = selected_class.year_id
    tempList = []
    list = []
    pupilList = Pupil.objects.filter(classes=class_id, attend__is_member=True).order_by('index', 'first_name',
        'last_name', 'birthday').distinct()
    if termNumber < 3:
        selected_term = Term.objects.get(year_id=selected_year, number=termNumber)
        tbHocKyList = TBHocKy.objects.filter(student_id__classes=class_id, term_id=selected_term,
            student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
            'student_id__last_name', 'student_id__birthday').distinct()
        hkList = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id,
            student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
            'student_id__last_name', 'student_id__birthday').distinct()
        hkList1 = []
        if termNumber == 1:
            for hk in hkList:
                hkList1.append(hk.term1)
        else:
            for hk in hkList:
                hkList1.append(hk.term2)
        list1 = zip(pupilList, tbHocKyList, hkList1)
    else:
        tbNamList = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id,
            student_id__attend__is_member=True).order_by('student_id__index', 'student_id__first_name',
            'student_id__last_name', 'student_id__birthday').distinct()
        list1 = zip(pupilList, tbNamList, tbNamList)

    contentList = []
    if termNumber < 3:
        subjectList = Subject.objects.filter(class_id=class_id, primary__in=[0, termNumber, 3, 4]).order_by("index",
            'name')
        markList = Mark.objects.filter(subject_id__class_id=class_id, term_id__number=termNumber,
            subject_id__primary__in=[0, termNumber, 3, 4], current=True).order_by('student_id__index',
            'student_id__first_name', 'student_id__last_name', 'student_id__birthday', 'subject_id__index',
            'subject_id__name')

        length = len(subjectList)
        i = 0
        for m in markList:
            t = i % length
            if t == 0:
                markOfAPupil = []
            if m.mg:
                markOfAPupil.append("MG")
            elif m.tb == None:
                markOfAPupil.append("")
            elif subjectList[t].nx:
                markOfAPupil.append(convertMarkToCharacter(m.tb))
            else:
                markOfAPupil.append(m.tb)

            if t == 0:
                tempList.append(markOfAPupil)
            i += 1
    else:
        subjectList = Subject.objects.filter(class_id=class_id).order_by("index", 'name')
        markList = TKMon.objects.filter(subject_id__class_id=class_id, current=True).order_by('student_id__index',
            'student_id__first_name', 'student_id__last_name', 'student_id__birthday', 'subject_id__index',
            'subject_id__name')
        length = len(subjectList)

        i = 0
        for m in markList:
            t = i % length
            if t == 0:
                markOfAPupil = []

            if m.mg:
                markOfAPupil.append("MG")
            elif m.tb_nam == None:
                markOfAPupil.append("")
            elif subjectList[t].nx:
                markOfAPupil.append(convertMarkToCharacter1(m.tb_nam))
            else:
                markOfAPupil.append(m.tb_nam)

            if t == 0:
                tempList.append(markOfAPupil)
            i += 1

    i = 1

    for p, tb, hk in list1:
        smsString = ''
        markOfAPupil = tempList[i - 1]
        for s, m in zip(subjectList, markOfAPupil):
            smsString += to_en1(s.name) + ':' + unicode(m) + ', '
        if termNumber < 3:
            if tb.tb_hk != None:
                smsString += 'TB:' + str(tb.tb_hk) + ', '
            else:
                smsString += 'TB:' + ', '
            smsString += 'hoc luc :' + to_en1(convertHlToVietnamese(tb.hl_hk)) + ', '
            smsString += 'hanh kiem:' + to_en1(convertHkToVietnamese(hk))
            if (tb.danh_hieu_hk == 'G') | (tb.danh_hieu_hk == 'TT'):
                smsString += ', ' + 'danh hieu:' + convertDanhHieu(tb.danh_hieu_hk) + '.'
            else:
                smsString += '.'
        else:
            if tb.tb_nam != None:
                smsString += 'TB:' + str(tb.tb_nam) + ', '
            else:
                smsString += 'TB:' + ', '
            smsString += 'hoc luc :' + to_en1(convertHlToVietnamese(tb.hl_nam)) + ', '
            smsString += 'hanh kiem:' + to_en1(convertHkToVietnamese(tb.year)) + ', '
            if (tb.danh_hieu_nam == 'G') | (tb.danh_hieu_nam == 'TT'):
                smsString += 'danh hieu:' + convertDanhHieu(tb.danh_hieu_nam) + ','
            smsString += 'thuoc dien:'
            if  tb.len_lop == True:
                smsString += 'len lop.'
            elif tb.len_lop == False:
                smsString += 'khong len lop.'
            elif tb.thi_lai == True:
                smsString += 'kiem tra lai mot so mon.'
            elif tb.ren_luyen_lai:
                smsString += 'ren luyen them trong he.'
            else:
                smsString += 'chua xep loai.'
        i += 1

        contentList.append(smsString)

    if termNumber < 3:
        list = zip(pupilList, contentList, tbHocKyList)
    else:
        list = zip(pupilList, contentList, tbNamList)
    return list


#@need_login
#def sendSMSResult(request, class_id, termNumber=None):
#    t1 = time.time()
#    user = request.user
#
#    selectedClass = Class.objects.get(id__exact=class_id)
#
#    try:
#        if in_school(request, selectedClass.year_id.school_id) == False:
#            return HttpResponseRedirect('/school')
#    except Exception as e:
#        return HttpResponseRedirect(reverse('index'))
#
#    ok = False
#    position = get_position(request)
#    if position == 4: ok = True
#    #kiem tra xem giao vien nay co phai chu nhiem lop nay khong
#    if position == 3:
#        if selectedClass.teacher_id != None:
#            if selectedClass.teacher_id.user_id.id == request.user.id:
#                ok = True
#
#    if (not ok):
#        return HttpResponseRedirect('/school')
#    if termNumber == None:
#        currentTerm = get_current_term(request)
#        termNumber = currentTerm.number
#
#    message = None
#    selectedYear = selectedClass.year_id
#
#    yearString = str(selectedYear.time) + "-" + str(selectedYear.time + 1)
#    # neu la hk1 hoac hk2
#    termNumber = int(termNumber)
#    list = getContentSendSMSResult(class_id, termNumber)
#    if request.method == "POST":
#        data = request.POST[u'data']
#        datas = data.split('-')
#        successString = ''
#        numberSent = 0
#        numberSuccess = 0
#        i = 1
#        for p, c, tb in list:
#            if str(i) in datas:
#                smsString = u'Tong ket '
#                if termNumber == 1:
#                    termString = u'hoc ky I nam hoc '
#                elif termNumber == 2:
#                    termString = u'hoc ky II nam hoc '
#                else:
#                    termString = u'ca nam nam hoc '
#                smsString += termString + yearString
#                smsString += ' cua hs ' + to_en1(p.last_name) + ' ' + to_en1(p.first_name) + ' nhu sau:'
#
#                smsString += c
#                numberSent += 1
#                if p.sms_phone:
#                    sent = ''
#
#                    try:
#                        sent = sendSMS(p.sms_phone, smsString, user)
#                    except Exception as e:
#                        pass
#                    if sent == '1':
#                        numberSuccess += 1
#                        successString += str(i) + '-'
#                        tb.sent = True
#                        tb.save()
#            i += 1
#
#        message = "ok111111111111"
#        result = 'Đã gửi thành công ' + str(numberSuccess) + '/' + str(numberSent)
#        data = simplejson.dumps({'successString': successString,
#                                 'result': result})
#        return HttpResponse(data, mimetype='json')
#
#    t = loader.get_template(os.path.join('school', 'send_sms_result.html'))
#
#    t2 = time.time()
#    print (t2 - t1)
#    c = RequestContext(request, {"message": message,
#                                 "list": list,
#                                 "selectedClass": selectedClass,
#                                 "termNumber": termNumber,
#                                 #"classList" :classList,
#    }
#    )
#
#    return HttpResponse(t.render(c))
