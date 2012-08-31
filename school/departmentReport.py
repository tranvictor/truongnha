# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from school.models import *
from app.models import *
from sms.models import *

from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
import os.path
import time
from datetime import datetime
from school.utils import *
from school.templateExcel import *
from school.writeExcel import count1Excel,count2Excel,printDanhHieuExcel,printNoPassExcel,practisingByGradeExcel,\
practisingByMajorExcel,learningByGradeExcel,learningByMajorExcel,titleByGradeExcel,titleByMajorExcel,\
practisingByDistrictExcel,learningByDistrictExcel,titleByDistrictExcel,countFinalMarkExcel
from decorators import need_login, school_function, operating_permission

@need_login
def departmentReport(request):
    message=None
    so = request.user.userprofile.organization
    if so.level != 'S':
        return HttpResponseRedirect(reverse('index'))

    schoolList = so.organization_set.all()

    t = loader.get_template(os.path.join('school/report','department_report.html'))
    c = RequestContext(request, {"message":message,
                                 'schoolList':schoolList,
                                 }
    )
    return HttpResponse(t.render(c))

def defineYearList(yearNumber,termNumber,type='1'):
    now = datetime.now()
    month = now.month
    if (1<=month) and (month<=10):
        lastestYear = now.year
    else:
        lastestYear = now.year+1

    if yearNumber==None:
        yearNumber = now.year-1
        if 5>=month:
            termNumber = 1
        elif (7>=month) or (type=='0'):
            termNumber = 2
        else:
            termNumber = 3

    yearList=[]
    for i in range(2011,lastestYear):
        yearList.append((str(i)+"-"+str(i+1)))

    return yearList,yearNumber,termNumber

@need_login
def practisingByGrade(request,yearNumber=None,termNumber=-1,isExcel=0):

    message=None
    yearList,yearNumber,termNumber = defineYearList(yearNumber,termNumber)
    so = request.user.userprofile.organization
    if so.level != 'S':
        return HttpResponseRedirect(reverse('index'))

    listSchool = so.organization_set.all()
    list=[0]*12
    for i in range(12):
        list[i] = [0]*9

    string=['T','K','TB','Y',None]
    for b in range(6,13):
        for i in range(string.__len__()-1):
            if int(termNumber) == 1:
                list[b-1][2*i+1]+=TBNam.objects.filter(year_id__time=yearNumber,term1=string[i],student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so).count()
            elif int(termNumber) == 2:
                list[b-1][2*i+1]+=TBNam.objects.filter(year_id__time=yearNumber,term2=string[i],student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so).count()
            else:
                list[b-1][2*i+1]+=TBNam.objects.filter(year_id__time=yearNumber,year=string[i],student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so).count()

        list[b-1][0] = TBNam.objects.filter(year_id__time=yearNumber,student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so).count()
        for i in range(string.__len__()-1):
            if list[b-1][0]!=0:
                list[b-1][2*i+2]=round(list[b-1][2*i+1]*100.0/list[b-1][0],2)
    if isExcel:
        return practisingByGradeExcel(list,yearNumber,termNumber,so)

    print yearNumber
    t = loader.get_template(os.path.join('school/report','practising_by_grade.html'))
    c = RequestContext(request, {"message":message,
                                 "list":list,
                                 'yearList':yearList,
                                 'yearNumber':yearNumber,
                                 'termNumber':termNumber,
                                 }
    )
    return HttpResponse(t.render(c))

