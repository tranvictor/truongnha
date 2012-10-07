# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.filter(name='get_value')
def get_value(d, k):
    return d[k] 
