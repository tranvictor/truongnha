__author__ = 'vutran'
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from exceptions import IndexError
import urllib

from school.utils import get_school, get_permission, gvcn
from app.models import POSITION_CHOICE

PERMISSION_LIST = [permission[0] for permission in POSITION_CHOICE]
PERMISSION_LIST.append('SUPER_USER')
PERMISSION_LIST.append('GIAO_VIEN_CHU_NHIEM')

def need_login(func):
    def wrapper(*args, **kwargs):
        try:
            request = args[0]
            if request.user.is_anonymous():
                return HttpResponseRedirect(reverse('login_redirect',
                    args=[urllib.quote(urllib.quote(
                        request.get_full_path(), ''), '')]))
        except IndexError:
            raise Exception("IllegalRequestCall")
        except AttributeError:
            raise Http404("NeedLogedIn")

        if kwargs:
            return func(*args, **kwargs)
        else:
            return func(*args)

    return wrapper


def year_started(func):
    def wrapper(*args, **kwargs):
        try:
            request = args[0]
            if not request.user.is_superuser:
                try:
                    school = get_school(request)
                    if not school.status in [1, 2]:
                        return HttpResponseRedirect(reverse('index'))
                except Exception as e:
                    if e.message == 'DoesNotHaveAnySchool':
                        return HttpResponseRedirect(reverse('index'))
        except (IndexError, Exception) as e:
            print e
            if isinstance(e, IndexError):
                raise Exception("IllegalRequestCall")
            else:
                return HttpResponseRedirect(reverse('index'))
        if kwargs:
            return func(*args, **kwargs)
        else: return func(*args)

    return wrapper


def year_not_started(func):
    def wrapper(*args, **kwargs):
        try:
            request = args[0]
            if not request.user.is_superuser:
                try:
                    school = get_school(request)
                    if not school.status in [0, 3]:
                        return HttpResponseRedirect(reverse('index'))
                except Exception as e:
                    if e.message == 'DoesNotHaveAnySchool':
                        return HttpResponseRedirect(reverse('index'))
        except (IndexError, Exception) as e:
            print e
            if isinstance(e, IndexError):
                raise Exception("IllegalRequestCall")
            else:
                return HttpResponseRedirect(reverse('index'))
        if kwargs:
            return func(*args, **kwargs)
        else: return func(*args)

    return wrapper


def school_function(func):
    def wrapper(*args, **kwargs):
        try:
            request = args[0]
            get_school(request)
        except (IndexError, Exception) as e:
            print e
            if isinstance(e, IndexError):
                raise Exception("IllegalRequestCall")
            else:
                return HttpResponseRedirect(reverse('index'))
        if kwargs:
            if 'school_id' in kwargs:
                kwargs.pop('school_id')
            return func(*args, **kwargs)
        else: return func(*args)

    return wrapper

def operating_permission(rules):
    permission_list = [permission.split('__')[0] for permission in rules]

    def the_middle_wrapper(func):
        def wrapper(*args, **kwargs):
            try:
                request = args[0]
                if request.user.is_superuser:
                    permission = 'SUPER_USER'
                    if not 'SUPER_USER' in permission_list:
                        return HttpResponseRedirect(reverse('index'))
                else:
                    permission = get_permission(request)
                    if not permission in permission_list:
                        class_id = None
                        if 'class_id' in kwargs: class_id = kwargs['class_id']
                        if not (class_id
                                and permission == 'GIAO_VIEN'
                                and gvcn(request, class_id)):
                            return HttpResponseRedirect(reverse('school_index'))
                for rule in rules:
                    parts = rule.split('__')
                    if permission == parts[0]:
                        if len(parts) >= 2:
                            if 'request_type' in kwargs:
                                request_type = kwargs['request_type']
                                if not request_type in parts[1:]:
                                    return HttpResponseRedirect(reverse('index'))
                        elif len(parts) == 1:
                            pass
                        else: raise Exception('RuleSyntaxError')
            except (IndexError, Exception) as e:
                if isinstance(e, IndexError):
                    raise Exception("IllegalRequestCall")
                else:
                    return HttpResponseRedirect(reverse('school_index'))
            if kwargs:
                return func(*args, **kwargs)
            else: return func(*args)

        return wrapper

    for permission in permission_list:
        if not permission in PERMISSION_LIST:
            raise Exception(unicode(permission) + 'DoesNotMatch')
    return the_middle_wrapper