@need_login
def practisingByMajor(request,yearNumber=None,termNumber=-1,isExcel=0):
    tt1=time.time()

    message=None
    yearList,yearNumber,termNumber = defineYearList(yearNumber,termNumber)
    so = request.user.userprofile.organization
    if so.level != 'S':
        return HttpResponseRedirect(reverse('index'))

    listSchool = so.organization_set.all()
    list=[0]*12
    for i in range(12):
        list[i] = [0]*len(BAN_CHOICE)

    for i in range(12):
        for j in range(len(BAN_CHOICE)):
            list[i][j] = [0] * 9

    string=['T','K','TB','Y',None]
    for b in range(10,13):
        for (k,ban) in enumerate(BAN_CHOICE):
            for i in range(string.__len__()-1):
                if int(termNumber) == 1:
                    list[b-1][k][2*i+1]+=TBNam.objects.filter(year_id__time=yearNumber,term1=string[i],student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so,student_id__ban_dk=ban[0]).count()
                elif int(termNumber) == 2:
                    list[b-1][k][2*i+1]+=TBNam.objects.filter(year_id__time=yearNumber,term2=string[i],student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so,student_id__ban_dk=ban[0]).count()
                else:
                    list[b-1][k][2*i+1]+=TBNam.objects.filter(year_id__time=yearNumber,year=string[i],student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so,student_id__ban_dk=ban[0]).count()

            list[b-1][k][0] = TBNam.objects.filter(year_id__time=yearNumber,student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so,student_id__ban_dk=ban[0]).count()

            for i in range(string.__len__()-1):
                if list[b-1][k][0]!=0:
                    list[b-1][k][2*i+2]=round(list[b-1][k][2*i+1]*100.0/list[b-1][k][0],2)

    if isExcel:
        return practisingByMajorExcel(list,yearNumber,termNumber,so)
    tt2 = time.time()
    print (tt2-tt1)/1000.0
    print yearNumber
    t = loader.get_template(os.path.join('school/report','practising_by_major.html'))
    c = RequestContext(request, {"message":message,
                                 "list":list,
                                 'yearList':yearList,
                                 'yearNumber':yearNumber,
                                 'termNumber':termNumber,
                                 'BAN_CHOICE':BAN_CHOICE,
                                 }
    )
    return HttpResponse(t.render(c))

@need_login
def practisingByDistrict(request,yearNumber=None,termNumber=-1,isExcel=0):
    tt1=time.time()

    message=None
    yearList,yearNumber,termNumber = defineYearList(yearNumber,termNumber)
    so = request.user.userprofile.organization
    if so.level != 'S':
        return HttpResponseRedirect(reverse('index'))

    listSchool = so.organization_set.all().order_by("district")
    numberSchool = len(listSchool)

    list=[]
    string=['T','K','TB','Y',None]
    numberType = len(string)*2 -1
    tong = [0] * numberType
    list1 = []
    tong = [0] * numberType
    for (k,s) in  enumerate(listSchool):
        list2 = [0] * numberType
        if int(termNumber) <3 :
            year = Year.objects.filter(time = yearNumber, school_id = s)
            if len(year) >0:
                y = year[0]
                list2[0] = TBNam.objects.filter(year_id = y).count()
                tong [0]+= list2[0]
                for i in range(string.__len__()-1):
                    if int(termNumber) == 1:
                        list2[2*i+1]=TBNam.objects.filter(year_id = y,term1=string[i]).count()
                        if (list2[0] > 0):
                            list2[2*i+2]=round(list2[2*i+1]*100.0/list2[0],2)
                    else:
                        list2[2*i+1]=TBNam.objects.filter(year_id = y,term2=string[i]).count()
                        if (list2[0] > 0):
                            list2[2*i+2]=round(list2[2*i+1]*100.0/list2[0],2)
                    tong [2*i+1]+=list2[2*i+1]
        else:
            year = Year.objects.filter(time = yearNumber, school_id = s)
            if len(year) >0:
                y = year[0]
                list2[0] = TBNam.objects.filter(year_id = y).count()
                tong [0]+= list2[0]
                for i in range(string.__len__()-1):
                    list2[2*i+1] = TBNam.objects.filter(year_id=y, year=string[i]).count()
                    if (list2[0] > 0):
                        list2[2*i+2]=round(list2[2*i+1]*100.0/list2[0],2)
                tong [2*i+1]+= list2[2*i+1]

        list1.append((s,list2))
        if ((k<numberSchool-1) and (listSchool[k].district != listSchool[k+1].district)) or ( k== numberSchool-1):
            for i in range(string.__len__()-1):
                if tong[0]>0:
                    tong[2*i+2] = round(tong[2*i+1]*100.0/tong[0],2)
            list1.append(('1',tong))
            tong = [0] * numberType
            list.append(list1)
            list1=[]

    if isExcel:
        return practisingByDistrictExcel(list,yearNumber,termNumber,so)
    tt2 = time.time()
    print (tt2-tt1)/1000.0
    print yearNumber
    t = loader.get_template(os.path.join('school/report','practising_by_district.html'))
    c = RequestContext(request, {"message":message,
                                 "list":list,
                                 'yearList':yearList,
                                 'yearNumber':yearNumber,
                                 'termNumber':termNumber,
                                 }
    )
    return HttpResponse(t.render(c))

