# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
#from school.views import *

from django.http import HttpResponse, HttpResponseRedirect
from school.models import *
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from school.utils import *
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.db import transaction
from decorators import need_login, school_function, operating_permission

import os.path
import time
import random

from templateExcel import *
from xlwt import Workbook, XFStyle, Borders, Font, easyxf ,Alignment
import xlwt
import xlrd

def getClassList(selectedYear):

    blockList = Block.objects.filter(school_id=selectedYear.school_id).order_by("number")
    numberBlock = len(blockList)
    maxLength=0
    for b in blockList:
        aClassList = Class.objects.filter(block_id = b,year_id = selectedYear).order_by("id")
        if maxLength < len(aClassList):
            maxLength = len(aClassList)
    classList = [0] * numberBlock * maxLength
    pupilList = [0] * numberBlock * maxLength
    i=0
    for b in blockList:
        j=0
        aClassList = Class.objects.filter(block_id = b,year_id = selectedYear).order_by("id")
        for c in aClassList:
            classList[j*numberBlock+i] = c
            aPupilList=Pupil.objects.filter(classes=c.id,attend__is_member=True).order_by('index','first_name','last_name','birthday')
            pupilList[j*numberBlock+i] = aPupilList
            j+=1
        i+=1
    return blockList,classList,pupilList,numberBlock

def setSizeOfExamList(s,numberPage):

    s.col(0).width=STT_WIDTH
    s.col(1).width=2*STT_WIDTH
    s.col(2).width=LASTNAME_WIDTH
    s.col(3).width=FIRSTNAME_WIDTH
    s.col(4).width=BIRTHDAY_WIDTH

    setHorz =[]
    for i in range(numberPage):
        setHorz.append(((i+1)*50,0,255))
    s.horz_page_breaks = setHorz

def printAList(aList,s,x,y,sbd,name,date,timeExam,subject,school):
    printHeader(s,x,y,school)
    printCongHoa(s,x,y+4,6)
    x+=4
    subjectString = u'DANH SÁCH THI MÔN: '+subject.upper()
    nameString  = u'KỲ THI:'+name.upper()
    dateString  = u'Ngày thi:'+date
    timeString  = u'Thời gian bắt đầu thi:'+timeExam
    s.write_merge(x,x,y,y+9,subjectString,h40)
    s.write_merge(x+1,x+1,y,y+9,nameString,h40)
    s.write_merge(x+3,x+3,y,y+2,u'Phòng thi:.............',h40)
    s.write_merge(x+3,x+3,y+3,y+5,dateString,h40)
    s.write_merge(x+3,x+3,y+6,y+9,timeString,h40)
    x+=4


    s.write_merge(x,x+1,y,y,'Số\nTT',h4)
    s.write_merge(x,x+1,y+1,y+1,'SBD',h4)
    s.write_merge(x,x+1,y+2,y+3,u'Họ và tên',h4)
    s.write_merge(x,x+1,y+4,y+4,u'Ngày sinh',h4)
    s.write_merge(x,x+1,y+5,y+5,u'Lớp',h4)
    s.write_merge(x,x,y+6,y+8,u'Điểm',h4)

    s.write_merge(x,x+1,y+9,y+9,u'Ghi chú',h4)
    s.write(x+1,y+6,"",h4)
    s.write(x+1,y+7,"",h4)
    s.write(x+1,y+8,"",h4)
    x+=1
    i=1
    for p in aList:
        s.write(x+i,y,i,h82)
        s.write(x+i,y+1,sbd+i,h82)
        s.write(x+i,y+2,p.last_name,last_name1)
        s.write(x+i,y+3,p.first_name,first_name1)
        s.write(x+i,y+4,p.birthday.strftime('%d/%m/%Y'),h82)
        className = p.current_class().name
        s.write(x+i,y+5,className,h82)
        s.write(x+i,y+6,"",h82)
        s.write(x+i,y+7,"",h82)
        s.write(x+i,y+8,"",h82)
        s.write(x+i,y+9,"",h82)
        i+=1
