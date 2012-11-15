from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
import os
OVER_SCHOOL = ['GIAM_DOC_SO', 'TRUONG_PHONG']
ABOUT = os.path.join('about.html')

def index(request):
    if not request.user.is_authenticated():
        return render_to_response("index.html",
                context_instance=RequestContext(request)) 
    else:
        try:
            request.user.teachers
            return HttpResponseRedirect(reverse('teacher_index',
                args=[request.user.teachers.id]))
        except ObjectDoesNotExist:
            pass
        try:
            request.user.student
            raise Exception('StudentNotSupported')
        except ObjectDoesNotExist:
            pass

    if request.user.is_superuser:
        return render_to_response("index.html",
                context_instance=RequestContext(request))
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