@need_login
def learningByGrade(request,yearNumber=None,termNumber=-1,isExcel=0):

    message=None
    yearList,yearNumber,termNumber = defineYearList(yearNumber,termNumber)
    so = request.user.userprofile.organization
    if so.level != 'S':
        return HttpResponseRedirect(reverse('index'))

    listSchool = so.organization_set.all()
    list=[0]*12
    for i in range(12):
        list[i] = [0]*11

    string=['G','K','TB','Y','Kem',None]
    for b in range(6,13):
        for i in range(string.__len__()-1):
            if int(termNumber) < 3:
                list[b-1][2*i+1]+=TBHocKy.objects.filter(term_id__year_id__time=yearNumber,term_id__number=termNumber,hl_hk=string[i],student_id__classes__block_id__number=b,term_id__year_id__school_id__upper_organization=so).count()
            else:
                list[b-1][2*i+1]+=TBNam.objects.filter(year_id__time=yearNumber,hl_nam=string[i],student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so).count()

        list[b-1][0] = TBNam.objects.filter(year_id__time=yearNumber,student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so).count()
        for i in range(string.__len__()-1):
            if list[b-1][0]!=0:
                list[b-1][2*i+2]=round(list[b-1][2*i+1]*100.0/list[b-1][0],2)
    if isExcel:
        return learningByGradeExcel(list,yearNumber,termNumber,so)

    print yearNumber
    t = loader.get_template(os.path.join('school/report','learning_by_grade.html'))
    c = RequestContext(request, {"message":message,
                                 "list":list,
                                 'yearList':yearList,
                                 'yearNumber':yearNumber,
                                 'termNumber':termNumber,
                                 }
    )
    return HttpResponse(t.render(c))

@need_login
def learningByMajor(request,yearNumber=None,termNumber=-1,isExcel=0):
    tt1=time.time()

    message=None
    yearList,yearNumber,termNumber = defineYearList(yearNumber,termNumber)
    so = request.user.userprofile.organization
    if so.level != 'S':
        return HttpResponseRedirect(reverse('index'))

    listSchool = so.organization_set.all()
    list=[0]*12
    for i in range(12):
        list[i] = [0]*len(BAN_CHOICE)

    for i in range(12):
        for j in range(len(BAN_CHOICE)):
            list[i][j] = [0] * 11

    string=['G','K','TB','Y','Kem',None]
    for b in range(10,13):
        for (k,ban) in enumerate(BAN_CHOICE):
            for i in range(string.__len__()-1):
                if int(termNumber) <3 :
                    list[b-1][k][2*i+1]+=TBHocKy.objects.filter(term_id__year_id__time=yearNumber,term_id__number=termNumber,hl_hk=string[i],student_id__classes__block_id__number=b,term_id__year_id__school_id__upper_organization=so,student_id__ban_dk=ban[0]).count()
                else:
                    list[b-1][k][2*i+1]+=TBNam.objects.filter(year_id__time=yearNumber,hl_nam=string[i],student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so,student_id__ban_dk=ban[0]).count()

            list[b-1][k][0] = TBNam.objects.filter(year_id__time=yearNumber,student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so,student_id__ban_dk=ban[0]).count()

            for i in range(string.__len__()-1):
                if list[b-1][k][0]!=0:
                    list[b-1][k][2*i+2]=round(list[b-1][k][2*i+1]*100.0/list[b-1][k][0],2)

    if isExcel:
        return learningByMajorExcel(list,yearNumber,termNumber,so)
    tt2 = time.time()
    print (tt2-tt1)/1000.0
    print yearNumber
    t = loader.get_template(os.path.join('school/report','learning_by_major.html'))
    c = RequestContext(request, {"message":message,
                                 "list":list,
                                 'yearList':yearList,
                                 'yearNumber':yearNumber,
                                 'termNumber':termNumber,
                                 'BAN_CHOICE':BAN_CHOICE,
                                 }
    )
    return HttpResponse(t.render(c))

