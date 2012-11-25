# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.filter(name='times')
def times(number):
    return range(number)

@register.filter(name='get_dict_value')
def get_dict_value(d, k):
    if k == None: return None
    if not k in d: return None
    return d[k]

@register.filter(name='get_list_value')
def get_list_value(l,k):
    if len(l) <= k: return None
    return l[k]

@register.filter(name='make_class')
def make_class(k):
    s = str(k)
    s = s.replace('.','dot')
    return s