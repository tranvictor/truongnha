#from report.models import ReceiverReportForm, SendReportForm
#from app.models import PositionTypeForm
from django.shortcuts import render_to_response
from django.template import RequestContext

# Create your views here.
#help.html extend base.html, include 2 iframe named: QLNT_Menu.html-MenuBar & QLNT_Welcome.html-contentHelp
def help(request, page = None):
    if not page:
        return render_to_response("help/help.html", context_instance=RequestContext(request))
    else:
        template_page = "help/" + str(page).replace("_", "-") + '.html'
        return render_to_response(template_page, context_instance=RequestContext(request))

#def QLNT_HS(request):
#    return render_to_response("help/QLNT_HS.html", context_instance=RequestContext(request))
#def QLNT_HS_Lophoc(request):
#    return render_to_response("help/QLNT_HS_Lophoc.html", context_instance=RequestContext(request))