@need_login
def learningByDistrict(request,yearNumber=None,termNumber=-1,isExcel=0):
    tt1=time.time()

    message=None
    yearList,yearNumber,termNumber = defineYearList(yearNumber,termNumber)
    so = request.user.userprofile.organization
    if so.level != 'S':
        return HttpResponseRedirect(reverse('index'))

    listSchool = so.organization_set.all().order_by("district")
    numberSchool = len(listSchool)

    list=[]
    string=['G','K','TB','Y','Kem',None]
    numberType = len(string)*2 -1
    tong = [0] * numberType
    list1 = []
    tong = [0] * numberType
    for (k,s) in  enumerate(listSchool):
        list2 = [0] * numberType
        if int(termNumber) <3 :
            term = Term.objects.filter(year_id__time = yearNumber,number= termNumber,year_id__school_id = s)
            if len(term) >0:
                t = term[0]
                list2[0] = TBHocKy.objects.filter(term_id = t).count()
                tong [0]+= list2[0]
                for i in range(string.__len__()-1):
                    list2[2*i+1]=TBHocKy.objects.filter(term_id = t,hl_hk=string[i]).count()
                    if (list2[0] > 0):
                        list2[2*i+2]=round(list2[2*i+1]*100.0/list2[0],2)
                    tong [2*i+1]+=list2[2*i+1]
        else:
            year = Year.objects.filter(time = yearNumber, school_id = s)
            if len(year) >0:
                y = year[0]
                list2[0] = TBNam.objects.filter(year_id = y).count()
                tong [0]+= list2[0]
                for i in range(string.__len__()-1):
                    list2[2*i+1] = TBNam.objects.filter(year_id=y, hl_nam=string[i]).count()
                    if (list2[0] > 0):
                        list2[2*i+2]=round(list2[2*i+1]*100.0/list2[0],2)
                    tong [2*i+1]+= list2[2*i+1]

        list1.append((s,list2))
        if ((k<numberSchool-1) and (listSchool[k].district != listSchool[k+1].district)) or ( k== numberSchool-1):
            for i in range(string.__len__()-1):
                if tong[0]>0:
                    tong[2*i+2] = round(tong[2*i+1]*100.0/tong[0],2)
            list1.append(('1',tong))
            tong = [0] * numberType
            list.append(list1)
            list1=[]

    if isExcel:
        return learningByDistrictExcel(list,yearNumber,termNumber,so)
    tt2 = time.time()
    print (tt2-tt1)/1000.0
    print yearNumber
    t = loader.get_template(os.path.join('school/report','learning_by_district.html'))
    c = RequestContext(request, {"message":message,
                                 "list":list,
                                 'yearList':yearList,
                                 'yearNumber':yearNumber,
                                 'termNumber':termNumber,
                                 }
    )
    return HttpResponse(t.render(c))

@need_login
def titleByGrade(request,yearNumber=None,termNumber=-1,isExcel=0):

    message=None
    yearList,yearNumber,termNumber = defineYearList(yearNumber,termNumber)
    so = request.user.userprofile.organization
    if so.level != 'S':
        return HttpResponseRedirect(reverse('index'))

    listSchool = so.organization_set.all()
    list=[0]*12
    for i in range(12):
        list[i] = [0]*5

    string=['G','TT',None]
    for b in range(6,13):
        for i in range(string.__len__()-1):
            if int(termNumber) < 3:
                list[b-1][2*i+1]+=TBHocKy.objects.filter(term_id__year_id__time=yearNumber,term_id__number=termNumber,danh_hieu_hk=string[i],student_id__classes__block_id__number=b,term_id__year_id__school_id__upper_organization=so).count()
            else:
                list[b-1][2*i+1]+=TBNam.objects.filter(year_id__time=yearNumber,danh_hieu_nam=string[i],student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so).count()

        list[b-1][0] = TBNam.objects.filter(year_id__time=yearNumber,student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so).count()
        for i in range(string.__len__()-1):
            if list[b-1][0]!=0:
                list[b-1][2*i+2]=round(list[b-1][2*i+1]*100.0/list[b-1][0],2)
    if isExcel:
        return titleByGradeExcel(list,yearNumber,termNumber,so)

    print yearNumber
    t = loader.get_template(os.path.join('school/report','title_by_grade.html'))
    c = RequestContext(request, {"message":message,
                                 "list":list,
                                 'yearList':yearList,
                                 'yearNumber':yearNumber,
                                 'termNumber':termNumber,
                                 }
    )
    return HttpResponse(t.render(c))

