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
from school.writeExcel import count1Excel,count2Excel,printDanhHieuExcel,printNoPassExcel,practisingByGradeExcel
from decorators import need_login, school_function, operating_permission

@need_login
def report(request,school_id=None):
    nameSchool = None
    if school_id != None:
        request.session['school_id'] = school_id
        request.session['school_name'] = Organization.objects.get(id = school_id).name
    user = request.user

    message=None
    year_id=None

    if year_id==None:
        year_id=get_current_year(request).id

    selected_year =Year.objects.get(id=year_id)

    try:
        if in_school(request,selected_year.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')

    currentTerm=get_current_term(request)
    yearString = str(currentTerm.number)+"-"+str(currentTerm.number+1)
    firstTerm  =Term.objects.get(year_id=currentTerm.year_id,number=1)
    secondTerm  =Term.objects.get(year_id=currentTerm.year_id,number=2)

    number_no_pass    = TBNam.objects.filter(len_lop=False,year_id = selected_year).count()
    number_exam_again = TBNam.objects.filter(thi_lai=True ,year_id = selected_year).count()
    number_practising_again = TBNam.objects.filter(ren_luyen_lai = True ,year_id = selected_year).count()

    if(currentTerm.number < 3):
        number_all_title = TBHocKy.objects.filter(term_id=currentTerm, danh_hieu_hk__in=['G','TT']).count()
    else:
        number_all_title = TBNam.objects.filter(year_id=selected_year, danh_hieu_nam__in=['G','TT']).count()

    t = loader.get_template(os.path.join('school/report','report.html'))
    c = RequestContext(request, {"message":message,
                                 'yearString':yearString,
                                 'firstTerm':firstTerm,
                                 'secondTerm':secondTerm,
                                 'currentTerm':currentTerm,
                                 'nameSchool':nameSchool,
                                 'number_no_pass':number_no_pass,
                                 'number_exam_again':number_exam_again,
                                 'number_practising_again':number_practising_again,
                                 'number_all_title':number_all_title,
                                }
                       )
    return HttpResponse(t.render(c))


def countTotalPractisingInTerm(term_id):
    slList  =[0,0,0,0,0]
    ptslList=[0,0,0,0,0]
    sum=0.0
    string=['T','K','TB','Y',None]

    selectedTerm=Term.objects.get(id=term_id)
    year_id  = selectedTerm.year_id
    if selectedTerm.number==1:
        for i in range(string.__len__()):
            slList[i]=TBNam.objects.filter(year_id=year_id,term1=string[i]).count()
            sum+=slList[i]
    else:
        for i in range(string.__len__()):
            slList[i]=TBNam.objects.filter(year_id=year_id,term2=string[i]).count()
            sum+=slList[i]

    if sum!=0:
        for i in range(string.__len__()):
            ptslList[i]=slList[i]/sum *100

    return slList,ptslList
def countTotalLearningInTerm(term_id):
    slList  =[0,0,0,0,0,0]
    ptslList=[0,0,0,0,0,0]
    sum=0.0
    string=['G','K','TB','Y','Kem',None]
    for i in range(string.__len__()):
        slList[i]=TBHocKy.objects.filter(term_id=term_id,hl_hk=string[i]).count()
        sum+=slList[i]
    if sum!=0:
        for i in range(string.__len__()):
            ptslList[i]=slList[i]/sum *100

    return slList,ptslList

def countDanhHieuInTerm(term_id):
    slList  =[0,0,0,0]
    ptslList=[0,0,0,0]
    sum=0.0
    string=['G','TT','K',None]
    for i in range(string.__len__()):
        slList[i]=TBHocKy.objects.filter(term_id=term_id,danh_hieu_hk=string[i]).count()
        sum+=slList[i]
    if sum!=0:
        for i in range(string.__len__()):
            ptslList[i]=slList[i]/sum *100

    return slList,ptslList

def countTotalPractisingInYear(year_id):
    slList  =[0,0,0,0,0]
    ptslList=[0,0,0,0,0]
    sum=0.0
    string=['T','K','TB','Y',None]
    for i in range(string.__len__()):
        slList[i]=TBNam.objects.filter(year_id=year_id,year=string[i]).count()
        sum+=slList[i]
    if sum!=0:
        for i in range(string.__len__()):
            ptslList[i]=slList[i]/sum *100

    return slList,ptslList
def countTotalLearningInYear(year_id):
    slList  =[0,0,0,0,0,0]
    ptslList=[0,0,0,0,0,0]
    sum=0.0
    string=['G','K','TB','Y','Kem',None]
    for i in range(string.__len__()):
        slList[i]=TBNam.objects.filter(year_id=year_id,hl_nam=string[i]).count()
        sum+=slList[i]
    if sum!=0:
        for i in range(string.__len__()):
            ptslList[i]=slList[i]/sum *100

    return slList,ptslList

def countDanhHieuInYear(year_id):
    slList  =[0,0,0,0]
    ptslList=[0,0,0,0]
    sum=0.0
    string=['G','TT','K',None]
    for i in range(string.__len__()):
        slList[i]=TBNam.objects.filter(year_id=year_id,danh_hieu_nam=string[i]).count()
        sum+=slList[i]
    if sum!=0:
        for i in range(string.__len__()):
            ptslList[i]=slList[i]/sum *100

    return slList,ptslList
def countPassInYear(year_id):
    slList  =[0,0,0,0,0]
    ptslList=[0,0,0,0,0]

    sum=0.0
    slList[0]=TBNam.objects.filter(year_id=year_id,len_lop=True).count()
    slList[1]=TBNam.objects.filter(year_id=year_id,len_lop=False).count()
    slList[2]=TBNam.objects.filter(year_id=year_id,thi_lai=True).count()
    slList[3]=TBNam.objects.filter(year_id=year_id,ren_luyen_lai=True).count()
    slList[4]=TBNam.objects.filter(year_id=year_id,len_lop=None).count()
    for i in range(slList.__len__()):
        sum+=slList[i]


    if sum!=0:
        for i in range( slList.__len__()):
            ptslList[i]=slList[i]/sum *100

    return slList,ptslList

@need_login
def countInSchool(request,year_id=None):

    user = request.user



    message=None

    if year_id==None:
        year_id=get_current_year(request).id

    selectedYear =Year.objects.get(id=year_id)
    try:
        if in_school(request,selectedYear.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')

    #currentTerm.year_id.school_id.status=1    
    #currentTerm.year_id.school_id.save()

    currentTerm= get_current_term(request)
    hkList,pthkList = countTotalPractisingInTerm(currentTerm.id)
    hlList,pthlList = countTotalLearningInTerm(currentTerm.id)
    ddList,ptddList = countDanhHieuInTerm(currentTerm.id)

    hkcnList=pthkcnList=hlcnList=pthlcnList=passedList=ptPassedList=ddcnList=ptddcnList=None

    if currentTerm.number==2:
        hkcnList,pthkcnList = countTotalPractisingInYear(year_id)
        hlcnList,pthlcnList = countTotalLearningInYear(year_id)
        ddcnList,ptddcnList = countDanhHieuInYear(year_id)
        passedList,ptPassedList  =countPassInYear(year_id)

    selectedYear=Year.objects.get(id=year_id)
    firstTerm = Term.objects.get(year_id=year_id,number=1)
    secondTerm = Term.objects.get(year_id=year_id,number=2)

    yearString = str(selectedYear.time)+"-"+str(selectedYear.time+1)

    t = loader.get_template(os.path.join('school/report','count_in_school.html'))
    c = RequestContext(request, {"message":message,
                                 'yearString':yearString,
                                 'selectedYear':selectedYear,
                                 'firstTerm':firstTerm,
                                 'secondTerm':secondTerm,
                                 'currentTerm':currentTerm,

                                 'hkList':hkList,
                                 'pthkList':pthkList,
                                 'hlList':hlList,
                                 'pthlList':pthlList,
                                 'ddList':ddList,
                                 'ptddList':ptddList,

                                 'hkcnList':hkcnList,
                                 'pthkcnList':pthkcnList,
                                 'hlcnList':hlcnList,
                                 'pthlcnList':pthlcnList,
                                 'ddcnList':ddcnList,
                                 'ptddcnList':ptddcnList,
                                 'passedList':passedList,
                                 'ptPassedList':ptPassedList,
                                }
                       )
    return HttpResponse(t.render(c))

def countPractisingInClassInTerm(class_id,term_id):
    slList  =[0,0,0,0,0]
    ptslList=[0,0,0,0,0]
    sum=0.0

    string=['T','K','TB','Y',None]
    selectedTerm = Term.objects.get(id=term_id)
    year_id = selectedTerm.year_id
    if selectedTerm.number ==1:
        for i in range(string.__len__()):
            slList[i]=TBNam.objects.filter(year_id=year_id,student_id__classes=class_id,term1=string[i],student_id__attend__is_member=True).count()
            sum+=slList[i]
    else:
        for i in range(string.__len__()):
            slList[i]=TBNam.objects.filter(year_id=year_id,student_id__classes=class_id,term2=string[i],student_id__attend__is_member=True).count()
            sum+=slList[i]

    if sum!=0:
        for i in range(string.__len__()):
            ptslList[i]=slList[i]/sum *100

    return slList,ptslList,sum

@need_login
def countPractisingInTerm(request,term_id):

    user = request.user

    selectedTerm=Term.objects.get(id=term_id)
    try:
        if in_school(request,selectedTerm.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')


    message=None
    yearString = str(selectedTerm.year_id.time)+"-"+str(selectedTerm.year_id.time+1)

    selectedYear=Year.objects.get(id=selectedTerm.year_id.id)
    classList=selectedYear.class_set.all().order_by("block_id__number")

    list=[]

    totalSlList=[0,0,0,0,0]
    totalPtList=[0,0,0,0,0]

    for c in classList:
        aslList,aptList,sum =countPractisingInClassInTerm(c.id,term_id)
        list.append([c.name,sum,zip(aslList,aptList)])

        for i in range(5):
            totalSlList[i]+=aslList[i]
    sum=0
    for i in range(5):
      sum+=totalSlList[i]
    if sum!=0:
        for i in range(5):
            totalPtList[i]=float(totalSlList[i])/sum *100

    t = loader.get_template(os.path.join('school/report','count_practising_in_term.html'))
    c = RequestContext(request, {"message":message,
                                 'yearString':yearString,
                                 'selectedTerm':selectedTerm,
                                 'totalSlList':totalSlList,
                                 'totalPtList':totalPtList,
                                 'list':list,
                                }
                       )
    return HttpResponse(t.render(c))

def countPractisingInClassInYear(class_id):
    year_id = Class.objects.get(id=class_id).year_id
    slList  =[0,0,0,0,0]
    ptslList=[0,0,0,0,0]
    sum=0.0
    string=['T','K','TB','Y',None]
    for i in range(string.__len__()):
        slList[i]=TBNam.objects.filter(year_id=year_id, student_id__classes=class_id,year=string[i],student_id__attend__is_member=True).count()
        sum+=slList[i]
    if sum!=0:
        for i in range(string.__len__()):
            ptslList[i]=slList[i]/sum *100

    return slList,ptslList,sum


@need_login
def countPractisingInYear(request,year_id):
    user = request.user

    selectedYear=Year.objects.get(id=year_id)
    try:
        if in_school(request,selectedYear.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')

    message=None
    yearString = str(selectedYear.time)+"-"+str(selectedYear.time+1)

    classList=selectedYear.class_set.all().order_by("block_id__number")
    list=[]

    totalSlList=[0,0,0,0,0]
    totalPtList=[0,0,0,0,0]

    for c in classList:
        aslList,aptList,sum =countPractisingInClassInYear(c.id,year_id)
        list.append([c.name,sum,zip(aslList,aptList)])

        for i in range(5):
            totalSlList[i]+=aslList[i]

    sum=0
    for i in range(5):
      sum+=totalSlList[i]
    if sum!=0:
        for i in range(5):
            totalPtList[i]=float(totalSlList[i])/sum *100
    t = loader.get_template(os.path.join('school/report','count_practising_in_year.html'))
    c = RequestContext(request, {"message":message,
                                 'yearString':yearString,
                                 'selectedYear':selectedYear,
                                 'totalSlList':totalSlList,
                                 'totalPtList':totalPtList,
                                 'list':list,
                                }
                       )
    return HttpResponse(t.render(c))


def countLearningInClassInTerm(class_id,term_id):
    slList  =[0,0,0,0,0,0]
    ptslList=[0,0,0,0,0,0]
    sum=0.0
    string=['G','K','TB','Y','Kem',None]
    for i in range(string.__len__()):
        slList[i]=TBHocKy.objects.filter(term_id=term_id,hl_hk=string[i],student_id__classes=class_id,student_id__attend__is_member=True).count()
        sum+=slList[i]
    if sum!=0:
        for i in range(string.__len__()):
            ptslList[i]=slList[i]/sum *100
    return slList,ptslList,sum

@need_login
def countLearningInTerm(request,term_id):

    user = request.user
    selectedTerm=Term.objects.get(id=term_id)
    try:
        if in_school(request,selectedTerm.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))
    if (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')


    message=None
    yearString = str(selectedTerm.year_id.time)+"-"+str(selectedTerm.year_id.time+1)

    selectedYear=Year.objects.get(id=selectedTerm.year_id.id)

    classList=selectedYear.class_set.all().order_by("block_id__number")
    list=[]

    totalSlList=[0,0,0,0,0,0]
    totalPtList=[0,0,0,0,0,0]

    for c in classList:
        aslList,aptList,sum =countLearningInClassInTerm(c.id,term_id)
        list.append([c.name,sum,zip(aslList,aptList)])

        for i in range(6):
            totalSlList[i]+=aslList[i]
    sum=0
    for i in range(6):
      sum+=totalSlList[i]
    if sum!=0:
        for i in range(6):
            totalPtList[i]=float(totalSlList[i])/sum *100

    t = loader.get_template(os.path.join('school/report','count_learning_in_term.html'))
    c = RequestContext(request, {"message":message,
                                 'yearString':yearString,
                                 'selectedTerm':selectedTerm,
                                 'totalSlList':totalSlList,
                                 'totalPtList':totalPtList,
                                 'list':list,
                                }
                       )
    return HttpResponse(t.render(c))


def countLearningInClassInYear(class_id):
    year_id = Class.objects.get(id=class_id).year_id
    slList  =[0,0,0,0,0,0]
    ptslList=[0,0,0,0,0,0]
    sum=0.0
    string=['G','K','TB','Y','Kem',None]
    for i in range(string.__len__()):
        slList[i]=TBNam.objects.filter(year_id=year_id, student_id__classes=class_id,hl_nam=string[i],student_id__attend__is_member=True).count()
        sum+=slList[i]
    if sum!=0:
        for i in range(string.__len__()):
            ptslList[i]=slList[i]/sum *100

    return slList,ptslList,sum

@need_login
def countLearningInYear(request,year_id):

    user = request.user

    selectedYear=Year.objects.get(id=year_id)
    try:
        if in_school(request,selectedYear.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')

    message=None
    selectedYear=Year.objects.get(id=year_id)
    yearString = str(selectedYear.time)+"-"+str(selectedYear.time+1)

    classList=selectedYear.class_set.all().order_by("block_id__number")
    list=[]

    totalSlList=[0,0,0,0,0,0]
    totalPtList=[0,0,0,0,0,0]

    for c in classList:
        aslList,aptList,sum =countLearningInClassInYear(c.id,year_id)
        list.append([c.name,sum,zip(aslList,aptList)])

        for i in range(6):
            totalSlList[i]+=aslList[i]
    sum=0
    for i in range(6):
      sum+=totalSlList[i]
    if sum!=0:
        for i in range(6):
            totalPtList[i]=float(totalSlList[i])/sum *100

    t = loader.get_template(os.path.join('school/report','count_learning_in_year.html'))
    c = RequestContext(request, {"message":message,
                                 'yearString':yearString,
                                 'totalSlList':totalSlList,
                                 'totalPtList':totalPtList,
                                 'list':list,
                                }
                       )
    return HttpResponse(t.render(c))


def countAllInClassInTerm(class_id,term_id):
    slList  =[0,0,0,0]
    ptslList=[0,0,0,0]
    sum=0.0
    string=['G','TT','K',None]
    for i in range(string.__len__()):
        slList[i]=TBHocKy.objects.filter(term_id=term_id, student_id__classes=class_id,danh_hieu_hk=string[i],student_id__attend__is_member=True).count()
        sum+=slList[i]
    if sum!=0:
        for i in range(string.__len__()):
            ptslList[i]=slList[i]/sum *100

    return slList,ptslList ,sum

@need_login
def countAllInTerm(request,term_id):

    user = request.user

    selectedTerm=Term.objects.get(id=term_id)
    try:
        if in_school(request,selectedTerm.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')

    message=None
    selectedTerm=Term.objects.get(id=term_id)
    yearString = str(selectedTerm.year_id.time)+"-"+str(selectedTerm.year_id.time+1)

    selectedYear=Year.objects.get(id=selectedTerm.year_id.id)

    classList=selectedYear.class_set.all().order_by("block_id__number")
    list=[]

    totalSlList=[0,0,0,0]
    totalPtList=[0,0,0,0]

    for c in classList:
        aslList,aptList,sum =countAllInClassInTerm(c.id,term_id)
        list.append([c.name,sum,zip(aslList,aptList)])

        for i in range(4):
            totalSlList[i]+=aslList[i]
    sum=0
    for i in range(4):
      sum+=totalSlList[i]
    if sum!=0:
        for i in range(4):
            totalPtList[i]=float(totalSlList[i])/sum *100

    t = loader.get_template(os.path.join('school/report','count_all_in_term.html'))
    c = RequestContext(request, {"message":message,
                                 "selectedTerm":selectedTerm,
                                 'yearString':yearString,
                                 'totalSlList':totalSlList,
                                 'totalPtList':totalPtList,
                                 'list':list,
                                }
                       )
    return HttpResponse(t.render(c))


def countAllInClassInYear(class_id):
    year_id = Class.objects.get(id=class_id).year_id
    slList=[0,0,0,0]
    ptList=[0,0,0,0]

    slList[0]=TBNam.objects.filter(year_id=year_id, student_id__classes=class_id,danh_hieu_nam='G',student_id__attend__is_member=True).count()
    slList[1]=TBNam.objects.filter(year_id=year_id, student_id__classes=class_id,danh_hieu_nam='TT',student_id__attend__is_member=True).count()
    slList[3]=TBNam.objects.filter(year_id=year_id, student_id__classes=class_id,danh_hieu_nam=None,student_id__attend__is_member=True).count()
    #slList[2]=
    #slList[2]=TBNam.objects.filter(year_id=year_id,student_id__classes=class_id,len_lop=True).count()
    #slList[3]=TBNam.objects.filter(year_id=year_id,student_id__classes=class_id,len_lop=False).count()
    #slList[4]=TBNam.objects.filter(year_id=year_id,student_id__classes=class_id,thi_lai=True).count()
    #slList[5]=TBNam.objects.filter(year_id=year_id,student_id__classes=class_id,ren_luyen_lai=True).count()    
    #sl1=TBNam.objects.filter(year_id=year_id,student_id__classes=class_id,len_lop=True).count()
    #sl2=TBNam.objects.filter(year_id=year_id,student_id__classes=class_id,len_lop=False).count()
    #sl3=TBNam.objects.filter(year_id=year_id,student_id__classes=class_id,thi_lai=True).count()
    #sl4=TBNam.objects.filter(year_id=year_id,student_id__classes=class_id,ren_luyen_lai=True).count()    
    sum = Pupil.objects.filter(classes=class_id,attend__is_member=True).count()

    #slList[2] = sum-sl1-sl2-sl3-sl4            

    if (sum!=0):
        for i in range(3):
            ptList[i]=float(slList[i])/sum *100

    return slList,ptList,sum

@need_login
def countAllInYear(request,year_id):

    user = request.user

    selectedYear=Year.objects.get(id=year_id)
    try:
        if in_school(request,selectedYear.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')

    message=None
    selectedYear=Year.objects.get(id=year_id)
    yearString = str(selectedYear.time)+"-"+str(selectedYear.time+1)


    classList=selectedYear.class_set.all().order_by("block_id__number")
    list=[]

    totalSlList=[0,0,0,0,0,0,0]
    totalPtList=[0,0,0,0,0,0,0]

    for c in classList:
        aslList,aptList,sum =countAllInClassInYear(c.id,year_id)
        list.append([c.name,sum,zip(aslList,aptList)])

        for i in range(7):
            totalSlList[i]+=aslList[i]
    sum=0
    for i in range(2,7):
      sum+=totalSlList[i]
    if sum!=0:
        for i in range(7):
            totalPtList[i]=float(totalSlList[i])/sum *100

    t = loader.get_template(os.path.join('school/report','count_all_in_year.html'))
    c = RequestContext(request, {"message":message,
                                 'yearString':yearString,
                                 'totalSlList':totalSlList,
                                 'totalPtList':totalPtList,
                                 'list':list,
                                }
                       )
    return HttpResponse(t.render(c))


@need_login
def count1(request,year_id=None,number=None,isExcel=0,):

    user = request.user

    currentTerm=get_current_term(request)
    try:
        if in_school(request,currentTerm.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')

    tt1=time.time()
    message=None
    if year_id==None:
        selectedTerm =get_current_term(request)
        selectedYear =get_current_year(request)
        year_id   = selectedTerm.year_id.id
        if selectedTerm.number==3:
            term_id = Term.objects.get(year_id=selectedYear.id,number=2).id
            number=2
        else:
            term_id = selectedTerm.id
            number = selectedTerm.number
    else:
        selectedYear=Year.objects.get(id=year_id)
        if int(number)<3:
            term_id = Term.objects.get(year_id=selectedYear.id,number=number).id
    number=int(number)
    blockList = Block.objects.filter(school_id=selectedYear.school_id)
    list=[]
    notFinishLearning=0
    notFinishPractising=0
    notFinishAll    =0
    allSlList=[0,0,0,0,0,0,0,0,0,0,0]
    allPtList=[0,0,0,0,0,0,0,0,0,0,0]
    allList=[]
    sumsumsum=0
    for b in blockList:
        classList = Class.objects.filter(block_id=b,year_id=selectedYear.id)
        list1=[]
        totalSlList=[0,0,0,0,0,0,0,0,0,0,0]
        totalPtList=[0,0,0,0,0,0,0,0,0,0,0]
        sumsum=0
        for c in classList:
            if int(number)<3:
                aslList,aptList,sum   =countLearningInClassInTerm(c.id,term_id)
                aslList1,aptList1,sum =countPractisingInClassInTerm(c.id,term_id)
                aslList2,aptList2,sum =countAllInClassInTerm(c.id,term_id)
            else:
                aslList,aptList,sum =countLearningInClassInYear(c.id)
                aslList1,aptList1,sum =countPractisingInClassInYear(c.id)
                aslList2,aptList2,sum =countAllInClassInYear(c.id)

            notFinishLearning+=aslList[5]
            notFinishPractising+=aslList1[4]
            notFinishAll      +=aslList2[3]
            aslList.pop(5)
            aptList.pop(5)
            aslList1.pop(4)
            aptList1.pop(4)

            aslList2.pop(3)
            aptList2.pop(3)
            aslList2.pop(2)
            aptList2.pop(2)

            slList = aslList+aslList1+aslList2
            ptList = aptList+aptList1+aptList2
            list1.append([c.name,sum,zip(slList,ptList)])

            for i in range(11):
                totalSlList[i]+=slList[i]
                allSlList[i]+=slList[i]
            sumsum+=sum
            sumsumsum+=sum
        if sumsum!=0:
            for i in range(11):
                totalPtList[i]=float(totalSlList[i])/sumsum *100
        list.append([b,sumsum,zip(totalSlList,totalPtList),list1])
    if sumsumsum!=0:
        for i in range(11):
            allPtList[i]=float(allSlList[i])/sumsumsum *100
        allList=zip(allSlList,allPtList)

    if notFinishLearning!=0:
        message=str(notFinishLearning)+ u' hs chưa có học lực'
    if notFinishPractising!=0:
        if message!='':
            message+=', '
        message+=unicode(notFinishPractising)+ u' hs chưa có hạnh kiểm'
    if notFinishAll!=0:
        if message!='':
            message+=', '
        message+=unicode(notFinishAll)+ u' hs chưa xét danh hiệu'
    if message!=None:
        message=u'Còn ' +message
    tt2=time.time()
    print tt2-tt1
    if isExcel:
        return count1Excel(year_id,number,list,sumsumsum,allList)

    t = loader.get_template(os.path.join('school/report','count1.html'))
    c = RequestContext(request, {'message':message,
                                 'list':list,
                                 'sumsumsum':sumsumsum,
                                 'allList':allList,
                                 'year_id':year_id,
                                 'number':number,
                                 })

    return HttpResponse(t.render(c))
def listSubject(year_id):
    subjectList=Subject.objects.filter(class_id__year_id=year_id).order_by("index",'name')
    list=[]
    for s in subjectList:
        if not (s.type in list):
            list.append(s.type)
    return list
@need_login
def count2(request,type=None,modeView=None,year_id=None,number=None,index=-1,isExcel=None):
    tt1=time.time()
    user = request.user

    currentTerm=get_current_term(request)
    try:
        if in_school(request,currentTerm.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')

    selectedTerm =get_current_term(request)
    currentNumber=selectedTerm.number

    if year_id==None:

        selectedYear =get_current_year(request)
        year_id   = selectedTerm.year_id.id
        if selectedTerm.number==3:
            term_id = Term.objects.get(year_id=selectedYear.id,number=2).id
            number=2
        else:
            term_id = selectedTerm.id
            number = selectedTerm.number
    else:
        selectedYear=Year.objects.get(id=year_id)
        if int(number)<3:
            term_id = Term.objects.get(year_id=selectedYear.id,number=number).id
    subjectList=listSubject(year_id)
    number=int(number)
    type=int(type)
    modeView=int(modeView)
    sumsumsum=0
    allList=[]
    list=[]
    subjectType=[]
    headerTable=[]
    if index!=-1:

        subjectType = subjectList[int(index)-1]
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

        sumsumsum=0
        allSlList=[0]*numberLevel
        allPtList=[0]*numberLevel
        list=[]
        if modeView==1:
            blockList = Block.objects.filter(school_id=selectedYear.school_id)
            for b in blockList:
                classList = Class.objects.filter(block_id=b,year_id=selectedYear.id)
                totalSlList=[0]*numberLevel
                totalPtList=[0]*numberLevel
                sumsum=0
                list1=[]
                for c in classList:
                    slList=[0]*numberLevel
                    ptList=[0]*numberLevel

                    selectedSubjectList = Subject.objects.filter(type=subjectType,class_id=c.id)
                    if len(selectedSubjectList)==0: continue
                    else: selectedSubject=selectedSubjectList[0]

                    if type==1:
                        if number<3:
                            for i in range(numberLevel):
                                slList[i]=Mark.objects.filter(term_id=term_id,subject_id=selectedSubject.id,tb__lt=level[i],tb__gt=level[i+1],current=True).count()
                        else:
                            for i in range(numberLevel):
                                slList[i]=TKMon.objects.filter(subject_id=selectedSubject.id,tb_nam__lt=level[i],tb_nam__gt=level[i+1],current=True).count()
                    elif type==2:
                        for i in range(numberLevel):
                            slList[i]=Mark.objects.filter(term_id=term_id,subject_id=selectedSubject.id,ck__lt=level[i],ck__gt=level[i+1],current=True).count()

                    sum=Pupil.objects.filter(classes=c.id,attend__is_member=True).count()
                    for i in range(numberLevel):
                        if sum!=0:
                            ptList[i]=float(slList[i])/sum*100
                        totalSlList[i]+=slList[i]
                        allSlList[i]+=slList[i]

                    if selectedSubject.teacher_id:
                        teacherName=selectedSubject.teacher_id.last_name+' '+selectedSubject.teacher_id.first_name
                        list1.append([c.name,sum,teacherName,zip(slList,ptList)])
                    else:
                        list1.append([c.name,sum,' ',zip(slList,ptList)])
                    sumsum+=sum
                    sumsumsum+=sum

                if sumsum!=0:
					for i in range(numberLevel):
						totalPtList[i]=float(totalSlList[i])/sumsum *100
                list.append(['Khối '+str(b.number),sumsum,zip(totalSlList,totalPtList),list1])

       #######################################################################
        elif modeView==2:
            selectedSubjectList =Subject.objects.filter(type=subjectType,class_id__year_id=year_id,teacher_id__isnull=False).order_by('teacher_id__first_name','teacher_id__last_name','teacher_id__id')
            length=len(selectedSubjectList)
            previousTeacher=None
            for (ii,s) in enumerate(selectedSubjectList):
                ok=False
                slList=[0] * numberLevel
                ptList=[0] * numberLevel
                teacherName = s.teacher_id.last_name+' '+s.teacher_id.first_name
                if  s.teacher_id !=previousTeacher:
                    if ii!=0:
                        if sumsum!=0:
                            for i in range(numberLevel):
                                totalPtList[i]=float(totalSlList[i])/sumsum *100
                        list.append(['Tổng',sumsum,zip(totalSlList,totalPtList),list1])

                    totalSlList=[0] * numberLevel
                    totalPtList=[0] * numberLevel
                    sumsum=0
                    list1=[]
                if ii==length-1:
                    ok=True
                previousTeacher=s.teacher_id
                if type==1:
                    if number<3:
                        for i in range(numberLevel):
                            slList[i]=Mark.objects.filter(term_id=term_id,subject_id=s.id,tb__lt=level[i],tb__gt=level[i+1],current=True).count()
                    else:
                        for i in range(numberLevel):
                            slList[i]=TKMon.objects.filter(subject_id=s.id,tb_nam__lt=level[i],tb_nam__gt=level[i+1],current=True).count()
                elif type==2:
                    for i in range(numberLevel):
                        slList[i]=Mark.objects.filter(term_id=term_id,subject_id=s.id,ck__lt=level[i],ck__gt=level[i+1],current=True).count()

                sum=Pupil.objects.filter(classes=s.class_id.id,attend__is_member=True).count()
                for i in range(numberLevel):
                    if sum!=0:
                        ptList[i]=float(slList[i])/sum*100
                    totalSlList[i]+=slList[i]
                    allSlList[i]+=slList[i]

                list1.append([s.class_id.name,sum,teacherName,zip(slList,ptList)])
                sumsum+=sum
                sumsumsum+=sum
                if ok:
                    if sumsum!=0:
                        for i in range(numberLevel):
                            totalPtList[i]=float(totalSlList[i])/sumsum *100
                    list.append(['Tổng',sumsum,zip(totalSlList,totalPtList),list1])

        if sumsumsum!=0:
           for i in range(numberLevel):
               allPtList[i]=float(allSlList[i])/sumsumsum *100
        allList=zip(allSlList,allPtList)
        if isExcel=='1':
            return count2Excel(year_id,number,subjectType,type,modeView,list,allList,sumsumsum,isComment)

    tt2=time.time()
    print tt2-tt1
    t = loader.get_template(os.path.join('school/report','count2.html'))
    c = RequestContext(request, {
                                 'type':type,
                                 'subjectList':subjectList,
                                 'year_id':year_id,
                                 'number':number,
                                 'index':index,
                                 'list':list,
                                 'allList':allList,
                                 'sumsumsum':sumsumsum,
                                 'subjectName':subjectType,
                                 'currentNumber':currentNumber,
                                 'modeView':modeView,
                                 'headerTable':headerTable
                                 })
    return HttpResponse(t.render(c))

@need_login
def printDanhHieu(request,year_id=None, term_number=None,type=None,isExcel=None):
    tt1=time.time()
    user = request.user
    current_term = get_current_term(request)
    try:
        if in_school(request,current_term.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')

    if year_id==None:
        term_id=current_term.id
        selected_term = current_term
        term_number = current_term.number
        year_id = selected_term.year_id.id
    else:
        selected_term = Term.objects.get(year_id=year_id, number=term_number)
        term_id = selected_term.id

    list=[]
    if type == None:
        type = 1
    term_number=int(term_number)
    type = int(type)
    blockList = Block.objects.filter(school_id=selected_term.year_id.school_id).order_by("number")
    for b in blockList:
        classList = Class.objects.filter(block_id=b,year_id=selected_term.year_id.id).order_by("id")
        for c in classList:
            if int(term_number)<3:
                if type == 1:
                    danhHieus=TBHocKy.objects.filter(term_id=term_id, student_id__classes=c.id,danh_hieu_hk__in=['G','TT'],student_id__attend__is_member=True).order_by("danh_hieu_hk","student_id__index")
                elif type == 2:
                    danhHieus=TBHocKy.objects.filter(term_id=term_id, student_id__classes=c.id,danh_hieu_hk='G',student_id__attend__is_member=True).order_by("student_id__index")
                elif type == 3:
                    danhHieus=TBHocKy.objects.filter(term_id=term_id, student_id__classes=c.id,danh_hieu_hk='TT',student_id__attend__is_member=True).order_by("student_id__index")
            else:
                if   type==1:
                    danhHieus=TBNam.objects.filter(year_id=year_id, student_id__classes=c.id,danh_hieu_nam__in=['G','TT'],student_id__attend__is_member=True).order_by("danh_hieu_nam","student_id__index")
                elif type==2:
                    danhHieus=TBNam.objects.filter(year_id=year_id, student_id__classes=c.id,danh_hieu_nam='G',student_id__attend__is_member=True).order_by("student_id__index")
                elif type==3:
                    danhHieus=TBNam.objects.filter(year_id=year_id, student_id__classes=c.id,danh_hieu_nam='TT',student_id__attend__is_member=True).order_by("student_id__index")
            list.append((c.name,danhHieus))
    if isExcel:
        return printDanhHieuExcel(list,term_number,type,selected_term)
    if(term_number < 3):
        number_good = TBHocKy.objects.filter(term_id=term_id, danh_hieu_hk='G').count()
        number_advanced = TBHocKy.objects.filter(term_id=term_id, danh_hieu_hk='TT').count()
        number_all = number_good + number_advanced
    else:
        number_good = TBNam.objects.filter(year_id=year_id, danh_hieu_nam='G').count()
        number_advanced = TBNam.objects.filter(year_id=year_id, danh_hieu_nam='TT').count()
        number_all = number_good + number_advanced
    tt2=time.time()
    print tt2-tt1
    t = loader.get_template(os.path.join('school/report','print_danh_hieu.html'))
    c = RequestContext(request, {
                                 'list':list,
                                 'type':type,
                                 'termNumber':term_number,
                                 'year_id':year_id,
                                 'number_good':number_good,
                                 'number_advanced':number_advanced,
                                 'number_all':number_all,
                                 })
    return HttpResponse(t.render(c))

@need_login
def printNoPass(request,type=None,isExcel=None):
    tt1=time.time()

    user = request.user
    currentYear = get_current_year(request)
    try:
        if in_school(request,currentYear.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')
    if type==None:
        type=1
    list=[]
    selected_year = currentYear
    type = int(type)
    blockList = Block.objects.filter(school_id=selected_year.school_id).order_by("number")
    for b in blockList:
        classList = Class.objects.filter(block_id=b,year_id=selected_year.id).order_by("id")
        for c in classList:
            if   type==1:
                pupils=TBNam.objects.filter(year_id=selected_year, student_id__classes=c.id,len_lop=False,student_id__attend__is_member=True).order_by("student_id__index")
            elif type==2:
                pupils=TBNam.objects.filter(year_id=selected_year, student_id__classes=c.id,thi_lai=True,student_id__attend__is_member=True).order_by("student_id__index")
            elif type==3:
                pupils=TBNam.objects.filter(year_id=selected_year, student_id__classes=c.id,ren_luyen_lai=True,student_id__attend__is_member=True).order_by("student_id__index")
            list.append((c.name,pupils))
    if isExcel:
        return printNoPassExcel(list,type,selected_year)

    tt2=time.time()
    print tt2-tt1
    t = loader.get_template(os.path.join('school/report','print_no_pass.html'))
    c = RequestContext(request, {
                                 'list':list,
                                 'type':type,
                                 })
    return HttpResponse(t.render(c))

@need_login
def countSMS(request,type=None,day=None,month=None,year=None,day1=None,month1=None,year1=None):
    tt1=time.time()

    user = request.user
    currentTerm = get_current_term(request)
    try:
        if in_school(request,currentTerm.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')

    if request.method == 'POST':
        firstDay =request.POST['firstDate'].split('/')
        secondDay =request.POST['secondDate'].split('/')
        day=int(firstDay[0])
        month=int(firstDay[1])
        year=int(firstDay[2])

        day1=int(secondDay[0])
        month1=int(secondDay[1])
        year1=int(secondDay[2])

        type =request.POST['type1']
    if (type==None):
        type=1
    if day==None:
        day1   = datetime.now().day
        month1 = datetime.now().month
        year1  = datetime.now().year

        day_of_before_month = datetime.fromordinal(datetime.now().toordinal()-30)
        day = day_of_before_month.day
        month = day_of_before_month.month
        year = day_of_before_month.year

    firstDay  =datetime(year,month,day)
    secondDay =datetime(year1,month1,day1,23, 59, 0)
    school=get_school(request)
    if   int(type)==1:
        list=sms.objects.filter(created__gte=firstDay,created__lte=secondDay, sender__userprofile__organization=school).order_by("-created")
    elif int(type)==2:
        list=sms.objects.filter(created__gte=firstDay,created__lte=secondDay, sender__userprofile__organization=school,success=True).order_by("-created")
    elif int(type)==3:
        list=sms.objects.filter(created__gte=firstDay,created__lte=secondDay, sender__userprofile__organization=school,success=False).order_by("-created")
    tt2=time.time()
    print "time",tt2-tt1
    t = loader.get_template(os.path.join('school/report','countSMS.html'))
    c = RequestContext(request, {
                                'list':list,
                                'type':type,

                                'day':day,
                                'month':month,
                                'year':year,

                                'day1':day1,
                                'month1':month1,
                                'year1':year1,
                                 })
    return HttpResponse(t.render(c))

