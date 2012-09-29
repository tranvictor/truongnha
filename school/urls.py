from django.conf.urls import patterns, include, url
import school.report_urls as report_urls
from school import views, shortlink
import viewMark, viewFinish, exam, helptools, writeExcel, importMark, school_functions, class_functions, excel_interaction, makeTest

urlpatterns = patterns('',
    url(r'^$', views.school_index , name = "school_index"),
    # author: luulethe@gmail.com (cac ham den cho gach)
    #-----------------------------------------------------------------------
    # 2 ham nay dung de test, tao tat ca cac thong tin con thieu cho sinh vien
    # sau nay hoan thien, co the bo di
    url(r'viewschool/(?P<school_id>\d+)$', views.ssv, name="view_school"),
    url(r'thu$', makeTest.thu, name="test_thu"),
    url(r'toolToMakeCol$', makeTest.toolToMakeCol, name="tool_to_make_col"),
    url(r'markTable$', viewMark.markTable, name="mark_table"),
    url(r'markTable/(?P<term_id>\w+)$', viewMark.markTable, name="mark_table"),
    url(r'markTable/(?P<term_id>\w+)/(?P<class_id>\w+)$', viewMark.markTable, name="mark_table"),
    url(r'markTable/(?P<term_id>\w+)/(?P<class_id>\w+)/(?P<subject_id>\w+)$', viewMark.markTable, name="mark_table"),
    url(r'markTable/(?P<term_id>\w+)/(?P<class_id>\w+)/(?P<subject_id>\w+)/(?P<move>\w+)$', viewMark.markTable, name="mark_table"),
    
    url(r'markForTeacher$', viewMark.markForTeacher, name="mark_for_teacher"),
    url(r'markForTeacher/(?P<type>\w+)$', viewMark.markForTeacher, name="mark_for_teacher"),
    url(r'markForTeacher/(?P<type>\w+)/(?P<term_id>\w+)$', viewMark.markForTeacher, name="mark_for_teacher"),
    url(r'markForTeacher/(?P<type>\w+)/(?P<term_id>\w+)/(?P<subject_id>\w+)$', viewMark.markForTeacher, name="mark_for_teacher"),
    url(r'markForTeacher/(?P<type>\w+)/(?P<term_id>\w+)/(?P<subject_id>\w+)/(?P<move>\w+)$', viewMark.markForTeacher, name="mark_for_teacher"),
    
    url(r'markForAStudent/(?P<class_id>\w+)/(?P<student_id>\w+)$', viewMark.markForAStudent, name="mark_for_a_student"),
    url(r'markForAStudent/(?P<class_id>\w+)/(?P<student_id>\w+)/(?P<term_id>\w+)$', viewMark.markForAStudent, name="mark_for_a_student"),
    #url(r'markForASubject/(?P<subject_id>\w+)', viewMark.markForASubject),
    
    url(r'saveMark$', viewMark.saveMark, name="save_mark"),
    url(r'saveNote$', viewMark.saveNote, name="save_note"),
    url(r'sendSMSMark$', viewMark.sendSMSMark, name="send_sms_mark"),
    url(r'sendSMSResult$', shortlink.sendSMSResult, name="send_sms_result"),
    url(r'sendSMSResult/(?P<class_id>\w+)/(?P<termNumber>\w+)$', viewFinish.sendSMSResult, name="send_sms_result"),
    url(r'sendSMSResult/(?P<class_id>\w+)$', viewFinish.sendSMSResult, name="send_sms_result"),
    
    url(r'saveHocLai$', viewFinish.saveHocLai, name="save_hoc_lai"),
    url(r'saveRenLuyenThem$', viewFinish.saveRenLuyenThem, name="save_ren_luyen_them"),
    
	# xep loai hoc luc theo lop, gom co xep loai k1, k2 va ca nam
    url(r'xepLoaiHlTheoLop$', shortlink.xepLoaiHlTheoLop, name="xep_loai_hl_theo_lop"),
    url(r'xepLoaiHlTheoLop/(?P<class_id>\w+)/(?P<termNumber>\w+)$', viewFinish.xepLoaiHlTheoLop, name="xep_loai_hl_theo_lop"),
    url(r'xepLoaiHlTheoLop/(?P<class_id>\w+)/(?P<termNumber>\w+)/(?P<isCalculate>\w+)$', viewFinish.xepLoaiHlTheoLop, name="xep_loai_hl_theo_lop"),
    url(r'xlCaNamTheoLop$', shortlink.xlCaNamTheoLop, name="xl_ca_nam_theo_lop"),
    url(r'xlCaNamTheoLop/(?P<class_id>\w+)/(?P<type>\w+)$', viewFinish.xlCaNamTheoLop, name="xl_ca_nam_theo_lop"),
    url(r'xlCaNamTheoLop/(?P<class_id>\w+)/(?P<type>\w+)/(?P<xepLoai>\w+)$', viewFinish.xlCaNamTheoLop, name="xl_ca_nam_theo_lop"),
    url(r'thilai/(?P<class_id>\w+)$', viewFinish.thilai, name="thi_lai"),
    url(r'renluyenthem/(?P<class_id>\w+)$', viewFinish.renluyenthem, name="ren_luyen_them"),
    url(r'capNhapMienGiam/(?P<class_id>\w+)/(?P<student_id>\w+)$', viewMark.capNhapMienGiam, name="cap_nhap_mien_giam"),
    		
	# tinh diem tong ket hoc luc toan truong	
	# tong ket hoc ky, tinh toan bo hoc luc cua hoc sinh trong toan truong
	# xem xet lop nao da tinh xong, lop nao chua xong de hieu truong co the chi dao
	# co chuc nang ket thuc hoc ky	
    url(r'finishYear/(?P<year_id>\w+)$', viewFinish.finishYear, name="finish_year"),
    url(r'finishTerm/(?P<term_id>\w+)$', viewFinish.finishTerm, name="finish_term"),

    url(r'finish$', viewFinish.finish, name="finish"),
    url(r'finish/(?P<active_term>\w+)$', viewFinish.finish, name="finish"),
    url(r'finish/(?P<active_term>\w+)/(?P<term_number>\w+)/(?P<year_number>\w+)$', viewFinish.finish, name="finish"),
    url(r'finish/(?P<active_term>\w+)/(?P<term_number>\w+)/(?P<year_number>\w+)/(?P<is_calculate>\w+)$', viewFinish.finish, name="finish"),
    #url(r'countInSchool/(?P<year_id>\w+)' ,  viewCount.countInSchool),


    url(r'exportMark/(?P<term_id>\w+)/(?P<subject_id>\w+)$' ,  writeExcel.exportMark, name="export_mark"),
    url(r'exportMark/(?P<term_id>\w+)/(?P<subject_id>\w+)/(?P<colMieng>\w+)/(?P<col15Phut>\w+)/(?P<colMotTiet>\w+)$' ,  writeExcel.exportMark, name="export_mark"),
    url(r'importMark/(?P<term_id>\w+)/(?P<subject_id>\w+)$' ,  importMark.importMark, name="import_mark"),
    url(r'importMark/(?P<term_id>\w+)/(?P<subject_id>\w+)/(?P<checkDiff>\w+)$' ,  importMark.importMark, name="import_mark"),



    #------------------------------------------------------------------
    # cac chuc nang quan ly thi
    #------------------------------------------------------------------
    url(r'createListExam$',  exam.createListExam, name="create_list_exam"),

    url(r'classes$',  school_functions.classes, name = "classes"),
    url(r'classtab/(?P<block_id>\w+)$',  school_functions.classtab, name="class_tab"),
    url(r'classtab$',  school_functions.classtab, name="class_tab"),
    url(r'addclass$',  school_functions.addClass, name="add_class"),
    url(r'hanhkiem$',shortlink.hanhkiem,name="hanh_kiem"),
    url(r'hanhkiem/(?P<class_id>\w+)$',  class_functions.hanh_kiem, name="hanh_kiem"),
    #url(r'hanhkiem$',  class_functions.hanh_kiem, name="hanh_kiem"),
    #url(r'teachers_tab/(?P<sort_type>\w+)/(?P<sort_status>\w+)$',  views.teachers_tab),
    #url(r'teachers_tab$',  views.teachers_tab),
    #url(r'teachers_in_team/(?P<team_id>\w+)$',  views.teachers_in_team),
    url(r'teachers$',  school_functions.teachers, name="teachers"),
    #url(r'team/(?P<team_id>\w+)/(?P<sort_type>\w+)/(?P<sort_status>\w+)$',  views.team),
    #url(r'team/(?P<team_id>\w+)$',  views.team),
    #url(r'teachers_in_group/(?P<group_id>\w+)$',  views.teachers_in_group),
    url(r'students/organize/(?P<class_id>\w+)/(?P<type>\w+)$',  views.organize_students, name="orgamize_student"),
    url(r'viewTeacherDetail/(?P<teacher_id>\w+)$',  school_functions.viewTeacherDetail, name="teacher_detail"),
    url(r'viewStudentDetail/(?P<student_id>\w+)',  school_functions.viewStudentDetail, name ="student_detail"),
    #url(r'getStudent/(?P<student_id>\w+)',  views.student, name="student"),
    url(r'viewClassDetail$', shortlink.viewClassDetail, name="class_detail"),
    url(r'viewClassDetail/(?P<class_id>\w+)',  class_functions.viewClassDetail,
            name="class_detail"),
    url(r'viewUncategorizedClassDetail/(?P<class_id>\w+)/(?P<l_class_id>\w*)',
            class_functions.viewUncategorizedClassDetail,
            name="unc_class_detail"),
    url(r'subjectPerClass$',shortlink.subjectPerClass,name="subject_per_class"),
    url(r'subjectPerClass/(?P<class_id>\w+)',  class_functions.subjectPerClass, name="subject_per_class"),
    url(r'viewSubjectDetail/(?P<subject_id>\w+)',  class_functions.viewSubjectDetail, name="subject_detail"),
    url(r'start_year$', views.b1, name = "start_year"),

   
    url(r'khenthuong/(?P<student_id>\w+)/add$',  class_functions.add_khen_thuong, name="add_khen_thuong"),
    url(r'khenthuong/(?P<kt_id>\w+)/delete$',  class_functions.delete_khen_thuong, name="delete_khen_thuong"),
    url(r'khenthuong/(?P<kt_id>\w+)/edit$',  class_functions.edit_khen_thuong, name="edit_khen_thuong"),
    url(r'kiluat/(?P<student_id>\w+)/add$',  class_functions.add_ki_luat, name="add_ki_luat"),
    url(r'kiluat/(?P<kt_id>\w+)/edit$',  class_functions.edit_ki_luat, name="edit_ki_luat"),
    url(r'kiluat/(?P<kt_id>\w+)/delete$',  class_functions.delete_ki_luat, name="delete_ki_luat"),
    url(r'ktkl/(?P<student_id>\w+)$', class_functions.ktkl, name="ktkl"),

    url(r'diemdanhhs/(?P<student_id>\w+)/(?P<view_type>\w+)$',  class_functions.diem_danh_hs, name="diem_danh_hs"),
    url(r'diemdanhhs/(?P<student_id>\w+)$',  class_functions.diem_danh_hs, name="diem_danh_hs"),
    url(r'dsnghi/(?P<class_id>\w+)/(?P<day>\w+)/(?P<month>\w+)/(?P<year>\w+)$',  class_functions.ds_nghi, name="ds_nghi"),
    url(r'datecheck', views.date_check, name="date_check"),
    url(r'diemdanhold/(?P<class_id>\w+)/(?P<day>\w+)/(?P<month>\w+)/(?P<year>\w+)$',  class_functions.diem_danh, name="diem_danh"),
    url(r'diemdanh$', shortlink.diemdanh, name="dd"),
    url(r'diemdanh/(?P<class_id>\w+)/(?P<day>\w+)/(?P<month>\w+)/(?P<year>\w+)$', class_functions.dd, name="dd"),
    url(r'diemdanh/(?P<class_id>\w+)$',  views.diem_danh_form, name="diem_danh_form"),
    url(r'change_index/(?P<target>\w+)/(?P<class_id>\w+)$',  views.change_index, name="change_index"),
    url(r'password_change$',  views.password_change, name="password_change"),
    url(r'username_change$',  views.username_change, name="username_change"),
    url(r'success$', views.change_success, name="change_success"),
    url(r'student/account/(?P<student_id>\w+)$', views.student_account, name="student_account"),
    url(r'teacher/account/(?P<teacher_id>\w+)$', views.teacher_account, name="teacher_account"),
    url(r'movestudent/(?P<student_id>\w+)$', school_functions.move_one_student, name="move_one_student"),
    url(r'movestudents$', school_functions.move_students, name="move_students"),

    url(r'generate/(?P<class_id>\w+)/(?P<object>\w+)/$', excel_interaction.class_generate, name = "class_generate"),
    url(r'generate_teacher/(?P<type>\w+)/$', excel_interaction.teacher_generate, name = "teacher_generate"),
    url(r'start_year/import/student/(?P<class_id>\w+)/(?P<request_type>\w+)$',
            excel_interaction.student_import, name="student_import"),
    url(r'import/teacher/(?P<request_type>\w+)$',  excel_interaction.teacher_import, name = "teacher_import"),

    url(r'deleteTeacher/(?P<teacher_id>\w+)/(?P<team_id>\w+)$',  school_functions.deleteTeacher, name="delete_teacher"),
    url(r'deleteSubject/(?P<subject_id>\w+)',  class_functions.deleteSubject, name="delete_subject"),
    #url(r'deleteStudentInSchool/(?P<student_id>\w+)',  views.deleteStudentInSchool, name="delete_student_in_school"),
    url(r'deleteStudentInClass/(?P<student_id>\w+)',  class_functions.deleteStudentInClass, name="delete_student_in_class"),
    url(r'deleteClass/(?P<class_id>\w+)$',  views.deleteClass, name="delete_class"),
    url(r'deleteAllStudentsInClass/(?P<class_id>\w+)$', class_functions.deleteAllStudentsInClass, name="delete_all_student_in_class"),
    url(r'import/timeTable$', excel_interaction.import_timeTable, name="import_timetable"),
    url(r'export/timeTable$', excel_interaction.export_timetable, name="export_timetable"),
    url(r'timeTable$', shortlink.timeTable, name="timetable"),
    url(r'timeTable/(?P<class_id>\w+)$', views.timeTable, name="timetable"),
    url(r'timeTableSchool$', views.timeTable_school, name="timetable_school"),
    url(r'timetableStudent/(?P<day>\w+)/(?P<month>\w+)/(?P<year>\w+)$', views.timetableStudent, name="timetable_student"),
    url(r'timetableStudent$', views.timetableStudent, name="timetable_student"),
    url(r'timetableTeacher$', views.timetableTeacher, name="timetable_teacher"),
    url(r'^subjectAgenda/(?P<subject_id>\w+)$', views.subjectAgenda, name="subject_agenda"),
    url(r'import/subjectAgenda/(?P<subject_id>\w+)$', excel_interaction.import_agenda, name="import_agenda"),
    url(r'export_agenda/(?P<subject_id>\w+)$', excel_interaction.export_agenda, name="export_agenda"),
    url(r'export_hanh_kiem/(?P<class_id>\w+)$', excel_interaction.export_hanh_kiem, name="export_hanh_kiem"),
    url(r'import/hanh_kiem/(?P<class_id>\w+)$', excel_interaction.import_hanh_kiem, name="import_hanh_kiem"),

    #top menu
    url(r'setup/$',  views.setup, name = "setup"),
    #side menu
    url(r'classlabels/$',  views.class_label, name = "class_label"),
    url(r'info/$',  views.info, name = "info"),
    url(r'activate/teacher/$', school_functions.activate_teacher, name= "activate_teacher"),
    #url(r'classify/$',  views.classify, name = "classify"),
    #url(r'^school/test$', views.test), 
    
        #agenda
    url(r'donvi/$', views.donvi, name="donvi"),
    url(r'manage_school_agenda/(?P<subject>\w+)/(?P<grade>\w+)/(?P<term>\w+)$',  views.school_subject_agenda, name="school_subject_agenda"),
    url(r'manage_school_agenda/$',  views.school_subject_agenda, name="school_subject_agenda"),
    url(r'import/schoolAgenda/(?P<subject>\w+)/(?P<grade>\w+)/(?P<term>\w+)$', excel_interaction.import_school_agenda, name="import_school_agenda"),
    url(r'export_school_agenda/(?P<subject>\w+)/(?P<grade>\w+)/(?P<term>\w+)$', excel_interaction.export_school_agenda, name="export_school_agenda"),
    url(r'use_school_agenda/(?P<subject_id>\w+)$', views.use_school_agenda, name="use_school_agenda"),
    url(r'use_system_agenda/(?P<subject_id>\w+)$', views.use_system_agenda, name="use_system_agenda"),
    url(r'report/', include(report_urls)),
    url(r'export_gvcn/$', excel_interaction.export_gvcn_list, name="export_gvcn_list"),
#help
    #url(r'recover/$',  helptools.recover_marktime, name = "recover_marktime"),
    #url(r'sync_index/$',  helptools.sync_index, name = "sync_index"),
    #url(r'sync_subject/$',  helptools.sync_subject, name='sync_subject),
    #url(r'check_logic/$',  helptools.check_logic, name='check_logic),
    #url(r'sync_subject_type/$', helptools.sync_subject_type, name='sync_subject_type'),
    #url(r'sync_subject_nx/$',  helptools.sync_subject_nx, name='sync_subject_nx),
    #url(r'sync_subject_primary/$',  helptools.sync_subject_primary, name='sync_subject_primary),
    #url(r'test_table/$',  helptools.test_table),
    #url(r'copy_hanh_kiem_data/$', helptools.copy_hanh_kiem_data),
    #url(r'make_setting/$', helptools.make_setting),
    #url(r'convert_1n_mn/$',  helptools.convert_data_1n_mn),
    #url(r'realtime/$',  helptools.realtime, name="realtime"),
    #url(r'convertMark/$',  helptools.convertMark),
    #url(r'sync_major/$',  helptools.sync_major, name="sync_major"),
    #url(r'sync_user/$', helptools.disable_user, name="disable_user"),
    #url(r'sync_birthday/$', helptools.sync_birthday, name="sync_birthday"),
    #url(r'convert_diem_danh$',helptools.convert_diem_danh, name="convert_diem_danh"),
    #url(r'sync_name/$', helptools.sync_name, name="sync_name"),
    #url(r'sync_class_name/$', helptools.sync_class_name, name="sync_class_name"),
    #url(r'sync_startyear/$', helptools.sync_start_year, name="sync_start_year"),
    #url(r'sync_is_member/$', helptools.sync_is_member, name="sync_is_member"),
    #url(r'sync_tkdd/$', helptools.sync_tkdd, name="sync_tkdd"),
    url(r'fix_tkdd/$', helptools.fix_tkdd, name="fix_tkdd"),
)