@need_login
def titleByMajor(request,yearNumber=None,termNumber=-1,isExcel=0):
    tt1=time.time()

    message=None
    yearList,yearNumber,termNumber = defineYearList(yearNumber,termNumber)
    so = request.user.userprofile.organization
    if so.level != 'S':
        return HttpResponseRedirect(reverse('index'))

    listSchool = so.organization_set.all()
    list=[0]*12
    for i in range(12):
        list[i] = [0]*len(BAN_CHOICE)

    for i in range(12):
        for j in range(len(BAN_CHOICE)):
            list[i][j] = [0] * 5

    string=['G','TT',None]
    for b in range(10,13):
        for (k,ban) in enumerate(BAN_CHOICE):
            for i in range(string.__len__()-1):
                if int(termNumber) <3 :
                    list[b-1][k][2*i+1]+=TBHocKy.objects.filter(term_id__year_id__time=yearNumber,term_id__number=termNumber,danh_hieu_hk=string[i],student_id__classes__block_id__number=b,term_id__year_id__school_id__upper_organization=so,student_id__ban_dk=ban[0]).count()
                else:
                    list[b-1][k][2*i+1]+=TBNam.objects.filter(year_id__time=yearNumber,danh_hieu_nam=string[i],student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so,student_id__ban_dk=ban[0]).count()

            list[b-1][k][0] = TBNam.objects.filter(year_id__time=yearNumber,student_id__classes__block_id__number=b,year_id__school_id__upper_organization=so,student_id__ban_dk=ban[0]).count()

            for i in range(string.__len__()-1):
                if list[b-1][k][0]!=0:
                    list[b-1][k][2*i+2]=round(list[b-1][k][2*i+1]*100.0/list[b-1][k][0],2)

    if isExcel:
        return titleByMajorExcel(list,yearNumber,termNumber,so)
    tt2 = time.time()
    print (tt2-tt1)/1000.0
    print yearNumber
    t = loader.get_template(os.path.join('school/report','title_by_major.html'))
    c = RequestContext(request, {"message":message,
                                 "list":list,
                                 'yearList':yearList,
                                 'yearNumber':yearNumber,
                                 'termNumber':termNumber,
                                 'BAN_CHOICE':BAN_CHOICE,
                                 }
    )
    return HttpResponse(t.render(c))

@need_login
def titleByDistrict(request,yearNumber=None,termNumber=-1,isExcel=0):
    tt1=time.time()

    message=None
    yearList,yearNumber,termNumber = defineYearList(yearNumber,termNumber)
    so = request.user.userprofile.organization
    if so.level != 'S':
        return HttpResponseRedirect(reverse('index'))

    listSchool = so.organization_set.all().order_by("district")
    numberSchool = len(listSchool)

    list=[]
    string=['G','TT',None]
    numberType = len(string)*2 -1
    tong = [0] * numberType
    list1 = []
    tong = [0] * numberType
    for (k,s) in  enumerate(listSchool):
        list2 = [0] * numberType
        if int(termNumber) <3 :
            term = Term.objects.filter(year_id__time = yearNumber,number= termNumber,year_id__school_id = s)
            if len(term) >0:
                t = term[0]
                list2[0] = TBHocKy.objects.filter(term_id = t).count()
                tong [0]+= list2[0]
                for i in range(string.__len__()-1):
                    list2[2*i+1]=TBHocKy.objects.filter(term_id = t,danh_hieu_hk=string[i]).count()
                    if (list2[0] > 0):
                        list2[2*i+2]=round(list2[2*i+1]*100.0/list2[0],2)
                    tong [2*i+1]+=list2[2*i+1]
        else:
            year = Year.objects.filter(time = yearNumber, school_id = s)
            if len(year) >0:
                y = year[0]
                list2[0] = TBNam.objects.filter(year_id = y).count()
                tong [0]+= list2[0]
                for i in range(string.__len__()-1):
                    list2[2*i+1] = TBNam.objects.filter(year_id=y, danh_hieu_nam=string[i]).count()
                    if (list2[0] > 0):
                        list2[2*i+2]=round(list2[2*i+1]*100.0/list2[0],2)
                    tong [2*i+1]+= list2[2*i+1]

        list1.append((s,list2))
        if ((k<numberSchool-1) and (listSchool[k].district != listSchool[k+1].district)) or ( k== numberSchool-1):
            for i in range(string.__len__()-1):
                if tong[0]>0:
                    tong[2*i+2] = round(tong[2*i+1]*100.0/tong[0],2)
            list1.append(('1',tong))
            tong = [0] * numberType
            list.append(list1)
            list1=[]

    if isExcel:
        return titleByDistrictExcel(list,yearNumber,termNumber,so)
    tt2 = time.time()
    print (tt2-tt1)/1000.0
    print yearNumber
    t = loader.get_template(os.path.join('school/report','title_by_district.html'))
    c = RequestContext(request, {"message":message,
                                 "list":list,
                                 'yearList':yearList,
                                 'yearNumber':yearNumber,
                                 'termNumber':termNumber,
                                 }
    )
    return HttpResponse(t.render(c))

