from django.contrib import admin
from school.models import Block, Class, Teacher, Pupil, Mark, DiemDanh, KiLuat, TBNam, KhenThuong, StartYear, Year, Term, Subject

class MultiDBModelAdmin(admin.ModelAdmin):
    # A handy constant for the name of the alternate database.
    using = 'Mark_1'

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'Mark_1' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'Mark_1' database
        obj.delete(using=self.using)

    def queryset(self, request):
        # Tell Django to look for objects on the 'Mark_1' database.
        return super(MultiDBModelAdmin, self).queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'Mark_1' database.
        return super(MultiDBModelAdmin, self).formfield_for_foreignkey(db_field, request=request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'Mark_1' database.
        return super(MultiDBModelAdmin, self).formfield_for_manytomany(db_field, request=request, using=self.using, **kwargs)


admin.site.register(Block)

#admin.site.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'year_id']
    ordering = ['year_id']
admin.site.register(Class, ClassAdmin)

#admin.site.register(Team)
#admin.site.register(Group)

#admin.site.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'birthday', 'cmt', 'school_id']
    ordering = ['school_id', 'user_id']
admin.site.register(Teacher, TeacherAdmin)

#admin.site.register(Pupil)
class PupilAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'birthday', 'school_id', 'class_id']
    ordering = ['school_id', 'class_id', 'first_name', 'last_name']
admin.site.register(Pupil, PupilAdmin)

class MarkAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'subject_id', 'term_id' ]
    ordering = ['term_id', 'subject_id', 'student_id']
admin.site.register(Mark, MarkAdmin)

admin.site.register(Subject)

#admin.site.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['year_id', 'number']
    ordering = ['year_id']
admin.site.register(Term, TermAdmin)

#admin.site.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ['school_id', 'time']
    ordering = ['school_id']
admin.site.register(Year, YearAdmin)

admin.site.register(StartYear)

class KhenThuongAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'term_id', 'hinh_thuc', 'noi_dung']
    ordering = ['term_id', 'student_id', 'time']
admin.site.register(KhenThuong, KhenThuongAdmin)

class KiLuatAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'term_id', 'hinh_thuc', 'noi_dung']
    ordering = ['term_id', 'student_id', 'time']
admin.site.register(KiLuat, KiLuatAdmin)

#admin.site.register(TBHocKy)

admin.site.register(TBNam)

class DiemDanhAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'term_id', 'time', 'loai']
    ordering = ['student_id', 'term_id', 'time']
admin.site.register(DiemDanh, DiemDanhAdmin)

#admin.site.register(TKDiemDanh)
#admin.site.register(TKMon)
#admin.site.register(DanhSachLoaiLop)
#admin.site.register(Attend)


