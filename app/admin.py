from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from app.models import *

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'organization', 'position', 'email', 'phone')
    list_editable = ['first_name', 'last_name', 'organization', 'position', 'email', 'phone']
    list_filter = ('organization')
    search_fields = ['first_name', 'last_name', 'organization',  'email', 'phone', 'notes']

class UserProfileInline (admin.StackedInline):
    model = UserProfile
    max_num = 1
    
class CustomizedUserAdmin(UserAdmin):
    inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, CustomizedUserAdmin)

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'email', 'upper_organization', 'manager_name')
    list_filter = ('level', 'upper_organization', 'name')
    search_fields = ['name', 'email', 'manager_name']
    list_editable = ['name', 'address', 'email', 'upper_organization', 'manager_name']    
    list_per_page = 20
admin.site.register(Organization, OrganizationAdmin)

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'phone', 'email','title','content')
    list_filter = ('title', 'email')
    search_fields = ['title', 'content']
    list_per_page = 20
    
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Register)
admin.site.register(IP)