@need_login
def countFinalMark(request,type=0,yearNumber=None,termNumber=-1,subjectIndex=-1,blockIndex=-1,isExcel=0):
    tt1=time.time()
    message=None
    yearList,yearNumber,termNumber = defineYearList(yearNumber,termNumber,type)
    so = request.user.userprofile.organization
    if so.level != 'S':
        return HttpResponseRedirect(reverse('index'))
    subjectList = SUBJECT_LIST
    list=[]
    headerTable=[]
    if blockIndex!= None:
        subjectType = subjectList[int(subjectIndex)-1]
        if (subjectType==u'Âm nhạc') | (subjectType==u'Mĩ thuật') | (subjectType==u'Thể dục'):
            isComment = True
        else:
            isComment = False

        if not isComment:
            numberLevel = 5
            level =[11,7.995,6.495,4.995,3.495,-1]
            headerTable = [u"8 - 10",u"6.5 - 7.9",u"5 - 6.4",u"3.5 - 4.9",u"0 - 3.4"]
        else:
            numberLevel = 2
            level =[11,4.995,-1]
            headerTable = [u"Đạt",u"Không đạt"]


        listSchool = so.organization_set.all()
        slSum = [0]*numberLevel
        ptSum = [0]*numberLevel
        sumsum= 0.0

        for l in listSchool:
            if l.school_level=='2':
                if int(blockIndex) > 9: continue
            elif int(blockIndex) <10 :continue

            slList=[0]*numberLevel
            ptList=[0]*numberLevel

            term = Term.objects.filter(year_id__time = yearNumber,number = 1 ,year_id__school_id = l)
            if len(term)> 0:
                t = term[0]
                sum  = Mark.objects.filter(term_id = t, subject_id__type=subjectType,subject_id__class_id__block_id__number = blockIndex,current=True).count()
            else:
                sum =0
            sumsum+=sum

            for i in range(numberLevel):
                if type=='0':
                    term = Term.objects.filter(year_id__time = yearNumber, number = termNumber, year_id__school_id = l)
                    if len(term) > 0:
                        t = term[0]
                        slList[i] = Mark.objects.filter(term_id= t ,subject_id__type=subjectType,subject_id__class_id__block_id__number = blockIndex, ck__lt=level[i],ck__gt=level[i+1],current=True).count()
                        if sum >0: ptList[i] = round(slList[i]*100.0/sum,2)
                else:
                    if int(termNumber)< 3:
                        term = Term.objects.filter(year_id__time = yearNumber,number = termNumber,year_id__school_id = l)
                        if len(term) > 0:
                            t = term[0]
                            slList[i] = Mark.objects.filter(term_id = t ,subject_id__type=subjectType,subject_id__class_id__block_id__number = blockIndex, tb__lt=level[i],tb__gt=level[i+1],current=True).count()
                            if sum >0: ptList[i] = round(slList[i]*100.0/sum,2)
                    else:
                        year = Year.objects.filter(school_id = l,time = yearNumber)
                        print len(year)
                        if len(year)> 0:
                            y = year[0]
                            slList[i] = TKMon.objects.filter(subject_id__type=subjectType,subject_id__class_id__year_id = y, subject_id__class_id__block_id__number = blockIndex, tb_nam__lt=level[i],tb_nam__gt=level[i+1],current=True).count()
                            print slList[i]
                            if sum >0: ptList[i] = round(slList[i]*100.0/sum,2)

                slSum[i]+= slList[i]
            list.append((l.name,sum,zip(slList,ptList)))

        if sumsum !=0:
            for i in range(numberLevel):
                ptSum[i] = round(slSum[i]*100 / sumsum,2)

        sumList = zip(slSum,ptSum)
    if int(isExcel)==1:
        return countFinalMarkExcel(type,yearNumber,termNumber,subjectIndex,blockIndex,subjectList,list,headerTable,sumList,sumsum)
    tt2 = time.time()
    print (tt2-tt1)/1000.0
    t = loader.get_template(os.path.join('school/report','count_final_mark.html'))
    c = RequestContext(request, {"message":message,
                                 "type":type,
                                 "yearNumber":yearNumber,
                                 "termNumber":termNumber,
                                 "subjectIndex":subjectIndex,
                                 "blockIndex":blockIndex,

                                 "subjectList":subjectList,
                                 "list":list,
                                 "yearList":yearList,
                                 "headerTable":headerTable,
                                 "sumList":sumList,
                                 "sumsum":sumsum,
                                 }
    )
    return HttpResponse(t.render(c))
