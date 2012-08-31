#from report.models import ReceiverReportForm, SendReportForm
#from app.models import PositionTypeForm
from django.shortcuts import render_to_response
from django.template import RequestContext

# Create your views here.
#help.html extend base.html, include 2 iframe named: QLNT_Menu.html-MenuBar & QLNT_Welcome.html-contentHelp
def help(request):
    return render_to_response("help/help.html", context_instance=RequestContext(request))
#sitemap.html extend base.html, contain an iframe called sitemapFrame.html
def sitemap(request):
    return render_to_response("help/sitemap.html", context_instance=RequestContext(request))

def menu(request):
    return render_to_response("help/menu.html", context_instance=RequestContext(request))

def welcome(request):
    return render_to_response("help/welcome.htm", context_instance=RequestContext(request))

def dangky(request):
    return render_to_response("help/dangky.html", context_instance=RequestContext(request))

def dangnhap(request):
    return render_to_response("help/dangnhap.html", context_instance=RequestContext(request))

def lienhe(request):
    return render_to_response("help/lienhe.html", context_instance=RequestContext(request))

def home(request):
    return render_to_response("help/home.html", context_instance=RequestContext(request))

def taikhoan(request):
    return render_to_response("help/taikhoan.html", context_instance=RequestContext(request))

def thietlap(request):
    return render_to_response("help/thietlap.html", context_instance=RequestContext(request))

def thoikhoabieu(request):
    return render_to_response("help/thoikhoabieu.html", context_instance=RequestContext(request))

def lop_chuyenlop(request):
    return render_to_response("help/lop-chuyenlop.html", context_instance=RequestContext(request))

def baocao(request):
    return render_to_response("help/baocao.html", context_instance=RequestContext(request))

def giaovien(request):
    return render_to_response("help/giaovien.html", context_instance=RequestContext(request))

def lop_chunhiem(request):
    return render_to_response("help/lop-chunhiem.html", context_instance=RequestContext(request))

def lop(request):
    return render_to_response("help/lop.html", context_instance=RequestContext(request))

def lop_diemdanh(request):
    return render_to_response("help/lop-diemdanh.html", context_instance=RequestContext(request))

def lop_lichhoc(request):
    return render_to_response("help/lop-lichhoc.html", context_instance=RequestContext(request))

def lop_diem(request):
    return render_to_response("help/lop-diem.html", context_instance=RequestContext(request))

def lop_hanhkiem(request):
    return render_to_response("help/lop-hanhkiem.html", context_instance=RequestContext(request))

def lop_sapxep(request):
    return render_to_response("help/lop-sapxep.html", context_instance=RequestContext(request))

def lop_tongket(request):
    return render_to_response("help/lop-tongket.html", context_instance=RequestContext(request))

def lop_monhoc(request):
    return render_to_response("help/lop-monhoc.html", context_instance=RequestContext(request))

def lop_nhantin(request):
    return render_to_response("help/lop-nhantin.html", context_instance=RequestContext(request))

def lop_xeploai(request):
    return render_to_response("help/lop-xeploai.html", context_instance=RequestContext(request))


def giaovien_home(request):
    return render_to_response("help/giaovien-home.html", context_instance=RequestContext(request))
def giaovien_lopchunhiem(request):
    return render_to_response("help/giaovien-lopchunhiem.html", context_instance=RequestContext(request))
def giaovien_diem(request):
    return render_to_response("help/giaovien-diem.html", context_instance=RequestContext(request))
def giaovien_truong(request):
    return render_to_response("help/giaovien-truong.html", context_instance=RequestContext(request))
def giaovien_caclop(request):
    return render_to_response("help/giaovien-caclop.html", context_instance=RequestContext(request))
def giaovien_giaovien(request):
    return render_to_response("help/giaovien-giaovien.html", context_instance=RequestContext(request))
def giaovien(request):
    return render_to_response("help/giaovien.html", context_instance=RequestContext(request))

#def QLNT_HS(request):
#    return render_to_response("help/QLNT_HS.html", context_instance=RequestContext(request))
#def QLNT_HS_Lophoc(request):
#    return render_to_response("help/QLNT_HS_Lophoc.html", context_instance=RequestContext(request))
