# -*- coding: utf-8 -*-

from xlwt import easyxf

noneSubject = "............................."
MAX_COL = 8
MAX_VIEW = 4
from datetime import datetime

CHECKED_DATE = datetime(2010, 1, 1, 0, 0, 0)

e = 0.00000001
s1 = 1000
s2 = 5000
s3 = 2000
s4 = 3000
m1 = 3000
m2 = 4000
m3 = 4000
m4 = 1400
m5 = 1400

m6 = 3000
m7 = 3000
m8 = 3500
m9 = 1000
m10 = 1400
d1 = 1400
d2 = 2000 # kick thuoc cot o trang 31
d3 = 6000
d4 = 1200 # kich thuoc 1 o diem
STT_WIDTH = 1000
FIRSTNAME_WIDTH = 2000
LASTNAME_WIDTH = 5000
BIRTHDAY_WIDTH = 3000
PLACE_WIDTH = 4000
SEX_WIDTH = 1500
DAN_TOC_WIDTH = 2500
UU_TIEN_WIDTH = 5800

SIZE_PAGE_WIDTH = 36200
SIZE_PAGE_WIDTH1 = 22000
A4_WIDTH = 24500
A3_WIDTH = 36200

h1 = easyxf(
    'font:name Arial, bold on,height 1000 ;align: vert centre, horz center')
h2 = easyxf(
    'font:name Times New Roman, bold on,height 1000 ;align: vert centre, horz center')
h3 = easyxf(
    'font:name Times New Roman, bold on,height 400 ;align: vert centre, horz center')
h4 = easyxf(
    'font    :name Times New Roman, bold on,height 260 ;align:wrap on, vert centre, horz center;'
    'borders : top thin ,right thin, left thin, bottom thin')
h41 = easyxf(
    'font    :name Times New Roman, bold on,height 260 ;align:wrap on, horz left;'
    'borders : top thin ,right thin, left thin, bottom thin')
h40 = easyxf(
    'font    :name Times New Roman, bold on,height 260 ;align:wrap on, vert centre, horz center;')

h5 = easyxf(
    'font:name Times New Roman ,height 240 ;align:wrap on, vert centre, horz center;'
    'borders: top thin,right thin,left thin,bottom thin')
h6 = easyxf(
    'font:name Times New Roman ,height 240 ;align:wrap on;'
    'borders: right thin,left thin,bottom dotted')
h61 = easyxf(
    'font:name Times New Roman ,height 240 ;align:horz right;'
    'borders: right thin,left thin,bottom dotted')
h7 = easyxf(
    'font:name Times New Roman ,height 240 ;align:wrap on;'
    'borders: right thin,left thin,bottom thin')
h71 = easyxf(
    'font:name Times New Roman ,height 240 ;align:horz right;'
    'borders: right thin,left thin,bottom thin')

h72 = easyxf(
    'font:name Times New Roman ,height 220 ;align:horz right;'
    'borders: right thin,left thin,bottom thin,top thin',
)
h73 = easyxf(
    'font:name Times New Roman ,height 220 ;align:horz right;'
    'borders: right thin,left thin,bottom thin,top thin',
    num_format_str='0.00')
h74 = easyxf(
    'font:name Times New Roman ,height 240 ;align:wrap on;'
    'borders: right thin,left thin,bottom thin, top thin')

h8 = easyxf(
    'font:name Times New Roman ,height 240 ; align:wrap on,horz left')
h81 = easyxf(
    'font:name Times New Roman ,height 240 ; align:wrap on,horz left;'# trang 31
    'borders: right thin,left thin')

h82 = easyxf(
    'font:name Times New Roman ,height 240 ; align:wrap on,horz left;'# trang 31
    'borders: right thin,left thin,bottom thin,top thin')

h8center = easyxf(
    'font:name Times New Roman ,height 240 ; align:wrap on,horz center')

h9 = easyxf(
    'font:name Times New Roman,bold on ,height 240 ;align:horz centre')# xac nhan
h91 = easyxf(
    'font:name Times New Roman,bold on ,height 240 ;align:horz centre;'
    'borders: right thin,left thin')
h92 = easyxf(
    'font:name Times New Roman,bold on ,height 240 ;align:horz centre;'
    'borders: right thin,left thin,bottom thin,top thin')

