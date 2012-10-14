# -*- coding: utf-8 -*-
# author: luulethe@gmail.com 

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.db import transaction
import os.path 
import time
import datetime
from decorators import need_login
from school.models import Term, Mark, Subject, Pupil, TKMon, SUBJECT_LIST, Class, Teacher, HistoryMark
from school.utils import get_current_term, get_position, in_school, get_level, to_en1, get_school, get_student
from sms.utils import sendSMS
from templateExcel import  MAX_COL,CHECKED_DATE
from number_col import  NUMBER_COL_MIN
LOCK_MARK =False
ENABLE_CHANGE_MARK=True
e=0.00000001
def getDecodeMark(markList):
    
    decodeMarkList=[]
    for m in markList:
        decodeMarkList.append(m.convertToList())
    maxColMieng=0
    maxCol15Phut=0
    maxColMotTiet=0
    for d in decodeMarkList:
        if maxColMieng < d[0][0]:
            maxColMieng=d[0][0]
        if maxCol15Phut < d[1][0]:
            maxCol15Phut=d[1][0]
        if maxColMotTiet < d[2][0]:
            maxColMotTiet=d[2][0]

    return decodeMarkList,maxColMieng,maxCol15Phut,maxColMotTiet
def zipzip(list1,list2,list3=None,list4=None,list5=None):
    length1 = len(list1)
    length2 = len(list2)
    if length1 != length2:
        print length1
        print length2
        raise Exception("the lengths are not equal")

    # check mark correspond with each student
    for (p,m) in zip(list1,list2):
        if p.id != m.student_id.id:
            raise Exception("don't correspond")

    if list3 != None:
        length3 = len(list3)
        if length1 != length3:
            raise Exception("the lengths are not equal")
        if list4 != None:
            length4 = len(list4)
            if length1 != length4:
                raise Exception("the lengths are not equal")
            if list5 != None:
                length5 = len(list5)
                if length1 != length5:
                    raise Exception("the lengths are not equal")
                return zip(list1,list2,list3,list4,list5)
            return zip(list1,list2,list3,list4)
        return zip(list1,list2,list3)
    return zip(list1,list2)

