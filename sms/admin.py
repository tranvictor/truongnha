from models import sms
from django.contrib import admin

class SmsAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'phone', 'content', 'created', 'modified', 'failed_reason']
    ordering = ['created']
admin.site.register(sms, SmsAdmin)