h10 = easyxf(
    'font:name Times New Roman,bold on ,height 200 ;align:wrap on,horz centre,vert centre ;'
    'borders: top thin,right thin,left thin,bottom thin')

hh1 = easyxf(
    'font:name Times New Roman,italic on ,height 240 ;align:horz centre;'
    'borders: right thin,left thin')
hh2 = easyxf(
    'font:name Times New Roman,italic on ,height 240 ;align:horz centre;')

first_name = easyxf(
    'font:name Times New Roman ,height 240 ;'
    'borders: right thin,left no_line,bottom dotted')
last_name = easyxf(
    'font:name Times New Roman ,height 240 ;'
    'borders: right no_line,left thin,bottom dotted')

first_name1 = easyxf(
    'font:name Times New Roman ,height 240 ;'
    'borders: right thin,left no_line,bottom thin')
last_name1 = easyxf(
    'font:name Times New Roman ,height 240 ;'
    'borders: right no_line,left thin,bottom thin')

f1 = easyxf(
    'font:name Times New Roman, bold on,height 500 ;align: vert centre, horz center')
f2 = easyxf(
    'font:name Times New Roman, bold on,height 300 ;align: vert centre, horz center')
f3 = easyxf(
    'font:name Times New Roman, bold on,height 280 ;align: vert centre, horz left')
f4 = easyxf(
    'font:name Times New Roman, bold on,height 280 ;align: vert centre, horz center')
f5 = easyxf(
    'font    :name Times New Roman, bold on,height 260 ;align:wrap on, vert centre, horz center;'
    'borders :top thin,right thin, left thin')

f6 = easyxf(
    'font    :name Times New Roman, italic on,height 220 ;align:wrap on, vert centre, horz center;'
    'borders : right thin, left thin,bottom thin')

f7 = easyxf(
    'font    :name Times New Roman, italic on,bold on,height 260 ;align:wrap on, vert centre, horz left;')
f71 = easyxf(
    'font    :name Times New Roman, italic on,bold on,height 260 ;align:wrap on, vert centre, horz right;')

f8 = easyxf(
    'font:name Times New Roman ,height 240 ,bold on;align: vert centre, horz center;'
    'borders: right no_line,left thin,bottom thin,top thin')

f81 = easyxf(
    'font:name Times New Roman ,height 240 ;'
    'borders: right thin,left no_line,bottom no_line,top thin')

f82 = easyxf(
    'font:name Times New Roman ,height 240 ;'
    'borders: right thin,left no_line,bottom thin,top no_line')

htb = easyxf(
    'font:name Times New Roman ,height 240 ;align:horz left;'
    'borders: right thin,left thin,bottom thin')
htbdot = easyxf(
    'font:name Times New Roman ,height 240 ;align:horz left;'
    'borders: right thin,left thin,bottom dotted')

n4 = easyxf(
    'font    :name Times New Roman, bold on,height 260 ;align:wrap on, vert centre, horz center;'
    'borders : top thin ,right thin, left thin, bottom thin')
n4.num_format_str = "0.00"

def printHeader(s, x, y, school, width=4, heigh=3):
    name = school.name.strip()
    if name.lower().find(u'trường') < 0:
        name = u'Trường ' + name
        #print name
    s.write_merge(x, x + heigh - 1, y, y + width - 1, name, h40)


def printCongHoa(s, x, y, width=3, heigh=4):
    name = u'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM \n Độc lập-Tự do- Hạnh phúc \n-----------------'
    s.write_merge(x, x + heigh - 1, y, y + width - 1, name, h40)


def normalize(x, checkNx=0, isCut=True):
    if (not x) | (x == ""):
        return ""
    if not checkNx:
        if isCut:
            if float(x) - int(float(x)) < e:
                return str(int(float(x)))
            else:
                return str(x)
        else:
            return str(x)
    else:
        if float(x) >= 5:
            return u'Đ'
        else:
            return  u'CĐ'


def convertMarkToCharacter1(x, is_vietnamese=True):
    if (x == None) | (x == ""):
        return ""
    elif is_vietnamese:
        if x >= 5:
            return u'Đ'
        else:
            return  u'CĐ'
    else:
        if x >= 5:
            return u'D'
        else:
            return  u'CD'


def convertMarkToCharacter(x):
    if (x == None) | (x == ""):
        return ""
    elif x >= 5:
        return u'Đạt'
    else:
        return  u'Chưa đạt'