def getMark(subjectChoice,selectedTerm):
    selectedSubject = Subject.objects.get(id= subjectChoice)
    class_id = selectedSubject.class_id.id
    pupilList = Pupil.objects.filter(classes=class_id,attend__is_member=True).order_by('index','first_name','last_name','birthday').distinct()
    tbhk1List=[]
    tbnamList=[]
    if selectedTerm.number==1:            
        markList = Mark.objects.filter(term_id=selectedTerm.id,subject_id=subjectChoice,current=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday')
        decodeMarkList,maxColMieng,maxCol15Phut,maxColMotTiet = getDecodeMark(markList)
        list=zipzip(pupilList,markList,decodeMarkList)
    else:
        beforeTerm = Term.objects.get(year_id=selectedTerm.year_id,number=1).id
        markList = Mark.objects.filter(term_id=selectedTerm.id,subject_id=subjectChoice,current=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday')
        tbhk1List = Mark.objects.filter(term_id=beforeTerm,subject_id=subjectChoice,current=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday')
        tbnamList = TKMon.objects.filter(subject_id=subjectChoice,current=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday')
                    
        decodeMarkList,maxColMieng,maxCol15Phut,maxColMotTiet = getDecodeMark(markList)
        list=zipzip(pupilList,markList,decodeMarkList,tbhk1List,tbnamList)

    return   list,maxColMieng,maxCol15Phut,maxColMotTiet

#@transaction.commit_on_success    
def min_col(subject):
    try:
        name = subject.name
        c = subject.class_id.block_id.number
        i = -1
        for s in SUBJECT_LIST:
            i+=1
            if s == name: break;
        return NUMBER_COL_MIN[c-6][i][0],NUMBER_COL_MIN[c-6][i][1],NUMBER_COL_MIN[c-6][i][2]
    except Exception as e :
        return NUMBER_COL_MIN[0][0][0],NUMBER_COL_MIN[0][0][1],NUMBER_COL_MIN[0][0][2]
@need_login
def markTable(request,term_id=-1,class_id=-1,subject_id=-1,move=None):
    tt1=time.time()
    user = request.user
    termChoice = term_id
    classChoice = class_id
    subjectChoice = subject_id
    if termChoice==-1:
        selectedTerm = get_current_term(request)
        if selectedTerm.number ==3:
            selectedTerm=Term.objects.get(year_id=selectedTerm.year_id,number=2)
    else             :  selectedTerm=Term.objects.get(id=termChoice) 

    try:        
        if in_school(request,selectedTerm.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))
    
    enableChangeMark=True
    enableSendSMS   =True
    isSchool = True
    if get_position(request) != 4:
        if user.userprofile.organization.level!='T':
            enableChangeMark=False
            enableSendSMS   =False
            isSchool = False
        else:
            return HttpResponseRedirect('/school')

    message = None
    list=None
    subjectList=None
    termChoice = selectedTerm.id    
    yearChoice = selectedTerm.year_id.id
            
    termList= Term.objects.filter(year_id=yearChoice,number__lt=3).order_by('number')    
    classList = Class.objects.filter(year_id=yearChoice).order_by("block_id","id")
    
    selectedClass=None
    if classChoice !=-1: 
        subjectList = Subject.objects.filter(class_id=classChoice,primary__in=[0,selectedTerm.number,3,4]).order_by("index",'name')
        selectedClass = Class.objects.get(id=classChoice)
   
    selectedSubject=None
    maxColMieng=0
    maxCol15Phut=0
    maxColMotTiet=0
    max_col_mieng = 0
    max_col_15phut = 0
    max_col_mot_tiet = 0
    if subjectChoice!=-1:
        selectedSubject = Subject.objects.get(id=subjectChoice)
        list,maxColMieng,maxCol15Phut,maxColMotTiet = getMark(subjectChoice,selectedTerm)
        max_col_mieng,max_col_15phut,max_col_mot_tiet = min_col(selectedSubject)
    lengthList=0            
    if list!=None:        
        lengthList=list.__len__()  
    type=1

    firstLoop=[]
    for i in range(1,4):
        firstLoop.append(i)
        
    secondLoop=[]
    for i in range(1,MAX_COL+1):
        secondLoop.append(i)
        
    timeToEdit = int(selectedTerm.year_id.school_id.get_setting('lock_time'))*60
    now    = datetime.datetime.now()
    timeNow= int((now-CHECKED_DATE).total_seconds())

    t = loader.get_template(os.path.join('school','mark/mark_table.html'))
    
    c = RequestContext(request, { 
                                'message' : message,
                                'enableChangeMark':enableChangeMark,
                                'enableSendSMS':enableChangeMark,

                                'classList':classList,
                                'subjectList':subjectList,
                                'termList':termList,
                                'list':list,
                                
                                'classChoice':classChoice,
                                'subjectChoice':subjectChoice,
                                'termChoice':termChoice,            
                                                  
                                'selectedTerm':selectedTerm,
                                'selectedClass':selectedClass,
                                'selectedSubject':selectedSubject,
                                
                                'lengthList':lengthList,
                                'move':move,
                                'type':type,
                                'firstLoop':firstLoop,
                                'secondLoop':secondLoop,
                                'MAX_VIEW_COL_MIENG':max_col_mieng,
                                'MAX_VIEW_COL_15PHUT':max_col_15phut,
                                'MAX_VIEW_COL_MOT_TIET':max_col_mot_tiet,
                                'MAX_COL':MAX_COL,
                                'maxColMieng'  :min(MAX_COL,max(maxColMieng+1,max_col_mieng)),
                                'maxCol15Phut' :min(MAX_COL,max(maxCol15Phut+1,max_col_15phut)),
                                'maxColMotTiet':min(MAX_COL,max(maxColMotTiet+1,max_col_mot_tiet)),

                                'timeToEdit':timeToEdit,
                                'timeNow':timeNow,
                                'isSchool':isSchool,
                                }
                       )
    tt2=time.time()
    print "time.......................",(tt2-tt1)
    return HttpResponse(t.render(c))

@need_login
def markForTeacher(request,type=1,term_id=-1,subject_id=-1,move=None):
    tt1=time.time()
    user = request.user
    try:
        idTeacher =request.user.teacher.id
        classChoice   =-1
        termChoice    = term_id
        subjectChoice = subject_id     
        selectedSubject=None
        if subjectChoice!=-1:
            selectedSubject=Subject.objects.get(id=subjectChoice)    
            if int(type)==1:
                if idTeacher != selectedSubject.teacher_id.id:
                    return HttpResponseRedirect('/school')
            else:
                if selectedSubject.class_id.teacher_id.id != idTeacher:
                    return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect('/school')

    enableChangeMark=True
    enableSendSMS   =True        
    message = None            
    list=None
    subjectList=None
    isSchool = True
    currentTerm =get_current_term(request) 
    if type==None: type=1
    if termChoice==-1:  
        selectedTerm=currentTerm
        if selectedTerm.number ==3:
            selectedTerm=Term.objects.get(year_id=selectedTerm.year_id,number=2)

    else             :  selectedTerm=Term.objects.get(id=termChoice)
    
    if (selectedTerm.year_id.time<currentTerm.year_id.time) | ((selectedTerm.year_id.time==currentTerm.year_id.time) & (selectedTerm.number<currentTerm.number)):
        enableChangeMark=False
    termChoice = selectedTerm.id    
    yearChoice = selectedTerm.year_id.id
            
    termList= Term.objects.filter(year_id=yearChoice,number__lt=3).order_by('number')    
    if int(type)==1:
        subjectList=Subject.objects.filter(teacher_id=idTeacher,class_id__year_id=yearChoice,primary__in=[0,selectedTerm.number,3,4]).order_by("class_id__block_id__number","index")
    else:
        teaching_class=request.user.teacher.current_homeroom_class()
        subjectList=Subject.objects.filter(class_id=teaching_class,primary__in=[0,selectedTerm.number,3,4]).order_by("index")
        if subjectChoice!=-1:
            if selectedSubject.teacher_id==None:
                enableChangeMark=False
            elif  selectedSubject.teacher_id.id != idTeacher:
                enableChangeMark=False
                
    maxColMieng=0
    maxCol15Phut=0
    maxColMotTiet=0
    max_col_mieng = 0
    max_col_15phut = 0
    max_col_mot_tiet = 0

    if subjectChoice!=-1:
        list=getMark(subjectChoice,selectedTerm)
        list,maxColMieng,maxCol15Phut,maxColMotTiet=getMark(subjectChoice,selectedTerm)
        max_col_mieng,max_col_15phut,max_col_mot_tiet = min_col(selectedSubject)

    lengthList=0            
    if list!=None:        
        lengthList=list.__len__()
        
    firstLoop=[]
    for i in range(1,4):
        firstLoop.append(i)

    secondLoop=[]
    for i in range(1,MAX_COL+1):
        secondLoop.append(i)

    timeToEdit = int(selectedTerm.year_id.school_id.get_setting('lock_time'))*60
    now    = datetime.datetime.now()
    timeNow= int((now-CHECKED_DATE).total_seconds())

    print "lock time:",selectedTerm.year_id.school_id.get_setting('lock_time')

    t = loader.get_template(os.path.join('school','mark/mark_table.html'))
    c = RequestContext(request, { 
                                'message' : message,
                                'type':type,
                                'enableChangeMark':enableChangeMark,
                                'enableSendSMS':enableChangeMark,

                                'subjectList':subjectList,
                                'termList':termList,
                                'list':list,
                                
                                'subjectChoice':subjectChoice,
                                'termChoice':termChoice,
                                'classChoice':classChoice,            
                                                  
                                'selectedSubject':selectedSubject,
                                'selectedTerm':selectedTerm,
                                
                                'lengthList':lengthList,
                                'move':move,
                                'firstLoop':firstLoop,
                                'secondLoop':secondLoop,
                                'MAX_VIEW_COL_MIENG':max_col_mieng,
                                'MAX_VIEW_COL_15PHUT':max_col_15phut,
                                'MAX_VIEW_COL_MOT_TIET':max_col_mot_tiet,
                                'MAX_COL':MAX_COL,
                                'maxColMieng'  :min(MAX_COL,max(maxColMieng+1,max_col_mieng)),
                                'maxCol15Phut' :min(MAX_COL,max(maxCol15Phut+1,max_col_15phut)),
                                'maxColMotTiet':min(MAX_COL,max(maxColMotTiet+1,max_col_mot_tiet)),

                                'timeToEdit':timeToEdit,
                                'timeNow':timeNow,
                                'now':now,
                                'isSchool':isSchool,
                                }
                       )
    
    tt2=time.time()
    print (tt2-tt1)

    return HttpResponse(t.render(c))

@need_login
def markForAStudent(request,class_id,student_id,term_id=None):

    user = request.user

    selectedClass = Class.objects.get(id__exact = class_id)
    try:
        if in_school(request,selectedClass.year_id.school_id) == False:
            return HttpResponseRedirect('/school')

    except Exception as e:
        return HttpResponseRedirect(reverse('index'))

    message = None
    student=Pupil.objects.get(id=student_id)

    ok=False

    position = get_position(request)
    
    if position ==4: ok=True
    #kiem tra xem giao vien nay co phai chu nhiem lop nay khong
    if position ==3:
        if get_level(request) == 'S':
            ok = True
        elif selectedClass.teacher_id != None:
                if selectedClass.teacher_id.user_id.id == request.user.id:
                    ok=True

    if request.user.id==student.user_id.id: ok =True
    if (not ok):
        return HttpResponseRedirect('/school')

    studentName=student.last_name+" "+student.first_name

    yearChoice=selectedClass.year_id.id
    if term_id==None:
        selectedTerm=get_current_term(request)
        termChoice  =selectedTerm.id
    else:
        termChoice = term_id
        selectedTerm=Term.objects.get(id=termChoice)

    termList= Term.objects.filter(year_id=yearChoice,number__lt=3).order_by('number')

    #if request.method == 'POST':
    #    termChoice =int(request.POST['term'])
    #    selectedTerm=Term.objects.get(id=termChoice)

    subjectList=selectedClass.subject_set.all().order_by("index",'name')


    markList=[]
    tbnamList=[]
    tbhk1List=[]
    m1List=[]
    m2List=[]
    m3List=[]
    list=[]
    tbhk1=None
    tbhk2=None
    tbCaNam=None
    if selectedTerm.number==2:
        for s in subjectList:
            m=s.mark_set.get(student_id=student_id,term_id__number=2)
            markList.append(m)
            m1List.append(m.toString(0,True,s.nx))
            m2List.append(m.toString(1,True,s.nx))
            m3List.append(m.toString(2,True,s.nx))

            tbnam=s.tkmon_set.get(student_id=student_id)
            tbnamList.append(tbnam)

            hk1=s.mark_set.get(student_id=student_id,term_id__number=1)

            tbhk1List.append(hk1)

        list=zip(subjectList,markList,m1List,m2List,m3List,tbhk1List,tbnamList)

        tbhk1  =student.tbhocky_set.get(term_id__year_id=yearChoice,term_id__number=1)
        tbhk2  =student.tbhocky_set.get(term_id__year_id=yearChoice,term_id__number=2)
        tbCaNam=student.tbnam_set.get(year_id=yearChoice)
    elif  selectedTerm.number==1:
        for s in subjectList:
            m=s.mark_set.get(student_id=student_id,term_id=termChoice)
            markList.append(m)
            m1List.append(m.toString(0,True,s.nx))
            m2List.append(m.toString(1,True,s.nx))
            m3List.append(m.toString(2,True,s.nx))

        list=zip(subjectList,markList,m1List,m2List,m3List)
        tbhk1=student.tbhocky_set.get(term_id=termChoice)


    t = loader.get_template(os.path.join('school','mark/mark_for_a_student.html'))

    c = RequestContext(request, {
                                'message' : message,
                                'class_id':class_id,
                                'student_id':student_id,
                                'list':list,
                                'termList':termList,
                                'selectedTerm':selectedTerm,
                                'termChoice':termChoice,
                                'subjectList':subjectList,
                                'markList':markList,
                                'studentName':studentName,
                                'selectedClass':selectedClass,
                                'tbhk1':tbhk1,
                                'tbhk2':tbhk2,
                                'tbCaNam':tbCaNam,
                                }
                       )


    return HttpResponse(t.render(c))

# diem cho 1 mon
def toDigit(x):
    if x=='':
        return None
    else:
        return float(x)

def update(s,primary,isComment,user):
    strings=s.split(':')
    idMark=int(strings[0])    
    setOfNumber =strings[1].split('*')
    setOfValue  =strings[2].split('*')    
    length = len(setOfNumber)
    
    timeNow = datetime.datetime.now()
    
    m = Mark.objects.get(id=idMark)
    arrMark=m.toArrayMark()
    arrTime=m.toArrayTime()
    
    for i in range(length-1):
        
        number= int(setOfNumber[i])
        value = setOfValue[i]
                    
        if value=='-1'  :
            value = ''
            time  = ''
        else:
            time=str(int((timeNow-CHECKED_DATE).total_seconds()/60))

        if number <= 3*MAX_COL:
            if (arrMark[number] != value) & (arrMark[number] != '' ):
                h = HistoryMark()
                if arrMark[number]=='':
                    h.old_mark = None
                else:
                    h.old_mark = float(arrMark[number])
                h.number = number
                h.mark_id = m
                h.subject_id = m.subject_id
                h.user_id = user
                h.save()

            arrMark[number] = value
            arrTime[number] = time

        elif  number == 3*MAX_COL+1:
            m.ck=toDigit(value)
            arrTime[3*MAX_COL+1]=time
            
        elif  number == 3*MAX_COL+2:
            m.tb=toDigit(value)
            arrTime[3*MAX_COL+2]=time
            
            subject_id = m.subject_id
            student_id = m.student_id

            tbk2=Mark.objects.get(subject_id=subject_id.id,student_id=student_id.id,term_id__number=2)
            tbcn=TKMon.objects.get(subject_id=subject_id.id,student_id=student_id.id)

            if not isComment:
                if (tbk2.tb==None) | (value==''):
                    tbcn.tb_nam = None
                else:
                    tbcn.tb_nam = round((m.tb + tbk2.tb*2+e)/3 , 1)
                tbcn.save()
            if tbk2.mg:
                tbcn.tb_nam = toDigit(value)
                tbcn.save()
                
        elif number ==3*MAX_COL+3:
            m.tb = toDigit(value)
            arrTime[3*MAX_COL+2]=time

        elif number == 3*MAX_COL+4:
            subject_id = m.subject_id
            student_id = m.student_id
            tbcn=TKMon.objects.get(subject_id=subject_id.id,student_id=student_id.id)

            if (primary==0)| (primary==3)| (primary==4):
                tbcn.tb_nam   = toDigit(value)
                if value=='':
                    tbcn.time=None
                else:
                    tbcn.time=int(time)
            elif (primary==1) | (primary==2):
                tbcn.tb_nam   =m.tb
                if m.tb==None:
                    tbcn.time=None
                else:
                    tbcn.time=int(time)
            tbcn.save()
            
    m.saveMark(arrMark)
    m.saveTime(arrTime)
    #print m.time
    #print m.diem
    """
        elif (number==17):
            m.tb = value
            if isComment:
                mt.tb=time
            else:    
                subject_id = m.subject_id
                student_id = m.student_id
                
                tbk2=Mark.objects.get(subject_id=subject_id.id,student_id=student_id.id,term_id__number=2)
                tbcn=TKMon.objects.get(subject_id=subject_id.id,student_id=student_id.id)
                if (tbk2.tb==None) | (value==None):
                    tbcn.tb_nam = None
                else:     
                    tbcn.tb_nam = round((m.tb + tbk2.tb*2+e)/3 , 1)            
                tbcn.save()
            
        elif (number==18):                 
            m.tb = value
            if (isComment):
                mt.tb=time
        elif (number==19): 
            
                
            subject_id = m.subject_id
            student_id = m.student_id
            tbcn=TKMon.objects.get(subject_id=subject_id.id,student_id=student_id.id)
            if isComment:
                tbcn.tb_nam=value
                tbcn.time  =time
            else:    
                if (primary==0)| (primary==3)| (primary==4):
                    tbcn.tb_nam   = value
                elif (primary==1) | (primary==2):
                    tbcn.tb_nam   =m.tb
                          
            tbcn.save()
    """
    m.save()
@transaction.commit_on_success
@need_login
def saveMark(request):
    t1=time.time()
    message = 'hello'
    if request.method == 'POST':
        str = request.POST['data']
        strs=str.split('/')
                
        position = get_position(request)
        user = request.user
        if   position ==4 :
#            idTeacher= int(strs[1])
#            teacher= Teacher.objects.get(id=idTeacher)
#            if not in_school(request,teacher.school_id):
#                return
            pass
        elif position ==3 :
            idTeacher= int(strs[1])
            teacher= Teacher.objects.get(id=idTeacher)
            if request.user.id!=teacher.user_id.id: return
        else: return
        length = len(strs)
        primary= int(strs[2])
        isComment = strs[3]=="true"
        for i in range(4,length):
                update(strs[i],primary,isComment,user)
                     
        message=strs[0]
        data = simplejson.dumps({'message': message})
        t2=time.time()
        print (t2-t1)
        
    return HttpResponse(data,  mimetype = 'json')

def sendSMSForAPupil(s,user):
    #print s
    strings=s.split(':')
    
    idMark=int(strings[0])    
    setOfNumber =strings[1].split('*')
    setOfValue  =strings[2].split('*')    
    
    length = len(setOfNumber)
    
    m = Mark.objects.get(id=idMark)
    termNumber = m.term_id.number
    markStr1="" 
    markStr2="" 
    markStr3="" 
    markStr4=""
    markStr5=""
    markStr6=""
    markStr7=""
    tbNam   = None
    tbhk1   = None
    arrSent=['']*(3*MAX_COL+3)
    sents=m.sent.split('|')
    for (i,s) in enumerate(sents):
        ss=s.split('*')
        for (j,a) in enumerate(ss):
            if i<3:
                arrSent[i*MAX_COL+j+1]=a
            else:
                arrSent[3*MAX_COL+i-2]=a
    for i in range(length-1):
        number= int(setOfNumber[i])
        value = setOfValue[i]
        if   number <= MAX_COL   : markStr1+=value+"  "
        elif number <= 2*MAX_COL : markStr2+=value+"  "
        elif number <= 3*MAX_COL : markStr3+=value+"  "
        elif number == 3*MAX_COL+1 : markStr4+=value+" "
        elif number == 3*MAX_COL+2 :
            markStr5+=value+" "
            tbhk1   =Mark.objects.get(subject_id=m.subject_id,student_id=m.student_id,term_id__number=1)
            tempSent = tbhk1.sent
            tempSent=tempSent.split('|')
            tempSent[4]="1"
            tbhk1.sent = '|'.join(tempSent)
            continue
        elif number == 3*MAX_COL+3 : markStr6+=value+" "
        elif number == 3*MAX_COL+4 :
            markStr7+=value+" "
            tbNam = TKMon.objects.get(subject_id=m.subject_id,student_id=m.student_id)
            tbNam.sent=True
            continue
        if number==3*MAX_COL+3:
            number = 3*MAX_COL+2
        arrSent[number]='1'
        
    smsString=u'Diem mon '+to_en1(m.subject_id.name)+ u' cua hs '
    smsString+=to_en1(m.student_id.last_name)+" "+to_en1(m.student_id.first_name)+" nhu sau: "    
    termNumber = m.term_id.number

    if markStr1 !="":  smsString+="\nmieng:" + markStr1
    if markStr2 !="":  smsString+="\ndiem 15 phut:" + markStr2
    if markStr3 !="":  smsString+="\ndiem 45 phut:" + markStr3
    if markStr4 !="":  smsString+="\nthi cuoi ky:" + markStr4
    
    if markStr5 !="":
        smsString+="\nTBHK I:" + markStr5

    if markStr6 !="" :  smsString+="\nTBHK II:" + markStr6
    if markStr7 !="" :  smsString+="\nTB ca nam:" + markStr7
    sent=''
    for i in range(3):
        tempSent=''
        pre=1
        for j in range(1,MAX_COL+1):
            if arrSent[i*MAX_COL+j]!='':
                tempSent+=(j-pre)*'*'+arrSent[i*MAX_COL+j]
                pre=j
        sent+=tempSent+'|'
    sent+=arrSent[3*MAX_COL+1]+'|'+arrSent[3*MAX_COL+2]
    m.sent=sent

    if m.student_id.sms_phone:
        try:
            """
            m.save()
            if tbNam!=None:
                tbNam.save()
            if tbhk1 != None:
                tbhk1.save()
            """
            sent1 = sendSMS(m.student_id.sms_phone,smsString,user)
            if sent1=='1':
                m.save()
                if tbNam != None:
                    tbNam.save()
                if tbhk1 != None:
                    tbhk1.save()

                return  str(idMark)
        except Exception as e:
            print e
            pass
    return ''

@need_login
def sendSMSMark(request):
    message = '-'
    if request.method == 'POST':
        str = request.POST['data']
        strs=str.split('/')
        for s in strs:
            if s!="":
                message+=sendSMSForAPupil(s,request.user)+"-"
        data = simplejson.dumps({'message': message})
        return HttpResponse(data, mimetype='json')

@need_login
def capNhapMienGiam(request,class_id, student_id):
    user = request.user
    if not user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
        
    try:
        school = get_school(request)
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))
    
    pos = get_position(request)
    if (pos==1) and (get_student(request).id==int(student_id)):
        pos = 4
    if (get_position(request) < 1):
        return HttpResponseRedirect('/')
    subjectList = Subject.objects.filter(class_id=class_id,name__in=['GDQP-AN',u'Thể dục',u'Âm nhạc',u'Mĩ thuật','GDQP']).order_by('index','name')
    term1Mark   = Mark.objects.filter(subject_id__class_id=class_id,student_id=student_id,term_id__number=1,subject_id__name__in=['GDQP-AN',u'Thể dục',u'Âm nhạc',u'Mĩ thuật','GDQP']).order_by('subject_id__index','subject_id__name')
    term2Mark   = Mark.objects.filter(subject_id__class_id=class_id,student_id=student_id,term_id__number=2,subject_id__name__in=['GDQP-AN',u'Thể dục',u'Âm nhạc',u'Mĩ thuật','GDQP']).order_by('subject_id__index','subject_id__name')
    tkMonList   = TKMon.objects.filter(subject_id__class_id=class_id,student_id=student_id,subject_id__name__in=['GDQP-AN',u'Thể dục',u'Âm nhạc',u'Mĩ thuật','GDQP']).order_by('subject_id__index','subject_id__name')
    # cam xoa  2 dong nay. Xoa se sai ngay
    for term1,term2,tkMon,s in zip(term1Mark,term2Mark,tkMonList,subjectList):
        pass
    
    if request.method=='POST':
        str = request.POST['str']
        strs= str.split(':')
        index =int(strs[0])-1
        type  =int(strs[1])
        if type==0:
            term1Mark[index].mg=False
            term2Mark[index].mg=False
            tkMonList[index].mg=False
        elif type==3:
            term1Mark[index].mg=True
            term2Mark[index].mg=True
            tkMonList[index].mg=True
        elif type==1:
            term1Mark[index].mg=True
            term2Mark[index].mg=False
            tkMonList[index].mg=False
            if subjectList[index].primary==1:
                tkMonList[index].mg=True
            
        elif type==2:
            term1Mark[index].mg=False
            term2Mark[index].mg=True
            tkMonList[index].mg=False
            if subjectList[index].primary==2:
                tkMonList[index].mg=True
        
        term1Mark[index].save()    
        term2Mark[index].save()
        tkMonList[index].save()
                                            
    mgList=[]
    coMienGiam =False
    for term1,term2,tkMon in zip(term1Mark,term2Mark,tkMonList):
        if    (tkMon.mg) & (term1.mg) & (term2.mg) : 
            mgList.append(3)
        elif  term1.mg : mgList.append(1)
        elif  term2.mg : mgList.append(2)
        else: mgList.append(0)
        
    for m in mgList:
        if m !=0:
            coMienGiam=True
                
    
    list = zip(subjectList,mgList)     
    message = None
    t = loader.get_template(os.path.join('school/finish', 'cap_nhap_mien_giam.html'))
    c = RequestContext(request, { 
                                 'list':list,
                                 'class_id':class_id,
                                 'student_id':student_id,
                                 'coMienGiam':coMienGiam,
                                }
                       )
    return HttpResponse(t.render(c))

@need_login
def saveNote(request):
    t1=time.time()
    message = 'hello'
    if request.method == 'POST':
        data=request.POST['data']
        datas=data.split('/')
        
        position = get_position(request)
        if   position ==4 :pass
        elif position ==3 :
#            idTeacher= int(datas[0])
#            teacher= Teacher.objects.get(id=idTeacher)
#            if request.user.id!=teacher.user_id.id: return
            pass
        else: return
        m = Mark.objects.get(id=datas[2])

        contentList = m.note.split("/")
        newContent=''
        ok=False
        for c in contentList:
            cs = c.split("##")
            if (cs[0]==datas[1]):
                newContent+="/"+datas[1]+"##"+datas[3]
                ok=True
            else:
                newContent+="/"+c

        if not ok :
            m.note+="/"+datas[1]+"##"+datas[3]
        else:
            m.note=newContent
            
        m.save()
        data = simplejson.dumps({'message': message})
        t2=time.time()
        print (t2-t1)
        return HttpResponse( data, mimetype = 'json')
