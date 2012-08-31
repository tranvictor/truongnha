__author__ = 'vutran'

from djangorestframework.resources import ModelResource
from django.contrib.auth.models import User

class UserResource(ModelResource):
    model = User
    fields = ('username', 'password')
    ordering = ('username',)
