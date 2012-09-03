# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from school.models import *
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from school.utils import *
from django.core.urlresolvers import reverse
from django.db import transaction
import xlrd  
from  views import save_file 
import os.path 
import time 
import datetime
import random
import os.path
from settings import *

LOCK_MARK =False
ENABLE_CHANGE_MARK=True

def thu111(request):
    t1= time.time()
    t2= time.time()
    if request.method=='POST':
        print "chao"
        s=request.FILES.get('file')
        print s.name
        print s.size 
                       
        filename = save_file(request.FILES.get('file'), request.session)
        filepath = os.path.join(settings.TEMP_FILE_LOCATION, filename)
       
        book = xlrd.open_workbook(filepath)
        sheet = book.sheet_by_index(0)
        
        print to_en1(sheet.cell(13,1).value)
        print book
        print sheet
        print "ffffffffffffff"
        
        
    print (t2-t1)
    t = loader.get_template(os.path.join('school','ll.html'))
    
    c = RequestContext(request, {
                                }
                       )
    
    #print (t2-t1)

    return HttpResponse(t.render(c))

@transaction.commit_on_success                                                              
def thu11111(request):
    t1= time.time()
    school=get_school(request)
    classList=Class.objects.filter(year_id__school_id=school.id)
    tong=0
    tong1=0
    
    for c in classList:
        """
        tbnamList=TBNam.objects.filter(student_id__class_id=c.id)
        HKList=HanhKiem.objects.filter(student_id__class_id=c.id)
        for tbnam in tbnamList:
            if tbnam.len_lop==None:
                tong1+=1
        for hk in HKList:
            pass        
        for hk in HKList:
            pass        
        for hk in HKList:
            pass        
        tong+=len(tbnamList)
        """        
        tong1+=TBNam.objects.filter(student_id__class_id=c.id,len_lop=None).count()
        tong1+=HanhKiem.objects.filter(student_id__class_id=c.id,year=None).count()
        #print tbnamList   
    print tong     
    print tong1
    t2=time.time()    
    print (t2-t1)
    t = loader.get_template(os.path.join('school','ll.html'))
    
    c = RequestContext(request, {
                                 
                                }
                       )
    
    #print (t2-t1)

    return HttpResponse(t.render(c))

@transaction.commit_on_success                                                              
def thu1(request):
    t1= time.time()
    list1 = TKMon.objects.filter(student_id__class_id=27)
    print len(list1)/14
    for m in list1:
        m.tb_nam=random.randrange( 6,10)
       # m.save()
    for m in list1:
        m.save()
           
    list = Mark.objects.filter(subject_id__class_id=27)
    for m in list:
        m.mieng_1 = random.randrange( 7,11 )
        m.mieng_2 = random.randrange( 7,11 )
        m.mieng_3 = random.randrange( 7,11 )
        m.mieng_4 = random.randrange( 7,11 )
        m.mieng_5 = random.randrange( 7,11 )
        
        m.mlam_1 = random.randrange( 7,11 )
        m.mlam_2 = random.randrange( 7,11 )
        m.mlam_3 = random.randrange( 7,11 )
        m.mlam_4 = random.randrange( 7,11 )
        m.mlam_5 = random.randrange( 7,11 )

        m.mot_tiet_1 = random.randrange( 7,11 )
        m.mot_tiet_2 = random.randrange( 7,11 )
        m.mot_tiet_3 = random.randrange( 7,11 )
        m.mot_tiet_4 = random.randrange( 7,11 )
        m.mot_tiet_5 = random.randrange( 7,11 )
        m.ck=random.randrange( 7,11 )
        m.tb=random.randrange( 7,11 )
        """
        
        m.mieng_1 = None
        m.mieng_2 = None
        m.mieng_3 = None
        m.mieng_4 = None
        m.mieng_5 = None
        
        m.mlam_1 = None
        m.mlam_2 = None
        m.mlam_3 = None
        m.mlam_4 = None
        m.mlam_5 = None

        m.mot_tiet_1 = None
        m.mot_tiet_2 = None
        m.mot_tiet_3 = None
        m.mot_tiet_4 = None
        m.mot_tiet_5 = None
        m.ck=None
        m.tb=None
        
        mt=m.marktime
        mt.mieng_1 = None
        mt.mieng_2 = None
        mt.mieng_3 = None
        mt.mieng_4 = None
        mt.mieng_5 = None
        
        mt.mlam_1 = None
        mt.mlam_2 = None
        mt.mlam_3 = None
        mt.mlam_4 = None
        mt.mlam_5 = None

        mt.mot_tiet_1 = None
        mt.mot_tiet_2 = None
        mt.mot_tiet_3 = None
        mt.mot_tiet_4 = None
        mt.mot_tiet_5 = None
        mt.ck=None
        mt.tb=None
        mt.save()
        """
    for m in list:
        m.save()
    
    t = loader.get_template(os.path.join('school','ll.html'))
    t2=time.time()
    print (t2-t1)
    c = RequestContext(request, {'list':list,
                                }
                       )

    #print (t2-t1)
    return HttpResponse(t.render(c))

