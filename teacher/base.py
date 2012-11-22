# coding: utf-8
import os
import simplejson
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader, Context
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist

NOT_ALLOWED_TEACHER_TEMPLATE = os.path.join('teacher', 'not-allowed.html')

class BaseTeacherView(TemplateView):
    def __init__(self, *args, **kwargs):
        super(BaseTeacherView, self).__init__(*args, **kwargs)
        # Store teacher_id for further usage and checking
        # allow_other_teacher is False means that teacher's page
        # can't be accessed by other users
        self.teacher_id = None
        self.allow_other_teacher = False
        
    def _get_teacher(self):
        return self.request.user.teachers

    def _right_teacher_id(self, teacher_id):
        return teacher_id == unicode(self.teacher.id)

    def reverse(self, *args, **kwargs):
        # Do the same work with Django reverse method but add
        # valid teacher_id to **kwargs as an extra work
        kwargs['kwargs']['teacher_id'] = self.teacher_id
        return reverse(*args, **kwargs)
    
    def request_type_not_allowed(self, request, *args, **kwargs):
        t = loader.get_template(NOT_ALLOWED_TEACHER_TEMPLATE)
        c = Context({})
        return HttpResponse(t.render(c), status=405)

    def illegal_request(self, params):
        # This method get called if user make an illegal request
        # It have to return a warning page
        t = loader.get_template(NOT_ALLOWED_TEACHER_TEMPLATE)
        c = Context({})
        return HttpResponse(t.render(c), status=403)

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        # Before calling the actual view, try to validate teacher.
        # If the page belongs to other teacher rather than user, return an
        # error by default. This default behavior can be disabled if
        # self.allow_other_teacher set to True
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(),
                    self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.teacher_id = kwargs['teacher_id']
        self.teacher = self._get_teacher()
        if not self.teacher_id:
            self.teacher_id = self.teacher.id
            return HttpResponseRedirect(self.reserve('teacher_index'))
        else:
            if (not self.allow_other_teacher
                    and not self._right_teacher_id(self.teacher_id)):
                return render_to_response(NOT_ALLOWED_TEACHER_TEMPLATE,
                        {}, context_instance=RequestContext(request))
        self.args = args
        self.kwargs = kwargs
        return handler(request, *args, **kwargs)

    def _menu(self, *args, **kwargs):
        # This method return objects attached to menu
        classes = self.teacher.class_set.order_by('-created')
        return {'classes': classes,
                'user_teacher': self.teacher}

    def _get(self, *args, **kwargs):
        # This method return all the needs to render reponse.
        # Every view class inheritted from this class
        # SHOULD OVERRIDE this method to deal with request processing.
        # SHOULD NOT return NONE, return {} instead
        raise Exception('NotImplemented')

    def _post(self, *args, **kwargs):
        # This method return all the needs to notify after post request.
        # Every view class inheritted from this class
        # SHOULD OVERRIDE this method to deal with request processing.
        # SHOULD NOT return NONE, return {} instead
        raise Exception('NotImplemented')

    def validate_params(self, *args, **kwargs):
        # THIS METHOD WILL BE CALLED TO VALIDATE RIGHT AFTER get(), post()... get
        # called.
        # This method try to validate the policy of each URI parameters
        # for example: if URI refers to teacher A, class B so it try to
        # ensure that B should belongs to A
        # This base method will try to validate online parameters from kwargs
        # which is teacher_id, class_id, student_id (teacher_id is already
        # validated inside dispatch, see self.dispatch for more detail)
        # After validation, it will pass cleaned_params to kwargs and return
        # args, kwargs, in case it's  failed to validate those params, only one
        # dictionay will be return (eg: {'success': False, 'message': 'Lop ko
        # dung'}), this dictionary will be handled by self.illegal_request()
        # This method can be invoked for further validations about mark_id,
        # note_id, etc...
        #
        cleaned_params = {'teacher': self.teacher}
        if 'class_id' in kwargs:
            # Going to validate class_id
            cl_id = kwargs['class_id']
            try:
                cl = self.teacher.class_set.get(id=cl_id)
                cleaned_params['class'] = cl
            except ObjectDoesNotExist:
                return {'success': False,
                        'message': u'Lớp không tồn tại'}

        if 'student_id' in kwargs:
            # Going to validate student_id
            pass
            try:
                st = cl.student_set.get(id=kwargs['student_id'])
                cleaned_params['student'] = st
            except ObjectDoesNotExist:
                return {'success': False,
                        'message': u'Học sinh không tồn tại'}

        kwargs['cleaned_params'] = cleaned_params
        return args, kwargs


    def get(self, *args, **kwargs):
        # This method handles get request:
        # If the request is via ajax, it's assumed to be called 
        # inside client's javascript. In this case, we return 
        # only the content part of the view (not include menu part)
        # in json: {'success': True, 'content': html_string}
        # Otherwise, the normal HttpResponse will be returned
        # (including menu and content part)
        # This situation appears when user access directly via url
        # (not from ajax)
        #
        #
        # THIS METHOD SHOULD NOT BE OVERRIDED

        # Try to validate parameters, avoid illegal request
        params = self.validate_params(self, *args, **kwargs)
        # if request is illegal, call self.illegal(params)
        if len(params) == 1: return self.illegal_request(params)
        # else grap args, kwargs to pass to other hanlder
        else: args, kwargs = params
        menus = self._menu(*args, **kwargs)
        params = self._get(*args, **kwargs)
        # If params is instance of HttpReponse, return it
        # because it must be the error page
        if isinstance(params, HttpResponse): return params
        params.update(menus)
        if self.request.is_ajax():
            params['full'] = False
            res = render_to_string(self.template_name, params,
                    context_instance=RequestContext(self.request))
            return HttpResponse(simplejson.dumps(
                {'success': True, 'content': res}),
                mimetype='json')

        else:
            params['full'] = True
            print self.template_name
            return render_to_response(self.template_name,
                    params, context_instance=RequestContext(self.request))

    def post(self, *args, **kwargs):
        # This method handles post request:
        # If the request is via ajax, it's assumed to be called 
        # inside client's javascript. In this case, we return 
        # the result, message, error list ...
        # in json: {'success': True/False,
        # 'message': message_string,
        # 'error_list': error_list,
        # ........................}
        # Otherwise, the normal HttpResponse will be returned
        # (including menu and content part)
        # This situation appears when user disable their javascript
        # functionalities (not from ajax)
        #
        # THIS METHOD SHOULD NOT BE OVERRIDED

        # Try to validate parameters, avoid illegal request
        params = self.validate_params(self, *args, **kwargs)
        # if request is illegal, call self.illegal(params)
        if len(params) == 1: return self.illegal_request(params)
        # else grap args, kwargs to pass to other hanlder
        else: args, kwargs = params
        params = self._post(*args, **kwargs)
        if self.request.is_ajax():
            return HttpResponse(simplejson.dumps(
                params), mimetype='json')

        else:
            # This this a dump return, it just stands here to
            # handle nonajax post which is usually not supported
            return HttpResponse(unicode(params))

# This class provide 2 method to extract request type
# and call appropriate method to handle particular request type
# This calling has its own convention:
# - When a get or post request for the request type as (create, modify, remove,
# view), for example is view and the method is post, it will search for method
# named: _post_view, thus every view class that inherits this class should have
# the handling methods in the name of _(post|get)_(create|modify|remove|view)
# - If a method such as _get_view cant be found, it will call
# request_type_not_allowed method (see BaseTeacherView for more detail about
# this method)
class RestfulView:
    def _get(self, *args, **kwargs):
        try:
            req_type = kwargs['request_type']
        except KeyError:
            req_type = 'view'
        if req_type in self.request_type:
            handler = getattr(self, '_get_' + req_type,
                    self.request_type_not_allowed)
        else:
            handler = self.request_type_not_allowed
        return handler(*args, **kwargs)
    
    def _post(self, *args, **kwargs):
        try:
            req_type = kwargs['request_type']
        except KeyError:
            req_type = 'view'
        if req_type in self.request_type:
            handler = getattr(self, '_post_' + req_type,
                    self.request_type_not_allowed)
        else:
            handler = self.request_type_not_allowed
        return handler(*args, **kwargs)

