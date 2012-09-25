# -*- coding: utf-8 -*-
#from school.views import *

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
import time
import os.path
from xlwt import Workbook
from school.models import Term, Class, Mark, TBHocKy, TBNam, Subject, Pupil, TKMon, BAN_CHOICE, Block, DiemDanh,\
    TKDiemDanh, Year
from school.templateExcel import h4, noneSubject, h5, h1, first_name1, s3, s2, s1, last_name1, first_name, last_name,\
    h6, h7, h2, m1, m2, m3, m4, m5, h3, h8, h9, d1, h10, h61, h71, LASTNAME_WIDTH, SIZE_PAGE_WIDTH, h82, normalize, d2,\
    d3, h81, h91, hh1, f5, f6, STT_WIDTH, FIRSTNAME_WIDTH, A4_WIDTH, printCongHoa, h40, h92, h74, f2, f4, f3, hh2,\
    BIRTHDAY_WIDTH, PLACE_WIDTH, SEX_WIDTH, DAN_TOC_WIDTH, UU_TIEN_WIDTH, A3_WIDTH, f1, f81, f8, f71, f7, f82, m6,\
    m7, m8, m9, m10, printHeader, SIZE_PAGE_WIDTH1, s4, h72, h73, h41, MAX_VIEW, h8center
from school.utils import get_current_term, in_school, get_position, get_level, to_en1, convertDanhHieu,\
    convertHkToVietnamese, convertHlToVietnamese
from school.viewMark import  getDecodeMark, e
import datetime
from excel_interaction import class_generate
from decorators import need_login

def printASubject(class_id,termNumber,s,sub,x,y,ls,number):
    if sub!=None:
        if (sub.name==u'Ngoại ngữ'):
            s.write_merge(x,x,y,y+4,'NGOẠI NGỮ:...........................................',h4)
        else:
            s.write_merge(x,x,y,y+4,sub.name.upper(),h4)
    else:
        s.write_merge(x,x,y,y+4,noneSubject,h4)
    
    s.write_merge(x+1,x+1,y,y+1,u'Điểm hs 1',h5)
    s.write_merge(x+1,x+2,y+2,y+2,u'Điểm hs 2\n(V)',h5)
    s.write_merge(x+1,x+2,y+3,y+3,u'KT\nhk',h5)
    s.write_merge(x+1,x+2,y+4,y+4,u'TBm',h5)
    
    s.write(x+2,y,u'M',h5)
    s.write(x+2,y+1,u'v',h5)
    selected_class = Class.objects.get(id=class_id)
    selected_year = selected_class.year_id
    selected_term = Term.objects.get(year_id=selected_year, number=termNumber)
    monList = Mark.objects.filter(student_id__classes=class_id,subject_id=sub,term_id=selected_term).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday')

    i=0    
    for m in monList:
        i+=1    
        str1=m.toString(0,True,sub.nx)
        str2=m.toString(1,True,sub.nx)
        str3=m.toString(2,False,sub.nx)

        str4=""
        if m.ck!=None: str4=normalize(m.ck,sub.nx,False)
        
        str5=""
        if m.tb!=None: str5=normalize(m.tb,sub.nx,False)
        
        if i % 5 !=0:
            s.write(x+i+2,y,str1,h6)
            s.write(x+i+2,y+1,str2,h6)
            s.write(x+i+2,y+2,str3,h6)
            s.write(x+i+2,y+3,str4,h61)
            s.write(x+i+2,y+4,str5,h61)
            ls.write(i+3,number+2,str5,h61)
        else:    
            s.write(x+i+2,y,str1,h7)
            s.write(x+i+2,y+1,str2,h7)
            s.write(x+i+2,y+2,str3,h7)
            s.write(x+i+2,y+3,str4,h71)
            s.write(x+i+2,y+4,str5,h71)
            ls.write(i+3,number+2,str5,h71)
            
    for t in range(i+1,56):
        if t % 5!=0:
            for j in range(y,y+5):    
                s.write(x+t+2,j,"",h6)
                ls.write(t+3,number+2,"",h6)
        else:    
            for j in range(y,y+5):    
                s.write(x+t+2,j,"",h7)
                ls.write(t+3,number+2,"",h7)
                
def printName(class_id,s,x,y,mode=0):     
    
    if mode==0 :
        s.write_merge(x,x+2,y,y,u'Số\nTT',h4)
        s.write_merge(x,x+2,y+1,y+2,u'Họ và tên',h4)
    else:    
        s.write_merge(x,x+3,y,y,u'Số\nTT',h4)
        s.write_merge(x,x+3,y+1,y+2,u'Họ và tên',h4)
        x=x+1

    pupilList = Pupil.objects.filter(classes=class_id,attend__is_member=True).order_by('index','first_name','last_name','birthday').distinct()
    i=0
    for p in pupilList:
        i +=1
        if i % 5 !=0:
            s.write(x+i+2,y,i,h6)
            s.write(x+i+2,y+1,p.last_name,last_name)
            s.write(x+i+2,y+2,p.first_name,first_name)
        else:    
            s.write(x+i+2,y,i,h7)
            s.write(x+i+2,y+1,p.last_name,last_name1)
            s.write(x+i+2,y+2,p.first_name,first_name1)
        
    for t in range(i+1,56):
        if t % 5 !=0:
            s.write(x+t+2,y,t,h6)
            s.write(x+t+2,y+1,"",last_name)
            s.write(x+t+2,y+2,"",first_name)
        else:    
            s.write(x+t+2,y,t,h7)
            s.write(x+t+2,y+1,"",last_name1)
            s.write(x+t+2,y+2,"",first_name1)
                
def printPage13(s,x,y,string):    
    s.write_merge(x+23,x+27,y,y+12,u'PHẦN GHI ĐIỂM',h1)
    s.write_merge(x+28,x+33,y,y+12,string,h2)
    
def printPage14(class_id,s,termNumber,n1,mon1,mon2,x,y,ls):
            
    s.col(0).width = s1
    s.col(1).width = s2
    s.col(2).width = s3
    
    s.col(3).width = m1
    s.col(4).width = m2
    s.col(5).width = m3
    s.col(6).width = m4
    s.col(7).width = m5
    
    s.col(8).width  = m1
    s.col(9).width  = m2
    s.col(10).width = m3
    s.col(11).width = m4
    s.col(12).width = m5
    
    if termNumber==1:
        s.write_merge(x,x,y,y+12,u'HỌC KỲ I',h3)
    else:    
        s.write_merge(x,x,y,y+12,u'HỌC KỲ II',h3)
    
    printName(class_id,s,x+1,y)        
    printASubject(class_id,termNumber,s,mon1,x+1,y+3,ls,2*n1+1)
    printASubject(class_id,termNumber,s,mon2,x+1,y+8,ls,2*n1+2)
    
    max = 55
    str =u'Trong trang này có......... điểm được sửa chữa,'+u' trong đó môn: '+ unicode(mon1.name)+u'....... điểm'
    if mon2!=None:
        str+=', '+ unicode(mon2.name)+u'.......điểm'
    s.write_merge(x+max+5,x+max+5,y+0,y+8,str,h8)
    
    s.write_merge(x+max+5,x+max+5,y+9,y+12,u'Ký xác nhận của',h9)
    s.write_merge(x+max+6,x+max+6,y+9,y+12,u'giáo viên chủ nhiệm',h9)
        
