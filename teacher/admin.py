from django.contrib import admin
from teacher.models import Register, Teacher, Student, Class, Attend

admin.site.register(Register)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Class)
admin.site.register(Attend)