def exportToExcel(pupilList,exceltionalPupil,classifiedType,s,name,date,timeExam,subject,maxPupil,school):
    #print len(pupilList)
    #print pupilList
    numberPage = int((len(pupilList)-1)/25 + 1)+3
    setSizeOfExamList(s,numberPage)
    aList=[]
    numberPupil = 0
    x=0
    y=0
    sbd=0
    newSbd = 0
    blockList = Block.objects.filter(school_id = school ).order_by("number")
    for b in blockList:
        if classifiedType =='3':
            pupilList1 = pupilList
        else:
            pupilList1 = pupilList.filter(class_id__block_id = b)

        for p in pupilList1:
            if not p.id in exceltionalPupil:
                numberPupil+=1
                newSbd+=1
                aList.append(p)
                if numberPupil == maxPupil:
                    printAList(aList,s,x,y,sbd,name,date,timeExam,subject,school)
                    aList=[]
                    x+=50
                    sbd=newSbd
                    numberPupil = 0
        if numberPupil !=0:
            printAList(aList,s,x,y,sbd,name,date,timeExam,subject,school)
            aList=[]
            x+=50
            sbd=newSbd
            numberPupil = 0
        if classifiedType=='3':
            break

@need_login
def createListExam(request):
    tt1 = time.time()

    user = request.user

    message=None
    year_id=None
    if year_id==None:
        year_id=get_current_year(request).id

    selectedYear =Year.objects.get(id=year_id)
    try:
        if in_school(request,selectedYear.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    if get_position(request) != 4:
       return HttpResponseRedirect('/school')
    
    blockList,classList,pupilList1,numberBlock = getClassList(selectedYear)
    print request
    if request.method =='POST':
        name =  request.POST["name"]
        date =  request.POST["date"]
        timeExam =  request.POST["time"]
        subject =  request.POST["subject"]
        maxPupil  = int(request.POST["maxPupil"])
        classifiedType = request.POST["classifiedType"]

        print classifiedType
        classSet=[]
        for c in classList:
            if c!=0:
                if request.POST.get(unicode(c.id)):
                    classSet.append(c.id)
        exceptionalPupil=[]
        for xx in request.POST:
            xx = xx.split('_')
            if xx[0]=="pp":
                exceptionalPupil.append(int(xx[1]))
                
        print exceptionalPupil

        if  classifiedType=="1":
            pupilList = Pupil.objects.filter(classes__in=classSet,attend__is_member=True).order_by('classes__block_id__number','first_name','last_name','birthday')
        elif  classifiedType=="2":
            pupilList = Pupil.objects.filter(classes__in=classSet,attend__is_member=True).order_by('classes__block_id__number','classes','first_name','last_name','birthday')
        elif  classifiedType=="3":
            pupilList = Pupil.objects.filter(classes__in=classSet,attend__is_member=True).order_by('first_name','last_name','birthday')


        book = Workbook(encoding = 'utf-8')
        s=book.add_sheet("danh sach thi",True)
        exportToExcel(pupilList,exceptionalPupil,classifiedType,s,name,date,timeExam,subject,maxPupil,selectedYear.school_id)

        response = HttpResponse(mimetype='application/ms-excel')
        response['Content-Disposition'] = u'attachment; filename=%s.xls' % "danhSachThi"
        book.save(response)
        tt2=time.time()
        print (tt2-tt1)
        return response

    tt2=time.time()
    print (tt2-tt1)

    t = loader.get_template(os.path.join('school/exam','create_list_exam.html'))
    c = RequestContext(request, {"message":message,
                                 "classList":classList,
                                 "blockList":blockList,
                                 "numberBlock":numberBlock,
                                 "pupilList":pupilList1,
                                }
                       )
    return HttpResponse(t.render(c))
