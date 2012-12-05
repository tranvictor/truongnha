from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import models
import os
OVER_SCHOOL = ['GIAM_DOC_SO', 'TRUONG_PHONG']
ABOUT = os.path.join('about.html')

def index(request):
    if not request.user.is_authenticated():
        return render_to_response("index.html", context_instance=RequestContext(request)) 
    elif request.user.is_superuser:
        return render_to_response("index.html", context_instance=RequestContext(request))
    elif request.user.get_profile().position in OVER_SCHOOL:
        return HttpResponseRedirect(reverse('department_report'))
    else:
        #school_id = request.user.userprofile.organization.id
        return HttpResponseRedirect(reverse('school_index'))

def about(request):
    return render_to_response(ABOUT)

@models.permalink
def get_absolute_url(self):
        return 'profiles_profile_detail', (), { 'username': self.user.username }
get_absolute_url = models.permalink(get_absolute_url)

def help(request, page = None):
    if not page:
        return render_to_response("help/help.html", context_instance=RequestContext(request))
    else:
        template_page = "help/" + str(page).replace("_", "-") + '.html'
        return render_to_response(template_page, context_instance=RequestContext(request))