@transaction.commit_on_success                                                              
def thu1(request):
    t1= time.time()
    
    markList = Mark.objects.filter(subject_id__class_id=26)
    i=0
    for m in markList:
        m.mieng_1 = random.randrange( 7,11 )
        m.mieng_2 = random.randrange( 7,11 )
        m.mieng_3 = random.randrange( 7,11 )
        m.mieng_4 = random.randrange( 7,11 )
        m.mieng_5 = random.randrange( 7,11 )
        
        m.mlam_1 = random.randrange( 7,11 )
        m.mlam_2 = random.randrange( 7,11 )
        m.mlam_3 = random.randrange( 7,11 )
        m.mlam_4 = random.randrange( 7,11 )
        m.mlam_5 = random.randrange( 7,11 )

        m.mot_tiet_1 = random.randrange( 7,11 )
        m.mot_tiet_2 = random.randrange( 7,11 )
        m.mot_tiet_3 = random.randrange( 7,11 )
        m.mot_tiet_4 = random.randrange( 7,11 )
        m.mot_tiet_5 = random.randrange( 7,11 )
        m.ck=random.randrange( 7,11 )
        m.tb=random.randrange( 3,11 )
        i+=1
        m.note=str(i)
        m.save() 
    tkmonList= TKMon.objects.filter(subject_id__class_id=26)
    for tkmon in tkmonList:
        tkmon.tb_nam=random.randrange( 7,11 )
        tkmon.save()

    hanhKiemList =TBNam.objects.filter(student_id__classes=26)
    print len(hanhKiemList)
    for hk in hanhKiemList:
        t =random.randrange( 1,3 )
        if   t==1: hk.year='T'
        elif t==2: hk.year='K'
        elif t==3: hk.year='TB'
        elif t==4: hk.year='Y'

        t =random.randrange( 1,3 )
        if   t==1: hk.term1='T'
        elif t==2: hk.term1='K'
        elif t==3: hk.term1='TB'
        elif t==4: hk.term1='Y'

        t =random.randrange( 1,3 )
        if   t==1: hk.term2='T'
        elif t==2: hk.term2='K'
        elif t==3: hk.term2='TB'
        elif t==4: hk.term2='Y'
        
        hk.save()
            
    t = loader.get_template(os.path.join('school','ll.html'))
    t2=time.time()
    print (t2-t1)
    c = RequestContext(request, {'list':list,
                                }
                       )

    #print (t2-t1)
    return HttpResponse(t.render(c))
@transaction.commit_on_success
def thu1(request):
    t1= time.time()
    numberPupil=Pupil.objects.all().count()
    
    term=Term.objects.get(id=1)
    tong1=0
    tong2=0
    """
    for i in range(10000):
        try:
            p=random.randrange( 1,numberPupil)+1
            pp=Pupil.objects.get(id=p)
            year = random.randrange(2)
            month= random.randrange(12)+1
            day  = random.randrange(30)+1
            date = datetime.date(2011+year,month,day)
            t=random.randrange(2)
            if t==0:
                dd=DiemDanh(student_id=pp,time=date,term_id=term,loai=u'Không phép')
            else:     
                dd=DiemDanh(student_id=pp,time=date,term_id=term,loai=u'Có phép')
            dd.save()
            tong1+=1
        except Exception as e: 
            #print e 
            tong2+=1
            #print "tong1=",tong1
            #print "tong2=",tong2
            if tong1 % 100 ==0:
                print tong1
    """
    tong=0
    diemDanh=DiemDanh.objects.all()
    for dd in diemDanh:
        #print dd.loai
        #print dd.loai==u'Có phép'
        dd.delete()
        if (dd.loai!='Có phép') & (dd.loai!='Không phép'):
            #dd.delete()
            tong+=1
            if tong % 100==0:
                print tong
            
            
                                                
    t = loader.get_template(os.path.join('school','ll.html'))
    t2=time.time()
    print (t2-t1)
    x='K'
    c = RequestContext(request, {'list':list,
                                 'x':x,
                                }
                       )
    #print (t2-t1)
    return HttpResponse(t.render(c))

def thu(request):
    t1= time.time()
    filepath = os.path.join(SITE_ROOT, 'templates/school/mark/dataForMarkTable.xls')
    print filepath
    book = xlrd.open_workbook(filepath)
    s = book.sheet_by_index(0)


    t = loader.get_template(os.path.join('school','ll.html'))
    t2=time.time()
    print (t2-t1)
    x='K'
    c = RequestContext(request, {'list':list,
                                 'x':x,
                                }
                       )
    #print (t2-t1)
    return HttpResponse(t.render(c))