def printPage20(class_id,termNumber,s,length,subjectList):
    s.set_paper_size_code(8)
    s.col(0).width = s1
    s.col(1).width = s2
    s.col(2).width = s3
    for i in range(length):
        s.col(i+3).width = d1
        
    s.col(length+3).width = d1
    s.col(length+4).width = d1
    s.col(length+5).width = d1
    s.col(length+6).width = d1+500
    
    if termNumber==1:
        s.write_merge(0,0,0,length+6,u'TỔNG HỢP KẾT QUẢ HỌC KỲ I',h3)
    else:    
        s.write_merge(0,0,0,length+6,u'TỔNG HỢP KẾT QUẢ HỌC KỲ II',h3)
        
    for (i,ss) in enumerate(subjectList):
        if ss.name=='GDCD':
            s.write_merge(1,3,i+3,i+3,'GD\nCD',h10)
        elif ss.name=='GDQP-AN':     
            s.write_merge(1,3,i+3,i+3,'GD\nQP-\nAN',h10)
        elif ss.name=='GDQP':
            s.write_merge(1,3,i+3,i+3,'GD\nQP',h10)
        else:
            s.write_merge(1,3,i+3,i+3,ss.name,h10)
            
    s.write_merge(1,3,length+3,length+3,'TB',h10)
    s.write_merge(1,2,length+4,length+6,u'Kết quả xếp loại\n và thi đua',h10)
 
    s.write(3,length+4,u'HL',h10)
    s.write(3,length+5,u'HK',h10)
    s.write(3,length+6,u'TĐ',h10)
    
    
    selectedClass = Class.objects.get(id=class_id)
    selected_year = selectedClass.year_id
    selected_term = Term.objects.get(year_id=selected_year, number=termNumber)

    tbhkList = TBHocKy.objects.filter(student_id__classes=class_id,term_id=selected_term, student_id__attend__is_member=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday').distinct()
    hkList   = TBNam.objects.filter(student_id__classes=class_id,year_id=selectedClass.year_id,student_id__attend__is_member=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday').distinct()
    
    i=-1
    for (i,(tbhk,hk)) in enumerate(zip(tbhkList,hkList)):
        str1=""
        if tbhk.tb_hk!=None: str1 = str(tbhk.tb_hk)
        str2=""                                
        if tbhk.tb_hk!=None: str2 = str(tbhk.hl_hk)
        str3=""
        if termNumber==1:
            if hk.term1!=None  : str3 = hk.term1
        else:    
            if hk.term2!=None  : str3 = hk.term2
        str4=""
        if   tbhk.danh_hieu_hk=='G' : str4='HSG'
        elif tbhk.danh_hieu_hk=='TT': str4='HSTT'
        
        if i % 5!=4:            
            s.write(i+4,length+3,str1,h61)                         
            s.write(i+4,length+4,str2,h61)                         
            s.write(i+4,length+5,str3,h61)                         
            s.write(i+4,length+6,str4,h61)
        else:                             
            s.write(i+4,length+3,str1,h71)                         
            s.write(i+4,length+4,str2,h71)                         
            s.write(i+4,length+5,str3,h71)                         
            s.write(i+4,length+6,str4,h71)
    
    for t in range(i+2,56):
        if t % 5!=0:            
            s.write(t+3,length+3,"",h6)                         
            s.write(t+3,length+4,"",h6)                         
            s.write(t+3,length+5,"",h6)                         
            s.write(t+3,length+6,"",h6)
        else:                             
            s.write(t+3,length+3,"",h7)                         
            s.write(t+3,length+4,"",h7)                         
            s.write(t+3,length+5,"",h7)                         
            s.write(t+3,length+6,"",h7)
                 
    printName(class_id,s,1,0)
    max = 55
    str1 =u'Trong trang này có......... điểm được sửa chữa,'+u' trong đó môn:........................................................................... '
    str2 ='........................................................................................................................................................................'
    s.write_merge(max+5,max+5,0,16,str1,h8)
    s.write_merge(max+6,max+6,0,16,str2,h8)
    
    s.write_merge(max+5,max+5,17,21,u'Ký xác nhận của',h9)
    s.write_merge(max+6,max+6,17,21,u'giáo viên chủ nhiệm',h9)

def printPage31(class_id,s,tbNamList,x,y):
        
    s.col(y+0).width = s1
    s.col(y+1).width = s2
    s.col(y+2).width = s3
    for i in range(3,12):
        s.col(y+i).width = d2
        if (i==7) | (i==10):         
            s.col(y+i).width = d2+500

    s.col(y+12).width = d3
    
    printName(class_id,s,x+1,y,1)
                
    s.write_merge(x+0,x+0,y,y+12,u'TỔNG HỢP KẾT QUẢ ĐÁNH GIÁ, XẾP LOẠI CẢ NĂM HỌC',h3)
    s.write_merge(x+1,x+2,y+3,y+4,u'XẾP LOẠI',h10)
    s.write_merge(x+3,x+4,y+3,y+3,'HL',h10)
    s.write_merge(x+3,x+4,y+4,y+4,'HK',h10)
    s.write_merge(x+1,x+4,y+5,y+5,u'TS ngày\n nghỉ học',h10)
    s.write_merge(x+1,x+4,y+6,y+6,u'Được\n lên lớp',h10)
    s.write_merge(x+1,x+4,y+7,y+7,u'Ở lại lớp, KT lại, rèn luyện HK trong hè',h10)
    s.write_merge(x+1,x+2,y+8,y+10,u'Xếp loại lại về HK, HL, sau KT lại các môn học hoặc rèn luyện về HK',h10)
    s.write_merge(x+3,x+4,y+8,y+8,u'HL',h10)
    s.write_merge(x+3,x+4,y+9,y+9,u'HK',h10)
    s.write_merge(x+3,x+4,y+10,y+10,u'Lên lớp, ở lại lớp',h10)    
    s.write_merge(x+1,x+4,y+11,y+11,u'Danh hiệu\n HSG,\nHSTT',h10)
    s.write_merge(x+1,x+4,y+12,y+12,u'TỔNG HỢP CHUNG',h10)
    
    #hanhKiemList =HanhKiem.objects.filter(student_id__classes=class_id).order_by('student_id__index')
    llSauHe=0
    for (i,(tbNam)) in enumerate(tbNamList):
        if i % 5 != 4: h=h6
        else         : h=h7
        str1=''
        if tbNam.hl_nam!=None:           str1 = tbNam.hl_nam
                
        str2=''
        if tbNam.year!=None:   str2= tbNam.year
        
        str3=''
        if tbNam.tong_so_ngay_nghi!=None: str3 =tbNam.tong_so_ngay_nghi
         
        str4=''
        if (tbNam.len_lop==True) &(tbNam.thi_lai==None) & (tbNam.hk_ren_luyen_lai==None):
            str4='Lên lớp'
        
        str5=''
        if   tbNam.thi_lai       :str5='KT lại'
        elif tbNam.ren_luyen_lai    :str5='rèn luyện trong hè' 
        elif tbNam.len_lop==False:str5='Ở lại lớp'
        
        str6=''
        if tbNam.hl_thi_lai    :str6=tbNam.hl_thi_lai
         
        str7=''
        if tbNam.hk_ren_luyen_lai!=None: str7= tbNam.hk_ren_luyen_lai
        
        str8=''
        if (tbNam.ren_luyen_lai!=None) | (tbNam.thi_lai!=None):
            if   tbNam.len_lop==True : 
                str8='Lên lớp'
                llSauHe+=1
            elif tbNam.len_lop==False: str8='Ở lại lớp'
        
        str9=''
        if (tbNam.danh_hieu_nam != None) & (tbNam.danh_hieu_nam != 'K'):
            str9='HS'+tbNam.danh_hieu_nam
        
        
        s.write(x+i+5,y+3,str1,h)
        s.write(x+i+5,y+4,str2,h)
        s.write(x+i+5,y+5,str3,h)
        s.write(x+i+5,y+6,str4,h)
        s.write(x+i+5,y+7,str5,h)
        s.write(x+i+5,y+8,str6,h)
        s.write(x+i+5,y+9,str7,h)
        s.write(x+i+5,y+10,str8,h)
        s.write(x+i+5,y+11,str9,h)
        
    for tt in range(i+1,55):
        if tt % 5 != 4: h=h6
        else         : h=h7        
        for j in range(3,12):
            s.write(x+tt+5,y+j,'',h)
    sl1= tbNamList.filter(len_lop=True ).count()
    sl2= tbNamList.filter(len_lop=False).count()
    
    for i in range(55):
        s.write(x+i+5,y+12,'',h81)
    s.write(x+54+5,y+12,'',h71)    
    s.write(x+7,y+12,'Tổng số học sinh: '+str(len(tbNamList)),h81)
    s.write(x+10,y+12,'-Được lên lớp: '+str(sl1),h81)        
    s.write(x+12,y+12,'-Ở lại lớp:'+str(sl2),h81)
    s.write_merge(x+14,x+17,y+12,y+12,'-Được lên lớp sau khi kiểm tra lại các môn học hoặc rèn luyện trong hè: '+str(llSauHe),h81)        
    s.write(x+20,y+12,'Giáo viên chủ nhiệm',h91)        
    s.write(x+21,y+12,'(Ký và ghi rõ họ, tên)',hh1)        
    s.write(x+30,y+12,'Hiệu trưởng',h91)        
    s.write(x+31,y+12,'(Ký tên, đóng dấu)',hh1)        
    
def printPage30(class_id,book):
    subjectList = Subject.objects.filter(class_id=class_id).order_by("index",'name')
    for s in subjectList:
        pass
        #print s.index
    length = len(subjectList)
    s = book.add_sheet('XL cả năm',True)
    s.set_paper_size_code(8)
    s.col(0).width = s1
    s.col(1).width = s2
    s.col(2).width = s3
    for i in range(length):
        s.col(i+3).width =d1
        
    s.col(length+3).width = d1
    s.col(length+4).width = d1
    s.col(length+5).width = d1
    s.col(length+6).width = d1
    
    s.vert_page_breaks = [(length+8,0,65500)]    
    s.horz_page_breaks = []
    
    s.write_merge(0,0,0,length+6,u'TỔNG HỢP KẾT QUẢ ĐÁNH GIÁ, XẾP LOẠI CẢ NĂM HỌC',h3)

    printName(class_id,s,1,0,1)            
    for (i,ss) in enumerate(subjectList):
        if ss.name=='GDCD':
            s.write_merge(1,4,i+3,i+3,'GD\nCD',h10)
        elif ss.name=='GDQP-AN':     
            s.write_merge(1,4,i+3,i+3,'GD\nQP-\nAN',h10)
        else:    
            s.write_merge(1,4,i+3,i+3,ss.name,h10)
            
    s.write_merge(1,4,length+3,length+3,'TB\ncmcn',h10)
    s.write_merge(1,2,length+4,length+6,u'Điểm KT lại',h10)
    
    s.write_merge(3,4,length+4,length+4,'',h10)
    s.write_merge(3,4,length+5,length+5,'',h10)
    s.write_merge(3,4,length+6,length+6,'',h10)
    
    markList = TKMon.objects.filter(subject_id__class_id=class_id,current=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday','subject_id__index','subject_id__name')
    numberPupil = Pupil.objects.filter(classes=class_id,attend__is_member=True).distinct().count()
    for (t,m) in enumerate(markList):
        
        i = t % length
        j = int(t/length)
        if i==0 : tt=0
        str1 ="" 
        if m.tb_nam !=None: str1 =normalize(m.tb_nam,subjectList[i].nx,False)
        if j % 5!=4:            
            s.write(j+5,i+3,str1,h61)
            if m.diem_thi_lai!=None:
                tt+=1
                s.write(j+5,length+3+tt,str(m.diem_thi_lai),h61)
        else:     
            s.write(j+5,i+3,str1,h71)
            if m.diem_thi_lai!=None:
                tt+=1
                s.write(j+5,length+3+tt,str(m.diem_thi_lai),h71)
        
        if i==length-1:
            if j % 5!=4:            
                for ii in range(tt,3):
                    s.write(j+5,length+4+ii," ",h61)
                    
            else:        
                for ii in range(tt,3):
                    s.write(j+5,length+4+ii," ",h71)
    
    for i in range(numberPupil,55):
        for j in range(length+4):           
           if i % 5!=4:            
               s.write(i+5,j+3,'',h61)
           else:     
               s.write(i+5,j+3,'',h71)
    selected_class = Class.objects.get(id=class_id)
    selected_year = selected_class.year_id
    tbNamList = TBNam.objects.filter(year_id=selected_year, student_id__classes=class_id,student_id__attend__is_member=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday').distinct()
    for (i,tbNam) in enumerate(tbNamList):
        str1 ="" 
        if tbNam.tb_nam !=None: str1 =str(tbNam.tb_nam)  
        if i % 5!=4:            
            s.write(i+5,length+3,str1,h61)
        else:     
            s.write(i+5,length+3,str1,h71)

        for tt in range(i+1,55):
            if tt % 5!=4:            
                s.write(tt+5,length+3,'',h61)
            else:     
                s.write(tt+5,length+3,'',h71)
    
    printPage31(class_id,s,tbNamList,0,length+8)
    max = 56
    str1=u'Trong trang này có ... điểm được sửa chữa, trong đó môn:'
    for ss in subjectList:
        str1+=ss.name+u'.......điểm, '
    str1 = str1[:len(str1)-2]+'.'
    s.write_merge(max+5,max+9,0,length,str1,h8)
    
    s.write_merge(max+5,max+5,length+1,length+6,u'Ký xác nhận của',h9)
    s.write_merge(max+6,max+6,length+1,length+6,u'giáo viên chủ nhiệm',h9)
    
def printInTerm(class_id,book,termNumber):

    subjectList = Subject.objects.filter(class_id=class_id,primary__in=[0,termNumber,3,4]).order_by('index','name')    
    length = len(subjectList)
    numberPage = int((length+1)/2+1)
    
    if termNumber ==1:
        s  = book.add_sheet('Điểm HK I',True)
        ls = book.add_sheet('THKQ I',True)
    else:
        s = book.add_sheet('Điểm HK II',True)    
        ls = book.add_sheet('THKQ II',True)
    
             
    if termNumber == 1 :  printPage13(s,0,0,u'HỌC KỲ I')
    else               :  printPage13(s,0,0,u'HỌC KỲ II')
        
    s.set_paper_size_code(8)
    setHorz =[]
    
    for i in range(numberPage):
        setHorz.append(((i+1)*70,0,255))
    s.vert_page_breaks =[]    
    s.horz_page_breaks = setHorz
            
    for i in range(length/2):
        printPage14(class_id,s,termNumber,i,subjectList[2*i],subjectList[2*i+1],(i+1)*70,0,ls)
    i+=1     
    if length % 2==1:
        printPage14(class_id,s,termNumber,i,subjectList[2*i],None,(i+1)*70,0,ls)
    
    printPage20(class_id,termNumber,ls,length,subjectList)
    
def printFirstPage(class_id,book):
    x=0
    y=0
    selectedClass=Class.objects.get(id=class_id)
    yearString='Năm hoc:'+str(selectedClass.year_id.time)+'-'+str(selectedClass.year_id.time+1)
    className =u'Lớp: '+selectedClass.name
    
    s=book.add_sheet('Bia',True)
    s.set_paper_size_code(8)
    size=A3_WIDTH/7
    for i in range(7):
        s.col(i).width=size
        
    s.write_merge(x,x,y,y+6,'BỘ GIÁO DỤC VÀ ĐÀO TẠO',f2)
    s.write_merge(x+1,x+1,y,y+6,'SỞ GIÁO DỤC VÀ ĐÀO TẠO',f4)
    s.write_merge(x+2,x+2,y,y+6,'..................................................',f4)
    s.write_merge(x+30,x+30,y,y+6,'SỔ GỌI TÊN VÀ GHI ĐIỂM',f1)
    if (selectedClass.block_id.number<=9) & (selectedClass.block_id.number>=6):        
        s.write_merge(x+1,x+1,y,y+6,'SỞ GIÁO DỤC VÀ ĐÀO TẠO',f4)
        s.write_merge(x+2,x+2,y,y+6,'..................................................',f4)
        s.write_merge(x+32,x+32,y,y+6,'TRUNG HỌC CƠ SỞ',f4)
        s.write_merge(x+40,x+40,y,y+6,'TRƯỜNG TRUNG HỌC CƠ SỞ',f4)
        s.write_merge(x+41,x+41,y,y+6,selectedClass.year_id.school_id.name,f4)
        s.write_merge(x+50,x+50,y,y+3,'Xã(phường, thị trấn):....................................',f3)
        s.write_merge(x+50,x+50,y+4,y+6,'Huyện(quận,TX,TP thuộc tỉnh):...........................',f3)
        s.write_merge(x+52,x+52,y+0,y+6,'Tỉnh/TP:.................................................................................',f3)
        s.write_merge(x+54,x+54,y,y+3,className,f3)
        s.write_merge(x+54,x+54,y+4,y+6,yearString,f3)
    elif (selectedClass.block_id.number >= 10):        
        s.write_merge(x+32,x+32,y,y+6,'TRUNG HỌC PHỔ THÔNG',f4)
        s.write_merge(x+40,x+40,y,y+6,'TRƯỜNG TRUNG HỌC PHỔ THÔNG',f4)
        s.write_merge(x+41,x+41,y,y+6,selectedClass.year_id.school_id.name,f4)
        s.write_merge(x+50,x+50,y,y+3,'Huyện(quận,TX,TP thuộc tỉnh)....................................',f3)
        s.write_merge(x+50,x+50,y+4,y+6,'Tỉnh/TP:..............................',f3)
        s.write_merge(x+54,x+54,y,y+1,className,f3)
        s.write_merge(x+54,x+54,y+2,y+3,'Ban:.........................',f3)
        s.write_merge(x+54,x+54,y+4,y+6,yearString,f3)
        s.write_merge(x+58,x+58,y,y+6,'Các môn học tự chọn nâng cao(nếu là ban Cơ bản):......................................................................',f3)
    
    s.write_merge(x+62,x+62,y,y+2,'Giáo viên chủ nhiệm',h9)
    s.write_merge(x+63,x+63,y,y+2,'(Ký và ghi rõ họ, tên)',hh2)
    s.write_merge(x+62,x+62,y+4,y+6,'Hiệu trưởng',h9)
    s.write_merge(x+63,x+63,y+4,y+6,'(Ký, ghi rõ họ, tên và đóng dấu)',hh2)

def printPage2(class_id,book):
    x=0
    y=0
    selectedClass=Class.objects.get(id=class_id)    
    s=book.add_sheet('SYLL',True)
    s.set_paper_size_code(8)
    s.col(0).width=STT_WIDTH
    s.col(1).width=LASTNAME_WIDTH
    s.col(2).width=FIRSTNAME_WIDTH
    s.col(3).width=BIRTHDAY_WIDTH
    s.col(4).width=PLACE_WIDTH
    s.col(5).width=SEX_WIDTH
    s.col(6).width=DAN_TOC_WIDTH
    s.col(7).width=UU_TIEN_WIDTH
    s.col(8).width=A3_WIDTH- STT_WIDTH - LASTNAME_WIDTH - FIRSTNAME_WIDTH - BIRTHDAY_WIDTH-PLACE_WIDTH-SEX_WIDTH-DAN_TOC_WIDTH - UU_TIEN_WIDTH
    
    s.col(9).width=1000
    s.col(10).width=STT_WIDTH
    s.col(11).width=(A3_WIDTH-2*STT_WIDTH)/6
    s.col(12).width=(A3_WIDTH-2*STT_WIDTH)/6
    s.col(13).width=(A3_WIDTH-2*STT_WIDTH)/6
    s.col(14).width=(A3_WIDTH-2*STT_WIDTH)/6    
    s.col(15).width=(A3_WIDTH-2*STT_WIDTH)/3
    s.vert_page_breaks = [(9,0,65500)]    
    s.horz_page_breaks = []
    
    
    s.write_merge(x,x,y,y+8,'SƠ YẾU LÝ LỊCH HỌC SINH',h3)        
    s.write_merge(x+1,x+4,y,y,u'Số\nTT',h4)
    s.write_merge(x+1,x+4,y+1,y+2,u'Họ và tên',h4)
    s.write_merge(x+1,x+4,y+3,y+3,u'Ngày,\ntháng,\nnăm sinh',h4)
    s.write_merge(x+1,x+4,y+4,y+4,u'Nơi sinh',h4)
    s.write_merge(x+1,x+4,y+5,y+5,u'Nam\nnữ',h4)
    s.write_merge(x+1,x+4,y+6,y+6,u'Dân tộc',h4)
    s.write_merge(x+1,x+4,y+7,y+7,u'Con LS, con TB, con BB,\n con của người được hưởng\n chế độ như TB, con GĐ\n có công với CM ',h10)
    s.write_merge(x+1,x+4,y+8,y+8,u'Chỗ ở hiện nay ',h4)
    
    s.write_merge(x,x,y+10,y+15,'SƠ YẾU LÝ LỊCH HỌC SINH',h3)        
    s.write_merge(x+1,x+4,y+10,y+10,u'Số\nTT ',h4)
    s.write_merge(x+1,x+2,y+11,y+12,u'Họ và tên cha, nghề nghiệp ',f5)
    s.write_merge(x+1,x+2,y+13,y+14,u'Họ và tên mẹ , nghề nghiệp ',f5)
    s.write_merge(x+1,x+2,y+15,y+15,u'Những thay đổi cần chý ý của học sinh ',f5)

    s.write_merge(x+3,x+4,y+11,y+12,u'(hoặc người giám hộ) ',f6)
    s.write_merge(x+3,x+4,y+13,y+14,u'(hoặc người giám hộ) ',f6)
    if selectedClass.block_id.number>=10:
        comment ='(hoàn cảnh gia đình, nới ở, sức khỏe,\n chuyển ban trong quá trình học tập)'
    elif selectedClass.block_id.number>=6:        
        comment ='(hoàn cảnh gia đình, nới ở, sức khỏe)'
    s.write_merge(x+3,x+4,y+15,y+15,comment,f6)
    x=x+1
    
    pupilList = Pupil.objects.filter(classes=class_id,attend__is_member=True).order_by('index','first_name','last_name','birthday').distinct()
    i=0
    for p in pupilList:
        i +=1
        if i % 5 !=0:
            s.write(x+i+3,y,i,h6)
            s.write(x+i+3,y+1,p.last_name,last_name)
            s.write(x+i+3,y+2,p.first_name,first_name)
            s.write(x+i+3,y+3,p.birthday.strftime('%d/%m/%Y'),h6)
            s.write(x+i+3,y+4,p.birth_place,h6)
            s.write(x+i+3,y+5,p.sex,h6)
            s.write(x+i+3,y+6,p.dan_toc,h6)
            s.write(x+i+3,y+7,p.uu_tien,h6)
            s.write(x+i+3,y+8,p.current_address,h6)
            
            s.write(x+i+3,y+10,i,h6)
            s.write(x+i+3,y+11,p.father_name,last_name)
            s.write(x+i+3,y+12,p.father_job,first_name)            
            s.write(x+i+3,y+13,p.mother_name,last_name)
            s.write(x+i+3,y+14,p.mother_job,first_name)
            s.write(x+i+3,y+15,"",h6)
        else:    
            s.write(x+i+3,y,i,h7)
            s.write(x+i+3,y+1,p.last_name,last_name1)
            s.write(x+i+3,y+2,p.first_name,first_name1)
            s.write(x+i+3,y+3,p.birthday.strftime('%d/%m/%Y'),h7)
            s.write(x+i+3,y+4,p.birth_place,h7)
            s.write(x+i+3,y+5,p.sex,h7)
            s.write(x+i+3,y+6,p.dan_toc,h7)
            s.write(x+i+3,y+7,p.uu_tien,h7)
            s.write(x+i+3,y+8,p.current_address,h7)

            s.write(x+i+3,y+10,i,h7)
            s.write(x+i+3,y+11,p.father_name,last_name1)
            s.write(x+i+3,y+12,p.father_job,first_name1)            
            s.write(x+i+3,y+13,p.mother_name,last_name1)
            s.write(x+i+3,y+14,p.mother_job,first_name1)
            s.write(x+i+3,y+15,"",h7)
        
    for t in range(i+1,56):
        if t % 5 !=0:
            s.write(x+t+3,y,t,h6)
            s.write(x+t+3,y+1,"",last_name)
            s.write(x+t+3,y+2,"",first_name)
            s.write(x+t+3,y+3,"",h6)
            s.write(x+t+3,y+4,"",h6)
            s.write(x+t+3,y+5,"",h6)
            s.write(x+t+3,y+6,"",h6)
            s.write(x+t+3,y+7,"",h6)
            s.write(x+t+3,y+8,"",h6)
            
            s.write(x+t+3,y+10,t,h6)
            s.write(x+t+3,y+11,"",last_name)
            s.write(x+t+3,y+12,"",first_name)            
            s.write(x+t+3,y+13,"",last_name)
            s.write(x+t+3,y+14,"",first_name)
            s.write(x+t+3,y+15,"",h6)
        else:    
            s.write(x+t+3,y,t,h7)
            s.write(x+t+3,y+1,"",last_name1)
            s.write(x+t+3,y+2,"",first_name1)
            s.write(x+t+3,y+3,"",h7)
            s.write(x+t+3,y+4,"",h7)
            s.write(x+t+3,y+5,"",h7)
            s.write(x+t+3,y+6,"",h7)
            s.write(x+t+3,y+7,"",h7)
            s.write(x+t+3,y+8,"",h7)

            s.write(x+t+3,y+10,t,h7)
            s.write(x+t+3,y+11,"",last_name1)
            s.write(x+t+3,y+12,"",first_name1)            
            s.write(x+t+3,y+13,"",last_name1)
            s.write(x+t+3,y+14,"",first_name1)
            s.write(x+t+3,y+15,"",h7)
            
def printDiemDanh(class_id,book):
    x=0
    y=0
    line=70
    selectedClass=Class.objects.get(id=class_id)    
    s=book.add_sheet('DD',True)
    s.set_paper_size_code(8)
    s.col(0).width=STT_WIDTH
    s.col(1).width=LASTNAME_WIDTH
    s.col(2).width=FIRSTNAME_WIDTH
    size = (A3_WIDTH-STT_WIDTH-LASTNAME_WIDTH - FIRSTNAME_WIDTH) / 34
    for i in range(3,37):
        s.col(i).width=size
    setHorz =[]    
    for i in range(10):
        setHorz.append(((i+1)*line,0,255))
    s.vert_page_breaks =[]    
    s.horz_page_breaks = setHorz
        
    
    pupilList = Pupil.objects.filter(classes=class_id,attend__is_member=True).order_by('index','first_name','last_name','birthday').distinct()
    for (pg,month) in enumerate(range(7,17)):
        if month<=11:
            monthString = 'Tháng '+str(month % 12 +1)+' năm ' + str(selectedClass.year_id.time)
        else:            
            monthString = 'Tháng '+str(month % 12 +1)+' năm ' + str(selectedClass.year_id.time+1)
        sumPupilString='Tổng số học sinh của lớp '+str(len(pupilList))
        
        s.write_merge(x+pg*line,x+pg*line,y,y+2,monthString,f7)
        s.write_merge(x+pg*line,x+pg*line,y+3,y+36,sumPupilString,f71)
        s.write_merge(x+pg*line+1,x+pg*line+4,y,y,'Số\nTT',h4)
        
        s.write_merge(x+pg*line+1,x+pg*line+4,y+1,y+1,'Họ và tên',f8)
        s.write_merge(x+pg*line+1,x+pg*line+2,y+2,y+2,'Ngày',f81)
        s.write_merge(x+pg*line+3,x+pg*line+4,y+2,y+2,'Thứ',f82)
        for i in range(1,32):
            s.write_merge(x+pg*line+1,x+pg*line+2,y+i+2,y+i+2,i,h5)
            s.write_merge(x+pg*line+3,x+pg*line+4,y+i+2,y+i+2,"",h5)
            
        s.write_merge(x+pg*line+1,x+pg*line+2,y+34,y+36,'TS ngày\nnghỉ',h5)
        s.write_merge(x+pg*line+3,x+pg*line+4,y+34,y+34,'TS',h5)
        s.write_merge(x+pg*line+3,x+pg*line+4,y+35,y+35,'p',h5)
        s.write_merge(x+pg*line+3,x+pg*line+4,y+36,y+36,'k',h5)
        
        i=0
        for p in pupilList:
            i+=1
            if i % 5 !=0:
                s.write(x+pg*line+i+4,y,i,h6)
                s.write(x+pg*line+i+4,y+1,p.last_name,last_name)
                s.write(x+pg*line+i+4,y+2,p.first_name,first_name)
                for j in range(31):
                    s.write(x+pg*line+i+4,y+j+3,'',h6)                    
            else:    
                s.write(x+pg*line+i+4,y,i,h7)
                s.write(x+pg*line+i+4,y+1,p.last_name,last_name1)
                s.write(x+pg*line+i+4,y+2,p.first_name,first_name1)
                for j in range(31):
                    s.write(x+pg*line+i+4,y+j+3,'',h7)                    
        
        for t in range(i+1,56):
            if t % 5 !=0:
                s.write(x+pg*line+t+4,y,t,h6)
                s.write(x+pg*line+t+4,y+1,"",last_name)
                s.write(x+pg*line+t+4,y+2,"",first_name)
                for j in range(34):
                    s.write(x+pg*line+t+4,y+j+3,'',h6)                    
            else:    
                s.write(x+pg*line+t+4,y,t,h7)
                s.write(x+pg*line+t+4,y+1,"",last_name1)
                s.write(x+pg*line+t+4,y+2,"",first_name1)
                for j in range(34):
                    s.write(x+pg*line+t+4,y+j+3,'',h7)                    
    #diemDanhList=DiemDanh.objects.filter(student_id__clases=class_id,student_id__attend__is_member=True)
    beginDay=datetime.date(selectedClass.year_id.time,8,1)
    endDay  =datetime.date(selectedClass.year_id.time+1,6,1)
    tong=0
    sum=[0]*10
    for i in range(10):
        sum[i]=[0]*34
    for (i,p) in enumerate(pupilList):
        diemDanhList = DiemDanh.objects.filter(student_id=p.id,time__gte=beginDay,time__lt=endDay)
        #diemDanhList=DiemDanh.objects.filter(student_id=p.id)
        tongCoPhep = [0]*13
        tongKoPhep = [0]*13
        for dd in diemDanhList:
            month=dd.time.month
            if month >=8:
                month=month-8
            else:
                month=month+4
            loai=''        
            if dd.loai==u'Có phép':
                tongCoPhep[month]+=1
                loai='p'
            else:    
                tongKoPhep[month]+=1
                loai='k'                
            xPos=x+month*line + i +5
            yPos=dd.time.day+2
            if loai!= '':
                s.write(xPos,yPos,loai,h6)
                sum[month][yPos-3]+=1
                sum[month][31]+=1
                if loai=='p':
                    sum[month][32]+=1
                else:    
                    sum[month][33]+=1
        for j in range(10):
            s.write(x+j*line+i+5,35,tongCoPhep[j],h6)
            s.write(x+j*line+i+5,36,tongKoPhep[j],h6)
            s.write(x+j*line+i+5,34,tongKoPhep[j]+tongCoPhep[j],h6)
    for j in range(10):
        s.write_merge(x+j*line+59,x+j*line+59,1,2,'Tổng số',h7)
        for t in range(34):
            s.write(x+j*line+59,t+3,sum[j][t],h7)
            
def markBookClass(class_id):
    tt1 = time.time()
    book = Workbook(encoding = 'utf-8')
    
    printFirstPage(class_id,book)       
    printPage2(class_id,book) 
    printDiemDanh(class_id,book)
    printInTerm(class_id,book,1)
    printInTerm(class_id,book,2)
    printPage30(class_id,book)
    
    book.set_active_sheet(0)
    selectedClass=Class.objects.get(id=class_id)
    response = HttpResponse(mimetype='application/ms-excel')
    name = 'soGhiDiemGoiTen%s.xls' % unicode(selectedClass.name)
    name1=name.replace(' ','_')
    response['Content-Disposition'] = u'attachment; filename=%s' % name1
    book.save(response)
    tt2= time.time()
    print (tt2-tt1)
    return response

def printMarkBook(request,class_id=-2):
    user = request.user
    if not user.is_authenticated():
        return HttpResponseRedirect( reverse('login'))
    
    message=None
    currentTerm=get_current_term(request)
    try:
        if in_school(request,currentTerm.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))
    teaching_class=None
    if (get_position(request)==3) & (get_level(request)=='T'):
        teaching_class = user.teacher.current_homeroom_class()
        if teaching_class==None:
            return HttpResponseRedirect('/school')
        else:
            class_id=teaching_class.id
    elif (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')

    blockList = Block.objects.filter(school_id = currentTerm.year_id.school_id).order_by("number")
    classList = Class.objects.filter(year_id = currentTerm.year_id).order_by("id")

    class_id  = int(class_id)
    if class_id!=-2 :
        return markBookClass(class_id)
            
    t = loader.get_template(os.path.join('school/report','print_mark_book.html'))
    c = RequestContext(request, {"message":message,
                                 'classList':classList,
                                 'blockList':blockList,
                                 'classChoice':class_id,
                                 'teaching_class':teaching_class,
                                }
                       )
    return HttpResponse(t.render(c))

def printPage15(book,class_id,number,mon1,mon2,mon3):
    s = book.add_sheet('trang'+str(number+13) ,True)
    book.set_active_sheet(number)
    s.set_paper_size_code(8)
        
    s.col(0).width = s1
    
    s.col(1).width = m6
    s.col(2).width = m7
    s.col(3).width = m8
    s.col(4).width = m9
    s.col(5).width = m10
    
    s.col(6).width = m6
    s.col(7).width = m7
    s.col(8).width = m8
    s.col(9).width = m9
    s.col(10).width = m10

    s.col(11).width = m6
    s.col(12).width = m7
    s.col(13).width = m8
    s.col(14).width = m9
    s.col(15).width = m10
    
    s.write_merge(0,0,0,15,u'HỌC KỲ I',h3)    
    s.write_merge(1,3,0,0,u'Số\nTT',h4)
        
    printASubject(class_id,s,mon1,1,1)
    printASubject(class_id,s,mon2,1,6)
    printASubject(class_id,s,mon3,1,11)
    printSTT(s,55,4,0)
    
    max=55
    
    s.write_merge(max+5,max+5,0,11,u'Trong trang này có......... điểm được sửa chữa,'+
u' trong đó môn: '+ mon1+u'....... điểm, '+ mon2+u'.......điểm, '+mon3+u'.......điểm',h8)

    s.write_merge(max+6,max+6,0,11,u'Ghi chú: số TT ở trang này là số TT ở trang '+str(number+12),h8)
    
    s.write_merge(max+5,max+5,12,15,u'Ký xác nhận của',h9)
    s.write_merge(max+6,max+6,12,15,u'giáo viên chủ nhiệm',h9)


def printSTT(s,max,x,y):
    for t in range(1,max+1):
        if t % 5 !=0:
            s.write(x+t-1,y,t,h6)
        else:    
            s.write(x+t-1,y,t,h7)



@need_login
def exportMark(request,term_id,subject_id,colMieng=4,col15Phut=4,colMotTiet=4):
    tt1 = time.time()

    user = request.user

    selectedSubject = Subject.objects.get(id=subject_id)
    try:        
        if in_school(request,selectedSubject.class_id.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))
    
    position= get_position(request)
    if position==4:
        pass
    elif position ==3:
        try:
            if (selectedSubject.class_id.teacher_id.id==request.user.teacher.id):
                pass
            elif (selectedSubject.teacher_id.id != request.user.teacher.id):  
                return HttpResponseRedirect('/school')
        except Exception as e:    
            return HttpResponseRedirect('/school')
    else:    
            return HttpResponseRedirect('/school')

    markList = Mark.objects.filter(subject_id=subject_id,term_id=term_id,current=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday')
    decodeMarkList,maxColMieng,maxCol15Phut,maxColMotTiet = getDecodeMark(markList)
    maxColMieng  = max(maxColMieng,MAX_VIEW,int(colMieng))
    maxCol15Phut = max(maxCol15Phut,MAX_VIEW,int(col15Phut))
    maxColMotTiet= max(maxColMotTiet,MAX_VIEW,int(colMotTiet))

    selectedTerm   = Term.objects.get(id=term_id)
    book = Workbook(encoding = 'utf-8')
    str1=u'BẢNG ĐIỂM LỚP '+selectedSubject.class_id.name.upper()+u' MÔN '+selectedSubject.name.upper()+u'  HỌC KỲ'    
    if selectedTerm.number==1:
        str1+=' I'
    else:
        str1+=' II'  
              
    str3 =selectedSubject.class_id.name+'_'+selectedSubject.name+'_HK'+str(selectedTerm.number)       
    sstr2='bang_diem_'+str3
    sstr2=sstr2.replace(' ','_')  
    s=book.add_sheet(str3,True)
    if selectedTerm.number==1: numberCol=4+maxColMieng+maxCol15Phut+maxColMotTiet+2
    else                     : numberCol=4+maxColMieng+maxCol15Phut+maxColMotTiet+4
    sumCol = maxColMieng+maxCol15Phut+maxColMotTiet
    s.set_portrait(0)
    s.col(0).width=s1
    s.col(1).width=s2
    s.col(2).width=s3
    s.col(3).width=s4
    
    size = (SIZE_PAGE_WIDTH-s1-s2-s3-s4)/(numberCol-4) 
    for i in range(4,numberCol):
        s.col(i).width = size
    s.set_top_margin(0)  
    s.row(0).hidden=True
    s.row(1).hidden=True
    s.row(2).hidden=True
    str2 = 'Năm học '+ str(selectedTerm.year_id.time)+'-'+str(selectedTerm.year_id.time+1)   
    s.write_merge(4,4,0,19,str1,h9 )
    s.write_merge(5,5,0,19,str2,h9 )
    
    s.write_merge(8,10,0,0,u'Số\nTT',h4)
    s.write_merge(8,10,1,2,u'Họ và tên',h4)
    s.write_merge(8,10,3,3,u'Ngày sinh',h4)
    s.write_merge(8,9,4,3+maxColMieng,u'Điểm hs 1-Miệng',h4)
    s.write_merge(8,9,4+maxColMieng,3+maxColMieng+maxCol15Phut,u'Điểm hs 1-Viết',h4)
    s.write_merge(8,9,4+maxColMieng+maxCol15Phut,3+maxColMieng+maxCol15Phut+maxColMotTiet,u'Điểm hs 2',h4)
    s.write_merge(8,10,4+sumCol,4+sumCol,u'Thi ck',h4)
    for i in range(1,maxColMieng+1):
        s.write(10,i+3,i,h4)
    for i in range(1,maxCol15Phut+1):
        s.write(10,3+maxColMieng+i,i,h4)
    for i in range(1,maxColMotTiet+1):
        s.write(10,3+maxColMieng+maxCol15Phut+i,i,h4)
    if selectedTerm.number ==1:
        s.write_merge(8,10,5+sumCol,5+sumCol,'TB',h4)
    else:
        s.write_merge(8,9,5+sumCol,7+sumCol,'TB',h4)
        s.write(10,5+sumCol,'HK I',h4)
        s.write(10,6+sumCol,'HK II',h4)
        s.write(10,7+sumCol,'CN',h4)
        hk1List =  Mark.objects.filter(subject_id=subject_id,term_id__number=1,current=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday') 
        cnList  =  TKMon.objects.filter(subject_id=subject_id,current=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday')
    if selectedSubject.nx==True:
        checkNx=1
    else:
        checkNx=0
            
    for (i,(m,dm)) in enumerate(zip(markList,decodeMarkList)):
        if i % 5 !=4: h=h61
        else        : h=h71

        s.write(11+i,0,i+1,h)
        if i % 5!=4:
            s.write(11+i,1,m.student_id.last_name,last_name)
            s.write(11+i,2,m.student_id.first_name,first_name)
        else:
            s.write(11+i,1,m.student_id.last_name,last_name1)
            s.write(11+i,2,m.student_id.first_name,first_name1)

        tempStr = m.student_id.birthday.strftime('%d/%m/%Y')
        s.write(11+i,3,tempStr,h)

        maxLength=[maxColMieng,maxCol15Phut,maxColMotTiet,1]
        j=4
        order=0
        for len,aList in dm:
            for (t,mm) in enumerate(aList):
                s.write(11+i,j+t,normalize(mm,checkNx),h)
            for t in range(len,maxLength[order]):
                s.write(11+i,j+t,"",h)
            j+=maxLength[order]
            order+=1
        s.write(11+i,j,normalize(m.ck,checkNx),h)
        s.write(11+i,j,normalize(m.ck,checkNx,1),h)
        if selectedTerm.number==2:
            s.write(11+i,j+1,normalize(hk1List[i].tb,checkNx,1),h)
            s.write(11+i,j+2,normalize(m.tb,checkNx,1),h)
            s.write(11+i,j+3,normalize(cnList[i].tb_nam,checkNx,1),h)
        else:
            s.write(11+i,j+1,normalize(m.tb,checkNx,1),h)
        """
        if m.mieng_1!=None: strs[1]=normalize(m.mieng_1,checkNx)
        if m.mieng_2!=None: strs[2]=normalize(m.mieng_2,checkNx)
        if m.mieng_3!=None: strs[3]=normalize(m.mieng_3,checkNx)
        if m.mieng_4!=None: strs[4]=normalize(m.mieng_4,checkNx)
        if m.mieng_5!=None: strs[5]=normalize(m.mieng_5,checkNx)
        if m.mlam_1 !=None: strs[6]=normalize(m.mlam_1,checkNx)
        if m.mlam_2 !=None: strs[7]=normalize(m.mlam_2,checkNx)
        if m.mlam_3 !=None: strs[8]=normalize(m.mlam_3,checkNx)
        if m.mlam_4 !=None: strs[9]=normalize(m.mlam_4,checkNx)
        if m.mlam_5 !=None: strs[10]=normalize(m.mlam_5,checkNx)
        if m.mot_tiet_1!=None: strs[11]=normalize(m.mot_tiet_1,checkNx)
        if m.mot_tiet_2!=None: strs[12]=normalize(m.mot_tiet_2,checkNx)
        if m.mot_tiet_3!=None: strs[13]=normalize(m.mot_tiet_3,checkNx)
        if m.mot_tiet_4!=None: strs[14]=normalize(m.mot_tiet_4,checkNx)
        if m.mot_tiet_5!=None: strs[15]=normalize(m.mot_tiet_5,checkNx)        
        if m.ck!=None: strs[16]=normalize(m.ck,checkNx)
        if m.tb!=None: strs[17]=normalize(m.tb,checkNx,1)
        if selectedTerm.number==2:
            strs[18]=strs[17]
            strs[17]=''
            if hk1List[i].tb!=None    :strs[17]=normalize(hk1List[i].tb,checkNx,1)
            if cnList[i].tb_nam!=None :strs[19]=normalize(cnList[i].tb_nam,checkNx,1)
        

        for j in range(numberCol-3):
            s.write(11+i,3+j,strs[j],h
        """
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % to_en1(sstr2)
    book.save(response)
    tt2= time.time()
    print (tt2-tt1)
    return response

def count1Excel(year_id,number,list,sumsumsum,allList):
    tt1 = time.time()
    
    book = Workbook(encoding = 'utf-8')
    selectedYear = Year.objects.get(id=year_id)
    if number==1:
        str1='HKI'
        str2=u'HỌC KỲ I NĂM HỌC '+str(selectedYear.time)+'-'+str(selectedYear.time+1)
    elif number==2:
        str1='HKII'
        str2=u'HỌC KỲ II NĂM HỌC '+str(selectedYear.time)+'-'+str(selectedYear.time+1)
    else:
        str1='CaNam'        
        str2=u'CẢ NĂM NĂM HỌC '+str(selectedYear.time)+'-'+str(selectedYear.time+1)
    sheetName ='tkHocLuc'+str1+str(selectedYear.time)+'-'+str(selectedYear.time+1) 
    s=book.add_sheet(sheetName,True)
    s.set_portrait(0)
    s.col(0).width=s1    
    s.col(1).width=s2-s1    
    size = (SIZE_PAGE_WIDTH-s2)/23 
    for i in range(2,25):
        if i % 2==1:
            s.col(i).width = size-100
        else:    
            s.col(i).width = size+100
    printHeader(s,0,0,selectedYear.school_id,9)
    printCongHoa(s,0,10,13)

    s.write_merge(4,4,0,24,'THỐNG KÊ HỌC LỰC, HẠNH KIỂM, DANH HIỆU',h40)
    s.write_merge(5,5,0,24,str2,h40)
    x=7
    y=1    
    s.write_merge(x,x+2,y-1,y-1,u'STT',h4)    
    s.write_merge(x,x+2,y,y,u'Lớp',h4)    
    s.write_merge(x,x+2,y+1,y+1,u'Sĩ\nSố',h4)    
    s.write_merge(x,x,y+2,y+11,u'Học lực',h4)    
    s.write_merge(x,x,y+12,y+19,u'Hạnh kiểm',h4)    
    s.write_merge(x,x,y+20,y+23,u'Danh hiệu',h4)
        
    s.write_merge(x+1,x+1,y+2,y+3,'Giỏi',h4)
    s.write_merge(x+1,x+1,y+4,y+5,'Khá',h4)
    s.write_merge(x+1,x+1,y+6,y+7,'TB',h4)
    s.write_merge(x+1,x+1,y+8,y+9,'Yếu',h4)
    s.write_merge(x+1,x+1,y+10,y+11,'Kém',h4)
    
    s.write_merge(x+1,x+1,y+12,y+13,'Tốt',h4)
    s.write_merge(x+1,x+1,y+14,y+15,'Khá',h4)
    s.write_merge(x+1,x+1,y+16,y+17,'TB',h4)
    s.write_merge(x+1,x+1,y+18,y+19,'Yếu',h4)
    
    s.write_merge(x+1,x+1,y+20,y+21,'HSG',h4)
    s.write_merge(x+1,x+1,y+22,y+23,'HSTT',h4)
    for i in range(11):
        s.write(x+2,y+2*i+2,'sl',h4)
        s.write(x+2,y+2*i+3,'%' ,h4)
    
    
    i=0
    for b,sum,total,list1 in list:
        stt=0
        for name,ss,l in list1:
            i+=1
            stt+=1                
            s.write(x+i+2,y-1,stt,h82)
            s.write(x+i+2,y,name,h82)
            s.write(x+i+2,y+1,ss,h72)
            j=0
            for u,v in l :
                v=round(v+e, 2)
                s.write(x+i+2,y+2*j+2,u,h72)
                s.write(x+i+2,y+2*j+3,v,h73)
                j+=1
                
        i+=1
        str11=u'Khối '+str(b.number)
        s.write(x+i+2,y-1,'',h41)
        s.write(x+i+2,y,str11,h41)
        s.write(x+i+2,y+1,sum,h72)        
        j=0
        for u,v in total:
            v=round(v+e, 2)                            
            s.write(x+i+2,y+2*j+2,u,h72)
            s.write(x+i+2,y+2*j+3,v,h73)
            j+=1
        i+=1
        s.write(x+i+2,y-1,'',h41)
        s.write(x+i+2,y,'',h5)
        s.write(x+i+2,y+1,'',h72)        
        j=0
        for u,v in total:
            s.write(x+i+2,y+2*j+2,'',h72)
            s.write(x+i+2,y+2*j+3,'',h72)
            j+=1
    i+=1    
    s.write(x+i+2,y,u'Toàn trường',h41)
    s.write(x+i+2,y+1,sumsumsum,h72)
    j=0
    for u,v in allList:
        v=round(v+e, 2)        
        s.write(x+i+2,y+2*j+2,u,h72)
        s.write(x+i+2,y+2*j+3,v,h73)
        j+=1  
        
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % sheetName
    book.save(response)
    tt2= time.time()
    print (tt2-tt1)
    return response

def count2Excel(year_id,number,subjectName,type,modeView,list,allList,sumsumsum,isComment):
    tt1 = time.time()
    
    book = Workbook(encoding = 'utf-8')
    selectedYear = Year.objects.get(id=year_id)

    if number==1:
        str1='HKI'
        str2=u'HỌC KỲ I NĂM HỌC '+str(selectedYear.time)+'-'+str(selectedYear.time+1)
    elif number==2:
        str1='HKII'
        str2=u'HỌC KỲ II NĂM HỌC '+str(selectedYear.time)+'-'+str(selectedYear.time+1)
    else:
        str1='CaNam'        
        str2=u'CẢ NĂM NĂM HỌC '+str(selectedYear.time)+'-'+str(selectedYear.time+1)
    if   (type==1) & (modeView==1):
        str3='TBTheoLop'        
        titleString=u'THỐNG KÊ ĐIỂM TRUNG BÌNH THEO LỚP-MÔN '+unicode(subjectName.upper()) 
    elif (type==1) & (modeView==2):
        str3='TBTheoGiaoVien'        
        titleString=u'THỐNG KÊ ĐIỂM TRUNG BÌNH THEO GIÁO VIÊN-MÔN '+unicode(subjectName.upper())
    elif (type==2) & (modeView==1):      
        str3='ThiTheoLop'        
        titleString=u'THỐNG KÊ ĐIỂM THI CUỐI KÌ THEO LỚP-MÔN '+unicode(subjectName.upper()) 
    elif (type==2) & (modeView==2):      
        str3='ThiTheoGiaoVien'        
        titleString=u'THỐNG KÊ ĐIỂM THI CUỐI KÌ THEO GIÁO VIÊN-MÔN '+unicode(subjectName.upper())
         
    sheetName ='tkDiem'+str3+str1+str(selectedYear.time)+'-'+str(selectedYear.time+1) 
    s=book.add_sheet('tkDiem',True)
    s.set_portrait(0)
    s.col(0).width=s1    
    size = (SIZE_PAGE_WIDTH-s1)/16 
    s.col(1).width=2*size
    s.col(2).width=size
    s.col(3).width=3*size    
    for i in range(4,13):
        if i % 2==1:
            s.col(i).width = size-100
        else:    
            s.col(i).width = size+100

            
    printHeader(s,0,0,selectedYear.school_id,4)
    printCongHoa(s,0,4,8)
    x=7
    y=1    
    s.write_merge(x-3,x-3,0,12,titleString,h40)
    s.write_merge(x-2,x-2,0,12,str2,h40)
    s.write_merge(x,x+1,y-1,y-1,u'STT',h4)
    s.write_merge(x,x+1,y,y,u'Lớp',h4)
    s.write_merge(x,x+1,y+1,y+1,u'Sĩ\nSố',h4)
    s.write_merge(x,x+1,y+2,y+2,u'Giáo viên\ngiảng dạy',h4)
    if not isComment:
        s.write_merge(x,x,y+3,y+4,'8 - 10',h4)
        s.write_merge(x,x,y+5,y+6,'6.5 - 7.9',h4)
        s.write_merge(x,x,y+7,y+8,'5 - 6.4',h4)
        s.write_merge(x,x,y+9,y+10,'3.5 - 4.9',h4)
        s.write_merge(x,x,y+11,y+12,'0 - 3.4',h4)
        numberCol  = 5
    else:
        s.write_merge(x,x,y+3,y+4,u'Đạt',h4)
        s.write_merge(x,x,y+5,y+6,u'Không đạt',h4)
        numberCol = 2

    for i in range(numberCol):
        s.write(x+1,y+2*i+3,'sl',h4)
        s.write(x+1,y+2*i+4,'%' ,h4)

    i=0
    for b,sum,total,list1 in list:
        stt=0
        for name,ss,teacherName,l in list1:
            i+=1
            stt+=1                
            s.write(x+i+1,y-1,stt,h82)
            s.write(x+i+1,y,name,h82)
            s.write(x+i+1,y+1,ss,h72)
            s.write(x+i+1,y+2,teacherName,h82)
            j=0
            for u,v in l :
                v=round(v+e, 2)
                s.write(x+i+1,y+2*j+3,u,h72)
                s.write(x+i+1,y+2*j+4,v,h73)
                j+=1

        i+=1
        str11=b
        s.write(x+i+1,y-1,'',h41)
        s.write(x+i+1,y,str11,h41)
        s.write(x+i+1,y+1,sum,h72)
        s.write(x+i+1,y+2,'',h41)
        j=0
        for u,v in total:
            v=round(v+e, 2)                            
            s.write(x+i+1,y+2*j+3,u,h72)
            s.write(x+i+1,y+2*j+4,v,h73)
            j+=1
        i+=1
        s.write(x+i+1,y-1,'',h41)
        s.write(x+i+1,y,'',h5)
        s.write(x+i+1,y+1,'',h72)
        s.write(x+i+1,y+2,'',h72)
        j=0
        for u,v in total:
            s.write(x+i+1,y+2*j+3,'',h72)
            s.write(x+i+1,y+2*j+4,'',h72)
            j+=1
    i+=1    
    s.write(x+i+1,y,u'Toàn trường',h41)
    s.write(x+i+1,y+1,sumsumsum,h72)
    s.write(x+i+1,y+2,'',h72)
    j=0
    for u,v in allList:
        v=round(v+e, 2)        
        s.write(x+i+1,y+2*j+3,u,h72)
        s.write(x+i+1,y+2*j+4,v,h73)
        j+=1  
        
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % sheetName
    book.save(response)
    tt2= time.time()
    print (tt2-tt1)
    return response
# in phieu bao diem
def printMarkToExcel(termNumber,selectedClass,checkNxList,s,pupilList,markList,tkMonList,ddHKList,tbHKList,TBNamList,ddHK1List=None):
    today=datetime.datetime.now()
    if selectedClass.teacher_id!=None:
        nameTeacher=selectedClass.teacher_id.last_name+' '+selectedClass.teacher_id.first_name
    else:
        nameTeacher=''
    school = selectedClass.year_id.school_id
    x=4
    y=0
    i=0
    numberLine=50
    if termNumber==1:
        yearString='Học kỳ I - ' + 'Năm học '+ str(selectedClass.year_id.time)+'-'+str(selectedClass.year_id.time+1)
    else:     
        yearString='Học kỳ II - '+ 'Năm học '+ str(selectedClass.year_id.time)+'-'+str(selectedClass.year_id.time+1)
        
    for p in pupilList:
        
        printHeader(s,i*numberLine+x-4,y,school)
        printCongHoa(s,i*numberLine+x-4,y+4,5)
        s.write_merge(x+i*numberLine,x+i*numberLine,y,y+9,'PHIẾU BÁO ĐIỂM',h3)
        s.write_merge(x+i*numberLine+1,x+i*numberLine+1,y,y+9,yearString,h8center)
        nameString =u'Họ và tên: '+unicode(p.last_name)+' '+unicode(p.first_name)
        
        s.write_merge(x+i*numberLine+3,x+i*numberLine+3,y,y+4,nameString,h8)
        birthStr='Ngày sinh: '+p.birthday.strftime('%d/%m/%Y')
        s.write_merge(x+i*numberLine+3,x+i*numberLine+3,y+5,y+6,birthStr,h8)
        classString=u'Lớp: '+selectedClass.name        
        s.write_merge(x+i*numberLine+3,x+i*numberLine+3,y+7,y+9,classString,h8)
        s.write(x+i*numberLine+5,y,'STT',h92)
        s.write(x+i*numberLine+5,y+1,'Môn học',h92)
        s.write_merge(x+i*numberLine+5,x+i*numberLine+5,y+2,y+4,'Điểm hệ số 1',h92)
        s.write_merge(x+i*numberLine+5,x+i*numberLine+5,y+5,y+6,'Điểm hệ số 2',h92)
        s.write(x+i*numberLine+5,y+7,'KTHK',h92)
        s.write(x+i*numberLine+5,y+8,'TB',h92)
        if termNumber==2:
            s.write(x+i*numberLine+5,y+9,'TBCN',h92)            
        i+=1
    j=0
    for l in markList:
        i=0
        j+=1    
        for m in l:     
            s.write(x+i*numberLine+5+j,y,j,h82)        
            s.write(x+i*numberLine+5+j,y+1,m.subject_id.name,h82)
            hs1str=m.toString(0,True,checkNxList[j-1])+m.toString(1,True,checkNxList[j-1])
            hs2str=m.toString(2,True,checkNxList[j-1])

            s.write_merge(x+i*numberLine+5+j,x+i*numberLine+5+j,y+2,y+4,hs1str,h82)
            s.write_merge(x+i*numberLine+5+j,x+i*numberLine+5+j,y+5,y+6,hs2str,h82)
            ckstr=''
            if m.ck: ckstr+=normalize(m.ck,checkNxList[j-1])+' '         
            s.write(x+i*numberLine+5+j,y+7,ckstr,h82)
            tbstr=''
            if m.tb:
                if checkNxList[j-1]==0:
                    tbstr+=str(m.tb)
                else:
                    tbstr=normalize(m.tb,1)
                             
            s.write(x+i*numberLine+5+j,y+8,tbstr,h82)
            i+=1
    if termNumber==2:        
        j=0  
        for aTKMonList in tkMonList:
            i=0
            j+=1      
            for tkMon in aTKMonList:
                tkMonStr=''
                if tkMon.tb_nam!=None:
                    if checkNxList[j-1]==0: 
                        tkMonStr=str(tkMon.tb_nam)
                    else:
                        tkMonStr=normalize(tkMon.tb_nam,1)    
                s.write(x+i*numberLine+5+j,y+9,tkMonStr,h82)
                i+=1
                    
            
    i=0  
    for dd,tbhk,tbNam in zip(ddHKList,tbHKList,TBNamList):
        if termNumber==1:
            s.write_merge(x+i*numberLine+7+j,x+i*numberLine+8+j,y,y+1,'Tổng kết HK I',h82)
        else:    
            s.write_merge(x+i*numberLine+7+j,x+i*numberLine+8+j,y,y+1,'Tổng kết HK II',h82)
        s.write(x+i*numberLine+7+j,y+2,'TB',h82)
        s.write(x+i*numberLine+7+j,y+3,'Học lực',h82)
        s.write(x+i*numberLine+7+j,y+4,'Hạnh kiểm',h82)
        s.write(x+i*numberLine+7+j,y+5,'Danh hiệu',h82)
        s.write(x+i*numberLine+7+j,y+6,'Nghỉ có phép',h82)
        s.write_merge(x+i*numberLine+7+j,x+i*numberLine+7+j,y+7,y+8,'Nghỉ không phép',h82)
        if tbhk.tb_hk!=None:
            s.write(x+i*numberLine+8+j,y+2,str(tbhk.tb_hk),h82)
        else:
            s.write(x+i*numberLine+8+j,y+2,'',h82)
        s.write(x+i*numberLine+8+j,y+3,convertHlToVietnamese(tbhk.hl_hk),h82)
        
        if termNumber==1:
            s.write(x+i*numberLine+8+j,y+4,convertHkToVietnamese(tbNam.term1),h82)
        else:    
            s.write(x+i*numberLine+8+j,y+4,convertHkToVietnamese(tbNam.term2),h82)
            
        s.write(x+i*numberLine+8+j,y+5,convertDanhHieu(tbhk.danh_hieu_hk),h82)        
        s.write(x+i*numberLine+8+j,y+6,dd.co_phep,h82)
        s.write_merge(x+i*numberLine+8+j,x+i*numberLine+8+j,y+7,y+8,dd.khong_phep,h82)
        
        s.write_merge(x+i*numberLine+12+j,x+i*numberLine+12+j,y,y+3,'Ý kiến của phụ huynh',h8)    
        s.write_merge(x+i*numberLine+12+j,x+i*numberLine+12+j,y+5,y+8,'Ý kiến của GVCN',h8)
        for t in range(1,6):
            s.write_merge(x+i*numberLine+12+j+t,x+i*numberLine+12+j+t,y,y+3,'......................................................................',h8)    
            s.write_merge(x+i*numberLine+12+j+t,x+i*numberLine+12+j+t,y+5,y+8,'.....................................................................',h8)
        dateStr='Ngày ' + str(today.day)+' tháng '+str(today.month)+' năm '+str(today.year)

        s.write_merge(x+i*numberLine+16+j+t,x+i*numberLine+16+j+t,y+6,y+8,dateStr,h8)
        s.write_merge(x+i*numberLine+17+j+t,x+i*numberLine+17+j+t,y+6,y+8,'Giáo viên chủ nhiệm',h8)
        s.write_merge(x+i*numberLine+21+j+t,x+i*numberLine+21+j+t,y+6,y+8,nameTeacher,h8)
        i+=1
        
            
        
    if termNumber==2:
        i=0
        for dd1,dd2,tbNam in zip(ddHK1List,ddHKList,TBNamList):
            s.write_merge(x+i*numberLine+9+j,x+i*numberLine+9+j,y,y+1,'Cả năm',h82)
            s.write(x+i*numberLine+9+j,y+2,tbNam.tb_nam,h82)
            s.write(x+i*numberLine+9+j,y+3,convertHlToVietnamese(tbNam.hl_nam),h82)
            s.write(x+i*numberLine+9+j,y+4,convertHkToVietnamese(tbNam.year),h82)
            s.write(x+i*numberLine+9+j,y+5,convertDanhHieu(tbNam.danh_hieu_nam),h82)
            if (dd1.co_phep!=None) & (dd2.co_phep!=None):
                coPhep=dd1.co_phep+dd2.co_phep
            else:
                coPhep=''
                    
            if (dd1.khong_phep!=None) & (dd2.khong_phep!=None):
                khongPhep=dd1.khong_phep+dd2.khong_phep
            else:
                khongPhep=''    
                
            s.write(x+i*numberLine+9+j,y+6,coPhep,h82)
            s.write_merge(x+i*numberLine+9+j,x+i*numberLine+9+j,y+7,y+8,khongPhep,h82)

            if   tbNam.len_lop:
                lenLopStr='Thuộc diện: Được lên lớp.'
            elif tbNam.len_lop==False:
                lenLopStr='Thuộc diện: Không được lên lớp.'
            elif tbNam.thi_lai:
                lenLopStr='Thuộc diện: kiểm tra lại trong hè.'
            elif tbNam.ren_luyen_lai:                         
                lenLopStr='Thuộc diện: rèn luyện thêm trong hè.'
            else:
                lenLopStr='Thuộc diện: Chưa được xếp loại.'        
            s.write_merge(x+i*numberLine+11+j,x+i*numberLine+11+j,y,y+3,lenLopStr,h8)
            i+=1 
    
            
               
        
def setSizeOfMarkClass(s,numberPage):
    s.set_paper_size_code(9)
    setHorz =[]    
    for i in range(numberPage):
        setHorz.append(((i+1)*50,0,255))
   # s.vert_page_breaks =[]    
    s.horz_page_breaks = setHorz
    s1=1000
    s2=3000
    s.col(0).width=s1
    s.col(1).width=s2
    size = int((A4_WIDTH-s1-s2)/8)
    for i in range(2,6):
        s.col(i).width=size
    s.col(4).width=size+200
    s.col(6).width=size+1000
    s.col(7).width=size-500
    s.col(8).width=size-500
    s.col(9).width=size-500
    
    
    
def markForClass(termNumber,class_id):
    tt1 = time.time()
    if termNumber>2: return
    selectedClass = Class.objects.get(id=class_id)
    selected_year = selectedClass.year_id
    selected_term = Term.objects.get(year_id=selected_year, number=termNumber)

    book = Workbook(encoding = 'utf-8')
    s    = book.add_sheet('s1',True)
      
      
    markList=[]
    tkMonList=[]
    if termNumber==1:
        subjectList = Subject.objects.filter(class_id=class_id,primary__in=[0,termNumber,3,4]).order_by("index",'name')
    else:    
        subjectList = Subject.objects.filter(class_id=class_id).order_by("index",'name')
    pupilList = Pupil.objects.filter(classes=class_id,attend__is_member=True).order_by('index','first_name','last_name','birthday').distinct()
    checkNxList=[]
    for sub in subjectList:
        l = Mark.objects.filter(subject_id=sub.id,term_id__number=termNumber,current=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday')
        markList.append(l)
        if termNumber==2:
            tkMon=TKMon.objects.filter(subject_id=sub.id,current=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday')
            tkMonList.append(tkMon)
        if sub.nx:  checkNxList+=[1]
        else     :  checkNxList+=[0]  
    ddHKList = TKDiemDanh.objects.filter(student_id__classes=class_id,term_id=selected_term, student_id__attend__is_member=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday').distinct()
    tbHKList = TBHocKy.objects.filter(student_id__classes=class_id,term_id=selected_term, student_id__attend__is_member=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday').distinct()
    TBNamList = TBNam.objects.filter(year_id = selected_year, student_id__classes=class_id,student_id__attend__is_member=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday').distinct()

    ddHK1List=None
    if termNumber==2:
        term1 = Term.objects.get(year_id=selected_year, number=1)
        ddHK1List=TKDiemDanh.objects.filter(student_id__classes=class_id, term_id=term1, student_id__attend__is_member=True).order_by('student_id__index','student_id__first_name','student_id__last_name','student_id__birthday').distinct()
        
    setSizeOfMarkClass(s,len(pupilList))
    printMarkToExcel(termNumber,selectedClass,checkNxList,s,pupilList,markList,tkMonList,ddHKList,tbHKList,TBNamList,ddHK1List)

    response = HttpResponse(mimetype='application/ms-excel')
    
    name = 'phieuBaoDiem'+ unicode(selectedClass.name)+ "Ky" +unicode(termNumber)+".xls"
    name1=name.replace(' ','_')
    response['Content-Disposition'] = u'attachment; filename=%s' % name1
    book.save(response)
    tt2= time.time()
    print (tt2-tt1)
    return response

@need_login
def printMarkForClass(request,termNumber=None,class_id=-2):
    
    user = request.user

    message=None
    currentTerm=get_current_term(request)
    try:
        if in_school(request,currentTerm.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))
    teaching_class=None
    if (get_position(request)==3) & (get_level(request)=='T'):
        teaching_class = user.teacher.current_homeroom_class()
        if teaching_class==None:
            return HttpResponseRedirect('/school')
        else:
            class_id=teaching_class.id
    elif (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')

    if termNumber==None:
        if currentTerm.number==3:
            termNumber==2
        else:
            termNumber= currentTerm.number

    blockList = Block.objects.filter(school_id = currentTerm.year_id.school_id).order_by("number")
    classList =Class.objects.filter(year_id=currentTerm.year_id.id).order_by("id")

    termNumber=int(termNumber)
    class_id  = int(class_id)

    if (class_id!=-2):
        return markForClass(termNumber,class_id)
        
    
    t = loader.get_template(os.path.join('school/report','print_mark_for_class.html'))
    c = RequestContext(request, {"message":message,
                                 'classList':classList,
                                 'blockList':blockList,
                                 'termNumber':termNumber,
                                 'classChoice':class_id,
                                 'teaching_class':teaching_class,
                                }
                       )
    return HttpResponse(t.render(c))
def markExcelForAStudent(request,class_id,student_id,term_id):
    tt1 = time.time()
    user = request.user
    if not user.is_authenticated():
        return HttpResponseRedirect( reverse('login'))

    message=None
    currentTerm=get_current_term(request)
    try:
        if in_school(request,currentTerm.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))
    teaching_class=None
    if get_position(request)==1:
        if user.pupil.id !=student_id:
            return HttpResponseRedirect('/school')
    elif get_position(request)==3:
        teaching_class = user.teacher.current_homeroom_class()
        if teaching_class==None:
            return HttpResponseRedirect('/school')
        else:
            class_id=teaching_class.id
    elif (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')

    class_id  = int(class_id)
    selectedTerm=Term.objects.get(id=term_id)
    selectedClass = Class.objects.get(id=class_id)
    selected_year = selectedClass.year_id
    book = Workbook(encoding = 'utf-8')
    s    = book.add_sheet('s1',True)

    markList=[]
    tkMonList=[]

    if selectedTerm.number==1:
        subjectList = Subject.objects.filter(class_id=class_id,primary__in=[0,selectedTerm.number,3,4]).order_by("index",'name')
    else:
        subjectList = Subject.objects.filter(class_id=class_id).order_by("index",'name')
    pupilList = Pupil.objects.filter(id=student_id)
    checkNxList=[]
    for sub in subjectList:
        l = Mark.objects.filter(subject_id=sub.id,term_id=term_id,student_id=student_id)
        markList.append(l)
        if selectedTerm.number==2:
            tkMon=TKMon.objects.filter(subject_id=sub.id,student_id=student_id)
            tkMonList.append(tkMon)
        if sub.nx:  checkNxList+=[1]
        else     :  checkNxList+=[0]
    ddHKList = TKDiemDanh.objects.filter(student_id__classes=class_id,term_id=term_id,student_id=student_id,student_id__attend__is_member=True).distinct()
    tbHKList = TBHocKy.objects.filter(student_id__classes=class_id,term_id=term_id,student_id=student_id,student_id__attend__is_member=True).distinct()
    TBNamList = TBNam  .objects.filter(year_id=selected_year, student_id__classes=class_id,student_id=student_id).distinct()

    ddHK1List=None
    if selectedTerm.number==2:
        term1 = Term.objects.get(year_id=selected_year, number=1)
        ddHK1List = TKDiemDanh.objects.filter(student_id__classes=class_id,term_id=term1,student_id=student_id,student_id__attend__is_member=True).distinct()

    setSizeOfMarkClass(s,len(pupilList))
    printMarkToExcel(selectedTerm.number,selectedClass,checkNxList,s,pupilList,markList,tkMonList,ddHKList,tbHKList,TBNamList,ddHK1List)

    response = HttpResponse(mimetype='application/ms-excel')

    name=pupilList[0].last_name+pupilList[0].first_name+"hk"+str(selectedTerm.number)

    name = 'phieuBaoDiem%s.xls' % unicode(to_en1(name))
    name1=name.replace(' ','')
    response['Content-Disposition'] = u'attachment; filename=%s' % name1
    book.save(response)
    tt2= time.time()
    print (tt2-tt1)
    return response

def printDanhHieuExcel(list,termNumber,type,currentTerm):
    
    book = Workbook(encoding = 'utf-8')
    numberLine=50

    if termNumber==1:
        str1='HKI'
        str2=u'HỌC KỲ I NĂM HỌC '+str(currentTerm.year_id.time)+'-'+str(currentTerm.year_id.time+1)
    elif termNumber==2:
        str1='HKII'
        str2=u'HỌC KỲ II NĂM HỌC '+str(currentTerm.year_id.time)+'-'+str(currentTerm.year_id.time+1)
    else:
        str1='CaNam'        
        str2=u'CẢ NĂM NĂM HỌC '+str(currentTerm.year_id.time)+'-'+str(currentTerm.year_id.time+1)
        
    if   (type==1): 
        str3='dshsGioiVaTienTien'
        titleString=u'DANH SÁCH HỌC SINH GIỎI VÀ TIÊN TIẾN'
    elif (type==2):
        str3='dshsGioi'
        titleString=u'DANH SÁCH HỌC SINH GIỎI  '
    elif (type==3):
        str3='dshsTienTien'
        titleString=u'DANH SÁCH HỌC SINH TIÊN TIẾN'

    sheetName =str3+str1+str(currentTerm.year_id.time)+'-'+str(currentTerm.year_id.time+1)     
    s=book.add_sheet('DSHS ',True)
    s.col(0).width=s1    
    s.col(1).width=LASTNAME_WIDTH
    s.col(2).width=LASTNAME_WIDTH
    s.col(3).width=FIRSTNAME_WIDTH    
    s.col(4).width=BIRTHDAY_WIDTH    
    s.col(5).width=SIZE_PAGE_WIDTH1-s1-2*LASTNAME_WIDTH-FIRSTNAME_WIDTH-BIRTHDAY_WIDTH    

    printHeader(s,0,0,currentTerm.year_id.school_id,3)
    printCongHoa(s,0,3,4)
    x=7
    y=0    
    s.write_merge(x-3,x-3,0,5,titleString,h40)
    s.write_merge(x-2,x-2,0,5,str2,h40)
    s.write(x,y,u'STT',h4)
    s.write(x,y+1,u'Lớp',h4)    
    s.write_merge(x,x,y+2,y+3,u'Họ và tên',h4)    
    s.write(x,y+4,u'Ngày sinh',h4)    
    s.write(x,y+5,u'Danh hiệu',h4)  
    i=1  
    for c,danhHieus in list:
        j=1
        for dh in danhHieus:
            s.write(x+i,y,j,h82)
            s.write(x+i,y+1,c,h82)
            s.write(x+i,y+2,dh.student_id.last_name,last_name1)
            s.write(x+i,y+3,dh.student_id.first_name,first_name1)
            s.write(x+i,y+4,dh.student_id.birthday.strftime('%d/%m/%Y'),h82)
            if termNumber<3:
                s.write(x+i,y+5,convertDanhHieu(dh.danh_hieu_hk),h82)
            else:    
                s.write(x+i,y+5,convertDanhHieu(dh.danh_hieu_nam),h82)
            j+=1
            i+=1
        if danhHieus:    
            s.write(x+i,y,'',h82)
            s.write(x+i,y+1,'',h82)
            s.write(x+i,y+2,'',last_name1)
            s.write(x+i,y+3,'',first_name1)
            s.write(x+i,y+4,'',h82)
            s.write(x+i,y+5,'',h82)
            i+=1
               
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % sheetName
    book.save(response)
    return response

def printNoPassExcel(list,type,currentYear):
    
    book = Workbook(encoding = 'utf-8')
    str2=u'CẢ NĂM NĂM HỌC '+str(currentYear.time)+'-'+str(currentYear.time+1)
        
    if   (type==1): 
        str3='khongLenLop'        
        titleString=u'DANH SÁCH HỌC SINH KHÔNG LÊN LỚP  ' 
    elif (type==2): 
        str3='thiLai'        
        titleString=u'DANH SÁCH HỌC SINH THI LẠI'
    elif (type==3):       
        str3='renLuyenThem'        
        titleString=u'DANH SÁCH HỌC SINH RÈN LUYỆN THÊM TRONG HÈ' 
         
    sheetName =str3+str(currentYear.time)+'-'+str(currentYear.time+1)     
    s=book.add_sheet('DSHS ',True)
    s.col(0).width=s1    
    s.col(1).width=LASTNAME_WIDTH
    s.col(2).width=LASTNAME_WIDTH
    s.col(3).width=FIRSTNAME_WIDTH    
    s.col(4).width=BIRTHDAY_WIDTH    
    s.col(5).width=SIZE_PAGE_WIDTH1-s1-2*LASTNAME_WIDTH-FIRSTNAME_WIDTH-BIRTHDAY_WIDTH    

    printHeader(s,0,0,currentYear.school_id,3)
    printCongHoa(s,0,3,4)
    x=7
    y=0    
    s.write_merge(x-3,x-3,0,5,titleString,h40)
    s.write_merge(x-2,x-2,0,5,str2,h40)
    s.write(x,y,u'STT',h4)
    s.write(x,y+1,u'Lớp',h4)    
    s.write_merge(x,x,y+2,y+3,u'Họ và tên',h4)    
    s.write(x,y+4,u'Ngày sinh',h4)    
    s.write(x,y+5,u'Thuộc diện',h4)  
    i=1  
    for c,tbNams in list:
        j=1
        for tbNam in tbNams:
            s.write(x+i,y,i,h82)
            s.write(x+i,y+1,c,h82)
            s.write(x+i,y+2,tbNam.student_id.last_name,last_name1)
            s.write(x+i,y+3,tbNam.student_id.first_name,first_name1)
            s.write(x+i,y+4,tbNam.student_id.birthday.strftime('%d/%m/%Y'),h82)
                
            if  tbNam.len_lop:
                if tbNam.thi_lai:                        
                    s.write(x+i,y+5,'lên lớp(sau khi kt lại)',h82)
                elif tbNam.ren_luyen_lai:    
                    s.write(x+i,y+5,'lên lớp(sau rèn luyện thêm trong hè)',h82)
                else:    
                    s.write(x+i,y+5,'lên lớp',h82)
            elif  tbNam.len_lop==False:
                if tbNam.thi_lai:                        
                    s.write(x+i,y+5,'Ở lại lớp(sau khi kt lại)',h82)
                elif tbNam.ren_luyen_lai:    
                    s.write(x+i,y+5,'Ở lại lớp(sau rèn luyện thêm trong hè)',h82)
                else:    
                    s.write(x+i,y+5,'Ở lại lớp',h82)
            elif tbNam.thi_lai:        
                s.write(x+i,y+5,'thi lại',h82)
            elif tbNam.ren_luyen_lai:
                s.write(x+i,y+5,'rèn luyện thêm trong hè',h82)    
            j+=1
            i+=1
               
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % sheetName
    book.save(response)
    return response

@need_login
def excelClassList(request,class_id=-2):
    user = request.user

    message = None
    currentTerm = get_current_term(request)
    try:
        if in_school(request,currentTerm.year_id.school_id) == False:
            return HttpResponseRedirect('/school')
    except Exception as e:
        return HttpResponseRedirect(reverse('index'))
    teaching_class=None
    if (get_position(request)==3)  & (get_level(request)=='T' ):
        teaching_class = user.teacher.current_homeroom_class()
        if teaching_class==None:
            return HttpResponseRedirect('/school')
        else:
            class_id=teaching_class.id
    elif (get_position(request) != 4) & (get_level(request)=='T' ):
       return HttpResponseRedirect('/school')

    class_id  = int(class_id)
    classList =Class.objects.filter(year_id=currentTerm.year_id).order_by("id")
    blockList = Block.objects.filter(school_id = currentTerm.year_id.school_id).order_by("number")

    if class_id!=-2 :
        return class_generate(request,class_id,'student_list')

    t = loader.get_template(os.path.join('school/report','excel_class_list.html'))
    c = RequestContext(request, {"message":message,
                                 'classList':classList,
                                 'blockList':blockList,
                                 'classChoice':class_id,
                                 'teaching_class':teaching_class,
                                }
                       )
    return HttpResponse(t.render(c))

def practisingByGradeExcel(list,yearNumber,termNumber,so):
    book = Workbook(encoding = 'utf-8')
    
    firstTitle  = u'TỔNG HỢP ĐÁNH GIÁ HẠNH KIỂM HỌC SINH'
    nextYear = int(yearNumber)+1
    if int(termNumber)==1:
        secondTitle = u'HỌC KỲ I NĂM HỌC '+str(yearNumber)+"-"+unicode(nextYear)
    elif int(termNumber)==2:
        secondTitle = u'HỌC KỲ II NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)
    else:
        secondTitle = u'CẢ NĂM NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)

    s=book.add_sheet('DSHS ',True)
    """
    s.col(0).width=s1
    s.col(1).width=LASTNAME_WIDTH
    s.col(2).width=LASTNAME_WIDTH
    s.col(3).width=FIRSTNAME_WIDTH
    s.col(4).width=BIRTHDAY_WIDTH
    s.col(5).width=SIZE_PAGE_WIDTH1-s1-2*LASTNAME_WIDTH-FIRSTNAME_WIDTH-BIRTHDAY_WIDTH
    """
    printCongHoa(s,0,3,7)
    x=7
    y=0
    s.write_merge(x-3,x-3,0,9,firstTitle,h40)
    s.write_merge(x-2,x-2,0,9,secondTitle,h40)
    
    s.write_merge(x,x+1,y,y,u'Khối',h4)
    s.write_merge(x,x+1,y+1,y+1,u'TS',h4)
    s.write_merge(x,x,y+2,y+3,u'Tốt',h4)
    s.write_merge(x,x,y+4,y+5,u'Khá',h4)
    s.write_merge(x,x,y+6,y+7,u'Trung bình',h4)
    s.write_merge(x,x,y+8,y+9,u'Yếu',h4)
    for i in range(4):
        s.write(x+1,y+2+2*i,'sl',h4)
        s.write(x+1,y+2+2*i+1,'%',h4)

    i=0
    for subList in list:
       i+=1
       if i>5:
           s.write(x+i-4,y,i,h5)
           j=0
           for sl in subList:
               j+=1
               s.write(x+i-4,y+j,sl,h5)
    if int(termNumber) <3 :
        term ='Ky'+str(termNumber)
    else:
        term = 'CaNam'
    name=u'SGD_ThongKeHanhKiemTheoKhoi'+unicode(yearNumber)+term
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' %  name
    book.save(response)
    return response

def practisingByMajorExcel(list,yearNumber,termNumber,so):
    book = Workbook(encoding = 'utf-8')

    firstTitle  = u'TỔNG HỢP ĐÁNH GIÁ HẠNH KIỂM HỌC SINH THEO BAN'
    nextYear = int(yearNumber)+1
    if int(termNumber)==1:
        secondTitle = u'HỌC KỲ I NĂM HỌC '+str(yearNumber)+"-"+unicode(nextYear)
    elif int(termNumber)==2:
        secondTitle = u'HỌC KỲ II NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)
    else:
        secondTitle = u'CẢ NĂM NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)

    s=book.add_sheet('DSHS ',True)
    width = (A4_WIDTH - LASTNAME_WIDTH) / 10
    for i in range(11):
        s.col(i).width = width
    s.col(1).width=LASTNAME_WIDTH

    printCongHoa(s,0,3,7)
    x=7
    y=0
    s.write_merge(x-3,x-3,0,9,firstTitle,h40)
    s.write_merge(x-2,x-2,0,9,secondTitle,h40)

    s.write_merge(x,x+1,y,y,u'Khối',h4)
    s.write_merge(x,x+1,y+1,y+1,u'Ban',h4)
    s.write_merge(x,x+1,y+2,y+2,u'TS',h4)
    s.write_merge(x,x,y+3,y+4,u'Tốt',h4)
    s.write_merge(x,x,y+5,y+6,u'Khá',h4)
    s.write_merge(x,x,y+7,y+8,u'Trung bình',h4)
    s.write_merge(x,x,y+9,y+10,u'Yếu',h4)
    for i in range(4):
        s.write(x+1,y+3+2*i,'sl',h4)
        s.write(x+1,y+3+2*i+1,'%',h4)

    i=0
    for b in range(10,13):
        s.write_merge(x+(b-10)*7+2,x+(b-9)*7+1,0,0,b,h5)
        for (k,ban) in enumerate(BAN_CHOICE):
            i+=1
            s.write(x+i+1,y+1,ban[1],h7)
            for j in range(9):
                s.write(x+i+1,y+j+2,list[b-1][k][j],h5)

    if int(termNumber) <3 :
        term ='Ky'+str(termNumber)
    else:
        term = 'CaNam'
    name=u'SGD_ThongKeHanhKiemTheoBan'+unicode(yearNumber)+term

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % name
    book.save(response)
    return response

def learningByGradeExcel(list,yearNumber,termNumber,so):
    book = Workbook(encoding = 'utf-8')

    firstTitle  = u'TỔNG HỢP ĐÁNH GIÁ HỌC LỰC HỌC SINH THEO KHỐI'
    nextYear = int(yearNumber)+1
    if int(termNumber)==1:
        secondTitle = u'HỌC KỲ I NĂM HỌC '+str(yearNumber)+"-"+unicode(nextYear)
    elif int(termNumber)==2:
        secondTitle = u'HỌC KỲ II NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)
    else:
        secondTitle = u'CẢ NĂM NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)

    s=book.add_sheet('DSHS ',True)
    width = A4_WIDTH / 12.0
    for i in range(12):
        s.col(i).width = width

    printCongHoa(s,0,3,7)
    x=7
    y=0
    s.write_merge(x-3,x-3,0,9,firstTitle,h40)
    s.write_merge(x-2,x-2,0,9,secondTitle,h40)

    s.write_merge(x,x+1,y,y,u'Khối',h4)
    s.write_merge(x,x+1,y+1,y+1,u'TS',h4)
    s.write_merge(x,x,y+2,y+3,u'Giỏi',h4)
    s.write_merge(x,x,y+4,y+5,u'Khá',h4)
    s.write_merge(x,x,y+6,y+7,u'Trung bình',h4)
    s.write_merge(x,x,y+8,y+9,u'Yếu',h4)
    s.write_merge(x,x,y+10,y+11,u'Kém',h4)
    for i in range(5):
        s.write(x+1,y+2+2*i,'sl',h4)
        s.write(x+1,y+2+2*i+1,'%',h4)

    i=0
    for subList in list:
        i+=1
        if i>5:
            s.write(x+i-4,y,i,h5)
            j=0
            for sl in subList:
                j+=1
                s.write(x+i-4,y+j,sl,h5)

    if int(termNumber) <3 :
        term ='Ky'+str(termNumber)
    else:
        term = 'CaNam'
    name=u'SGD_ThongKeHocLucTheoKhoi'+unicode(yearNumber)+term

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % name
    book.save(response)
    return response

def learningByMajorExcel(list,yearNumber,termNumber,so):
    book = Workbook(encoding = 'utf-8')

    firstTitle  = u'TỔNG HỢP ĐÁNH GIÁ HỌC LỰC HỌC SINH THEO BAN'
    nextYear = int(yearNumber)+1
    if int(termNumber)==1:
        secondTitle = u'HỌC KỲ I NĂM HỌC '+str(yearNumber)+"-"+unicode(nextYear)
    elif int(termNumber)==2:
        secondTitle = u'HỌC KỲ II NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)
    else:
        secondTitle = u'CẢ NĂM NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)

    s=book.add_sheet('DSHS ',True)
    width = (A4_WIDTH - LASTNAME_WIDTH) / 10
    for i in range(11):
        s.col(i).width = width
    s.col(1).width=LASTNAME_WIDTH

    printCongHoa(s,0,3,7)
    x=7
    y=0
    s.write_merge(x-3,x-3,0,9,firstTitle,h40)
    s.write_merge(x-2,x-2,0,9,secondTitle,h40)

    s.write_merge(x,x+1,y,y,u'Khối',h4)
    s.write_merge(x,x+1,y+1,y+1,u'Ban',h4)
    s.write_merge(x,x+1,y+2,y+2,u'TS',h4)
    s.write_merge(x,x,y+3,y+4,u'Tốt',h4)
    s.write_merge(x,x,y+5,y+6,u'Khá',h4)
    s.write_merge(x,x,y+7,y+8,u'Trung bình',h4)
    s.write_merge(x,x,y+9,y+10,u'Yếu',h4)
    for i in range(4):
        s.write(x+1,y+3+2*i,'sl',h4)
        s.write(x+1,y+3+2*i+1,'%',h4)

    i=0
    for b in range(10,13):
        s.write_merge(x+(b-10)*7+2,x+(b-9)*7+1,0,0,b,h5)
        for (k,ban) in enumerate(BAN_CHOICE):
            i+=1
            s.write(x+i+1,y+1,ban[1],h7)
            for j in range(9):
                s.write(x+i+1,y+j+2,list[b-1][k][j],h5)

    if int(termNumber) <3 :
        term ='Ky'+str(termNumber)
    else:
        term = 'CaNam'
    name=u'SGD_ThongKeHocLucTheoBan'+unicode(yearNumber)+term

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % name
    book.save(response)
    return response

def titleByGradeExcel(list,yearNumber,termNumber,so):
    book = Workbook(encoding = 'utf-8')

    firstTitle  = u'TỔNG HỢP DANH HIỆU HỌC SINH THEO KHỐI'
    nextYear = int(yearNumber)+1
    if int(termNumber)==1:
        secondTitle = u'HỌC KỲ I NĂM HỌC '+str(yearNumber)+"-"+unicode(nextYear)
    elif int(termNumber)==2:
        secondTitle = u'HỌC KỲ II NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)
    else:
        secondTitle = u'CẢ NĂM NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)

    s=book.add_sheet('DSHS ',True)
    width = A4_WIDTH / 6
    for i in range(6):
        s.col(i).width = width

    printCongHoa(s,0,2,4)
    x=7
    y=0
    s.write_merge(x-3,x-3,0,5,firstTitle,h40)
    s.write_merge(x-2,x-2,0,5,secondTitle,h40)

    s.write_merge(x,x+1,y,y,u'Khối',h4)
    s.write_merge(x,x+1,y+1,y+1,u'TS',h4)
    s.write_merge(x,x,y+2,y+3,u'Học sinh giỏi',h4)
    s.write_merge(x,x,y+4,y+5,u'Học sinh tiên tiến',h4)
    for i in range(2):
        s.write(x+1,y+2+2*i,'sl',h4)
        s.write(x+1,y+2+2*i+1,'%',h4)

    i=0
    for subList in list:
        i+=1
        if i>5:
            s.write(x+i-4,y,i,h5)
            j=0
            for sl in subList:
                j+=1
                s.write(x+i-4,y+j,sl,h5)
                print subList

    if int(termNumber) <3 :
        term ='Ky'+str(termNumber)
    else:
        term = 'CaNam'
    name=u'SGD_ThongKeDanhHieuTheoKhoi'+unicode(yearNumber)+term

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % name
    book.save(response)
    return response

def titleByMajorExcel(list,yearNumber,termNumber,so):
    book = Workbook(encoding = 'utf-8')

    firstTitle  = u'TỔNG HỢP DANH HIỆU HỌC SINH THEO BAN'
    nextYear = int(yearNumber)+1
    if int(termNumber)==1:
        secondTitle = u'HỌC KỲ I NĂM HỌC '+str(yearNumber)+"-"+unicode(nextYear)
    elif int(termNumber)==2:
        secondTitle = u'HỌC KỲ II NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)
    else:
        secondTitle = u'CẢ NĂM NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)

    s=book.add_sheet('DSHS ',True)
    width = (A4_WIDTH - LASTNAME_WIDTH) / 6
    for i in range(11):
        s.col(i).width = width
    s.col(1).width=LASTNAME_WIDTH

    printCongHoa(s,0,3,4)
    x=7
    y=0
    s.write_merge(x-3,x-3,0,6,firstTitle,h40)
    s.write_merge(x-2,x-2,0,6,secondTitle,h40)

    s.write_merge(x,x+1,y,y,u'Khối',h4)
    s.write_merge(x,x+1,y+1,y+1,u'Ban',h4)
    s.write_merge(x,x+1,y+2,y+2,u'TS',h4)
    s.write_merge(x,x,y+3,y+4,u'Học sinh giỏi',h4)
    s.write_merge(x,x,y+5,y+6,u'Học sinh tiên tiến',h4)
    for i in range(2):
        s.write(x+1,y+3+2*i,'sl',h4)
        s.write(x+1,y+3+2*i+1,'%',h4)

    i=0
    for b in range(10,13):
        s.write_merge(x+(b-10)*7+2,x+(b-9)*7+1,0,0,b,h5)
        for (k,ban) in enumerate(BAN_CHOICE):
            i+=1
            s.write(x+i+1,y+1,ban[1],h7)
            for j in range(5):
                s.write(x+i+1,y+j+2,list[b-1][k][j],h5)

    if int(termNumber) <3 :
        term ='Ky'+str(termNumber)
    else:
        term = 'CaNam'
    name=u'SGD_ThongKeDanhHieuTheoBan'+unicode(yearNumber)+term

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % name
    book.save(response)
    return response

def practisingByDistrictExcel(list,yearNumber,termNumber,so):
    book = Workbook(encoding = 'utf-8')

    firstTitle  = u'TỔNG HỢP ĐÁNH GIÁ HẠNH KIỂM HỌC SINH THEO QUẬN HUYỆN'
    nextYear = int(yearNumber)+1
    if int(termNumber)==1:
        secondTitle = u'HỌC KỲ I NĂM HỌC '+str(yearNumber)+"-"+unicode(nextYear)
    elif int(termNumber)==2:
        secondTitle = u'HỌC KỲ II NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)
    else:
        secondTitle = u'CẢ NĂM NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)

    s=book.add_sheet('DSHS ',True)
    s.set_portrait(0)
    width = (SIZE_PAGE_WIDTH - 3*LASTNAME_WIDTH) / 10
    for i in range(11):
        s.col(i).width = width
    s.col(0).width=LASTNAME_WIDTH
    s.col(1).width=2*LASTNAME_WIDTH

    printCongHoa(s,0,3,7)
    x=7
    y=0
    s.write_merge(x-3,x-3,0,9,firstTitle,h40)
    s.write_merge(x-2,x-2,0,9,secondTitle,h40)

    s.write_merge(x,x+1,y,y,u'Huyện',h4)
    s.write_merge(x,x+1,y+1,y+1,u'Trường',h4)
    s.write_merge(x,x+1,y+2,y+2,u'TS',h4)
    s.write_merge(x,x,y+3,y+4,u'Tốt',h4)
    s.write_merge(x,x,y+5,y+6,u'Khá',h4)
    s.write_merge(x,x,y+7,y+8,u'Trung bình',h4)
    s.write_merge(x,x,y+9,y+10,u'Yếu',h4)
    for i in range(4):
        s.write(x+1,y+3+2*i,'sl',h4)
        s.write(x+1,y+3+2*i+1,'%',h4)
    i=0
    for aList in list:
        for school,subList in aList:
            if school=='1':
                s.write(x+i+2,y,u'Tổng',h92)
                s.write(x+i+2,y+1,'',h5)
            else:
                s.write(x+i+2,y,school.district,h74)
                s.write(x+i+2,y+1,school.name,h74)

            for (t,l) in enumerate(subList):
                s.write(x+i+2,y+t+2,l,h5)

            i+=1
            if school=='1':
                i+=1


    if int(termNumber) <3 :
        term ='Ky'+str(termNumber)
    else:
        term = 'CaNam'
    name=u'SGD_ThongKeHanhKiemTheoQuanHuyen'+unicode(yearNumber)+term

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % name
    book.save(response)
    return response

def learningByDistrictExcel(list,yearNumber,termNumber,so):
    book = Workbook(encoding = 'utf-8')

    firstTitle  = u'TỔNG HỢP ĐÁNH GIÁ HỌC LỰC HỌC SINH THEO QUẬN HUYỆN'
    nextYear = int(yearNumber)+1
    if int(termNumber)==1:
        secondTitle = u'HỌC KỲ I NĂM HỌC '+str(yearNumber)+"-"+unicode(nextYear)
    elif int(termNumber)==2:
        secondTitle = u'HỌC KỲ II NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)
    else:
        secondTitle = u'CẢ NĂM NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)

    s=book.add_sheet('DSHS ',True)
    s.set_portrait(0)
    width = (SIZE_PAGE_WIDTH - 3*LASTNAME_WIDTH) / 10
    for i in range(11):
        s.col(i).width = width
    s.col(0).width=LASTNAME_WIDTH
    s.col(1).width=2*LASTNAME_WIDTH

    printCongHoa(s,0,3,7)
    x=7
    y=0
    s.write_merge(x-3,x-3,0,9,firstTitle,h40)
    s.write_merge(x-2,x-2,0,9,secondTitle,h40)

    s.write_merge(x,x+1,y,y,u'Huyện',h4)
    s.write_merge(x,x+1,y+1,y+1,u'Trường',h4)
    s.write_merge(x,x+1,y+2,y+2,u'TS',h4)
    s.write_merge(x,x,y+3,y+4,u'Giỏi',h4)
    s.write_merge(x,x,y+5,y+6,u'Khá',h4)
    s.write_merge(x,x,y+7,y+8,u'Trung bình',h4)
    s.write_merge(x,x,y+9,y+10,u'Yếu',h4)
    s.write_merge(x,x,y+9,y+12,u'Kém',h4)
    for i in range(5):
        s.write(x+1,y+3+2*i,'sl',h4)
        s.write(x+1,y+3+2*i+1,'%',h4)
    i=0
    for aList in list:
        for school,subList in aList:
            if school=='1':
                s.write(x+i+2,y,u'Tổng',h92)
                s.write(x+i+2,y+1,'',h5)
            else:
                s.write(x+i+2,y,school.district,h74)
                s.write(x+i+2,y+1,school.name,h74)

            for (t,l) in enumerate(subList):
                s.write(x+i+2,y+t+2,l,h5)

            i+=1
            if school=='1':
                i+=1


    if int(termNumber) <3 :
        term ='Ky'+str(termNumber)
    else:
        term = 'CaNam'
    name=u'SGD_ThongKeHocLucTheoQuanHuyen'+unicode(yearNumber)+term

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % name
    book.save(response)
    return response

def titleByDistrictExcel(list,yearNumber,termNumber,so):
    book = Workbook(encoding = 'utf-8')

    firstTitle  = u'TỔNG HỢP ĐÁNH GIÁ DANH HIỆU HỌC SINH THEO QUẬN HUYỆN'
    nextYear = int(yearNumber)+1
    if int(termNumber)==1:
        secondTitle = u'HỌC KỲ I NĂM HỌC '+str(yearNumber)+"-"+unicode(nextYear)
    elif int(termNumber)==2:
        secondTitle = u'HỌC KỲ II NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)
    else:
        secondTitle = u'CẢ NĂM NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)

    s=book.add_sheet('DSHS ',True)
    width = (A4_WIDTH - 2.5*LASTNAME_WIDTH) / 5
    for i in range(11):
        s.col(i).width = width
    s.col(0).width=LASTNAME_WIDTH
    s.col(1).width=1.5*LASTNAME_WIDTH

    printCongHoa(s,0,1,6)
    x=7
    y=0
    s.write_merge(x-3,x-3,0,6,firstTitle,h40)
    s.write_merge(x-2,x-2,0,6,secondTitle,h40)

    s.write_merge(x,x+1,y,y,u'Huyện',h4)
    s.write_merge(x,x+1,y+1,y+1,u'Trường',h4)
    s.write_merge(x,x+1,y+2,y+2,u'TS',h4)
    s.write_merge(x,x,y+3,y+4,u'Học sinh giỏi',h4)
    s.write_merge(x,x,y+5,y+6,u'Học sinh tiên tiến',h4)
    for i in range(2):
        s.write(x+1,y+3+2*i,'sl',h4)
        s.write(x+1,y+3+2*i+1,'%',h4)
    i=0
    for aList in list:
        for school,subList in aList:
            if school=='1':
                s.write(x+i+2,y,u'Tổng',h92)
                s.write(x+i+2,y+1,'',h5)
            else:
                s.write(x+i+2,y,school.district,h74)
                s.write(x+i+2,y+1,school.name,h74)

            for (t,l) in enumerate(subList):
                s.write(x+i+2,y+t+2,l,h5)

            i+=1
            if school=='1':
                i+=1


    if int(termNumber) <3 :
        term ='Ky'+str(termNumber)
    else:
        term = 'CaNam'
    name=u'SGD_ThongKeDanhHieuTheoQuanHuyen'+unicode(yearNumber)+term

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % name
    book.save(response)
    return response

def countFinalMarkExcel(type,yearNumber,termNumber,subjectIndex,blockIndex,list,headerTable,sumList):
    book = Workbook(encoding = 'utf-8')

    firstTitle  = u'TỔNG HỢP ĐÁNH GIÁ DANH HIỆU HỌC SINH THEO QUẬN HUYỆN'
    nextYear = int(yearNumber)+1
    if int(termNumber)==1:
        secondTitle = u'HỌC KỲ I NĂM HỌC '+str(yearNumber)+"-"+unicode(nextYear)
    elif int(termNumber)==2:
        secondTitle = u'HỌC KỲ II NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)
    else:
        secondTitle = u'CẢ NĂM NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)

    s=book.add_sheet('DSHS ',True)
    width = (A4_WIDTH - 2.5*LASTNAME_WIDTH) / 5
    for i in range(11):
        s.col(i).width = width
    s.col(0).width=LASTNAME_WIDTH
    s.col(1).width=1.5*LASTNAME_WIDTH

    printCongHoa(s,0,1,6)
    x=7
    y=0
    s.write_merge(x-3,x-3,0,6,firstTitle,h40)
    s.write_merge(x-2,x-2,0,6,secondTitle,h40)

    s.write_merge(x,x+1,y,y,u'Huyện',h4)
    s.write_merge(x,x+1,y+1,y+1,u'Trường',h4)
    s.write_merge(x,x+1,y+2,y+2,u'TS',h4)
    s.write_merge(x,x,y+3,y+4,u'Học sinh giỏi',h4)
    s.write_merge(x,x,y+5,y+6,u'Học sinh tiên tiến',h4)
    for i in range(2):
        s.write(x+1,y+3+2*i,'sl',h4)
        s.write(x+1,y+3+2*i+1,'%',h4)
    i=0
    for aList in list:
        for school,subList in aList:
            if school=='1':
                s.write(x+i+2,y,u'Tổng',h92)
                s.write(x+i+2,y+1,'',h5)
            else:
                s.write(x+i+2,y,school.district,h74)
                s.write(x+i+2,y+1,school.name,h74)

            for (t,l) in enumerate(subList):
                s.write(x+i+2,y+t+2,l,h5)

            i+=1
            if school=='1':
                i+=1


    if int(termNumber) <3 :
        term ='Ky'+str(termNumber)
    else:
        term = 'CaNam'
    name=u'SGD_ThongKeDanhHieuTheoQuanHuyen'+unicode(yearNumber)+term

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % name
    book.save(response)
    return response
def countFinalMarkExcel(type,yearNumber,termNumber,subjectIndex,blockIndex,subjectList,list,headerTable,sumList,sumsum):

    book = Workbook(encoding = 'utf-8')
    if type=='0':
        firstTitle = u'THỐNG KÊ ĐIỂM THI HỌC KỲ MÔN '+subjectList[int(subjectIndex)].upper() +u' KHỐI '+ blockIndex
    else:
        firstTitle = u'THỐNG KÊ ĐIỂM TRUNG BÌNH HỌC KỲ MÔN '+subjectList[int(subjectIndex)].upper() +u' KHỐI '+ blockIndex
    nextYear = int(yearNumber)+1

    if int(termNumber)==1:
        secondTitle = u'HỌC KỲ I NĂM HỌC '+str(yearNumber)+"-"+unicode(nextYear)
    elif int(termNumber)==2:
        secondTitle = u'HỌC KỲ II NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)
    else:
        secondTitle = u'CẢ NĂM NĂM HỌC '+unicode(yearNumber)+"-"+unicode(nextYear)

    s=book.add_sheet('DSHS ',True)
    if (len(headerTable)==2):
        width = (A4_WIDTH - 2*LASTNAME_WIDTH - STT_WIDTH) / (2*len(headerTable)+1)
        printCongHoa(s,0,2,5)
    else:
        s.set_portrait(0)
        width = (A3_WIDTH - 2*LASTNAME_WIDTH - STT_WIDTH) / (2*len(headerTable)+1)
        printCongHoa(s,0,3,9)
    s.col(0).width=STT_WIDTH
    s.col(1).width=2*LASTNAME_WIDTH
    for i in range(2,2+2*len(headerTable)):
        s.col(i).width = width
    x=7
    y=0
    s.write_merge(x-3,x-3,0,2+2*len(headerTable),firstTitle,h40)
    s.write_merge(x-2,x-2,0,2+2*len(headerTable),secondTitle,h40)

    s.write_merge(x,x+1,y,y,u'STT',h4)
    s.write_merge(x,x+1,y+1,y+1,u'Trường',h4)
    s.write_merge(x,x+1,y+2,y+2,u'TS',h4)
    for (i,h) in enumerate(headerTable):
        s.write_merge(x,x,y+2*i+3,2*i+4,h,h4)
    for (i,h) in enumerate(headerTable):
        s.write(x+1,y+2*i+3,'sl',h4)
        s.write(x+1,y+2*i+4,'%',h4)
    i=1
    for school,sum,aList in list:
        s.write(x+i+1,y,i,h5)
        s.write(x+i+1,y+1,school,h5)
        s.write(x+i+1,y+2,sum,h5)
        for (j,(sl,pt)) in enumerate(aList):
            s.write(x+i+1,y+2*j+3,sl,h5)
            s.write(x+i+1,y+2*j+4,pt,h5)
        i+=1
    s.write_merge(x+i+1,x+i+1,y,y+1,u'Tổng',h4)
    s.write(x+i+1,y+2,sumsum,h4)
    for (j,(sl,pt)) in enumerate(aList):
        s.write(x+i+1,y+2*j+3,sl,h4)
        s.write(x+i+1,y+2*j+4,pt,h4)
    if int(termNumber) <3 :
        term ='Ky'+str(termNumber)
    else:
        term = 'CaNam'
    name=u'SGD_ThongKeDiemTrungBinh'+unicode(yearNumber)+term

    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = u'attachment; filename=%s.xls' % name
    book.save(response)
    return response
