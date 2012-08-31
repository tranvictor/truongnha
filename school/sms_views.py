# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.files import File
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.views.generic.list import ListView
from sms.models import sms
from sms.utils import *
from school.forms import *
from django.conf import settings
