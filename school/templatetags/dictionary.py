# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.filter(name='get_value')
def get_value(d, k):
    if k == None: return None
    return d[k] 
