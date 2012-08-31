from django.conf.urls import patterns, url
from school import views
import viewMark, viewCount, viewFinish, exam, helptools,\
    writeExcel, importMark,departmentReport, school_functions, class_functions, excel_interaction, makeTest
urlpatterns = patterns('',
    url(r'^$' ,  viewCount.report, name="report"),
    url(r'viewSchool/(?P<school_id>\w+)$' ,  viewCount.report, name="report"),
    # cac chuc nang thong ke tong hop cap so
    url(r'departmentReport$' ,  departmentReport.departmentReport, name="department_report"),
    url(r'practisingByGrade$' , departmentReport.practisingByGrade, name="practising_by_grade"),
    url(r'practisingByGrade/(?P<yearNumber>\w+)$' ,  departmentReport.practisingByGrade, name="practising_by_grade"),
    url(r'practisingByGrade/(?P<yearNumber>\w+)/(?P<termNumber>\w+)$' ,  departmentReport.practisingByGrade, name="practising_by_grade"),
    url(r'practisingByGrade/(?P<yearNumber>\w+)/(?P<termNumber>\w+)/(?P<isExcel>\w+)$' , departmentReport.practisingByGrade, name="practising_by_grade"),

    url(r'practisingByMajor$' ,  departmentReport.practisingByMajor, name="practising_by_major"),
    url(r'practisingByMajor/(?P<yearNumber>\w+)$' ,  departmentReport.practisingByMajor, name="practising_by_major"),
    url(r'practisingByMajor/(?P<yearNumber>\w+)/(?P<termNumber>\w+)$' ,  departmentReport.practisingByMajor, name="practising_by_major"),
    url(r'practisingByMajor/(?P<yearNumber>\w+)/(?P<termNumber>\w+)/(?P<isExcel>\w+)$' ,  departmentReport.practisingByMajor, name="practising_by_major"),

    url(r'practisingByDistrict$' ,  departmentReport.practisingByDistrict, name="practising_by_district"),
    url(r'practisingByDistrict/(?P<yearNumber>\w+)$' ,  departmentReport.practisingByDistrict, name="practising_by_district"),
    url(r'practisingByDistrict/(?P<yearNumber>\w+)/(?P<termNumber>\w+)$' ,  departmentReport.practisingByDistrict, name="practising_by_district"),
    url(r'practisingByDistrict/(?P<yearNumber>\w+)/(?P<termNumber>\w+)/(?P<isExcel>\w+)$' ,  departmentReport.practisingByDistrict, name="practising_by_district"),

    url(r'learningByGrade$' , departmentReport.learningByGrade, name="learning_by_grade"),
    url(r'learningByGrade/(?P<yearNumber>\w+)$' ,  departmentReport.learningByGrade, name="learning_by_grade"),
    url(r'learningByGrade/(?P<yearNumber>\w+)/(?P<termNumber>\w+)$' ,  departmentReport.learningByGrade, name="learning_by_grade"),
    url(r'learningByGrade/(?P<yearNumber>\w+)/(?P<termNumber>\w+)/(?P<isExcel>\w+)$' , departmentReport.learningByGrade, name="learning_by_grade"),

    url(r'learningByMajor$' ,  departmentReport.learningByMajor, name="learning_by_major"),
    url(r'learningByMajor/(?P<yearNumber>\w+)$' ,  departmentReport.learningByMajor, name="learning_by_major"),
    url(r'learningByMajor/(?P<yearNumber>\w+)/(?P<termNumber>\w+)$' ,  departmentReport.learningByMajor, name="learning_by_major"),
    url(r'learningByMajor/(?P<yearNumber>\w+)/(?P<termNumber>\w+)/(?P<isExcel>\w+)$' ,  departmentReport.learningByMajor, name="learning_by_major"),

    url(r'learningByDistrict$' ,  departmentReport.learningByDistrict, name="learning_by_district"),
    url(r'learningByDistrict/(?P<yearNumber>\w+)$' ,  departmentReport.learningByDistrict, name="learning_by_district"),
    url(r'learningByDistrict/(?P<yearNumber>\w+)/(?P<termNumber>\w+)$' ,  departmentReport.learningByDistrict, name="learning_by_district"),
    url(r'learningByDistrict/(?P<yearNumber>\w+)/(?P<termNumber>\w+)/(?P<isExcel>\w+)$' ,  departmentReport.learningByDistrict, name="learning_by_district"),

    url(r'titleByGrade$' , departmentReport.titleByGrade, name="title_by_grade"),
    url(r'titleByGrade/(?P<yearNumber>\w+)$' ,  departmentReport.titleByGrade, name="title_by_grade"),
    url(r'titleByGrade/(?P<yearNumber>\w+)/(?P<termNumber>\w+)$' ,  departmentReport.titleByGrade, name="title_by_grade"),
    url(r'titleByGrade/(?P<yearNumber>\w+)/(?P<termNumber>\w+)/(?P<isExcel>\w+)$' , departmentReport.titleByGrade, name="title_by_grade"),

    url(r'titleByMajor$' ,  departmentReport.titleByMajor, name="title_by_major"),
    url(r'titleByMajor/(?P<yearNumber>\w+)$' ,  departmentReport.titleByMajor, name="title_by_major"),
    url(r'titleByMajor/(?P<yearNumber>\w+)/(?P<termNumber>\w+)$' ,  departmentReport.titleByMajor, name="title_by_major"),
    url(r'titleByMajor/(?P<yearNumber>\w+)/(?P<termNumber>\w+)/(?P<isExcel>\w+)$' ,  departmentReport.titleByMajor, name="title_by_major"),

    url(r'titleByDistrict$' ,  departmentReport.titleByDistrict, name="title_by_district"),
    url(r'titleByDistrict/(?P<yearNumber>\w+)$' ,  departmentReport.titleByDistrict, name="title_by_district"),
    url(r'titleByDistrict/(?P<yearNumber>\w+)/(?P<termNumber>\w+)$' ,  departmentReport.titleByDistrict, name="title_by_district"),
    url(r'titleByDistrict/(?P<yearNumber>\w+)/(?P<termNumber>\w+)/(?P<isExcel>\w+)$' ,  departmentReport.titleByDistrict, name="title_by_district"),

    url(r'countFinalMark/(?P<type>\w+)$',  departmentReport.countFinalMark, name="count_final_mark"),
    url(r'countFinalMark/(?P<type>\w+)/(?P<yearNumber>\w+)$',  departmentReport.countFinalMark, name="count_final_mark"),
    url(r'countFinalMark/(?P<type>\w+)/(?P<yearNumber>\w+)/(?P<termNumber>\w+)$',  departmentReport.countFinalMark, name="count_final_mark"),
    url(r'countFinalMark/(?P<type>\w+)/(?P<yearNumber>\w+)/(?P<termNumber>\w+)/(?P<subjectIndex>\w+)$',  departmentReport.countFinalMark, name="count_final_mark"),
    url(r'countFinalMark/(?P<type>\w+)/(?P<yearNumber>\w+)/(?P<termNumber>\w+)/(?P<subjectIndex>\w+)/(?P<blockIndex>\w+)$',  departmentReport.countFinalMark, name="count_final_mark"),
    url(r'countFinalMark/(?P<type>\w+)/(?P<yearNumber>\w+)/(?P<termNumber>\w+)/(?P<subjectIndex>\w+)/(?P<blockIndex>\w+)/(?P<isExcel>\w+)$',  departmentReport.countFinalMark, name="count_final_mark"),


    #thong ke toan truong
#    url(r'countInSchool$' ,  viewCount.countInSchool, name="count_in_school"),
#    url(r'countPractisingInTerm/(?P<term_id>\w+)$', viewCount.countPractisingInTerm, name="count_practising_in_term"),
#    url(r'countPractisingInYear/(?P<year_id>\w+)$', viewCount.countPractisingInYear, name="count_practising_in_year"),
#    url(r'countLearningInTerm/(?P<term_id>\w+)$', viewCount.countLearningInTerm, name="count_learning_in_term"),
#    url(r'countLearningInYear/(?P<year_id>\w+)$', viewCount.countLearningInYear, name="count_learning_in_year"),
#    url(r'countAllInTerm/(?P<term_id>\w+)$', viewCount.countAllInTerm, name="count_all_in_term"),
#    url(r'countAllInYear/(?P<year_id>\w+)$', viewCount.countAllInYear, name="count_all_in_year"),
    #thong ke hoc luc, hanh kiem, danh hieu
    url(r'count1/(?P<year_id>\w+)/(?P<number>\w+)/(?P<isExcel>\w+)$', viewCount.count1, name="count1"),
    url(r'count1/(?P<year_id>\w+)/(?P<number>\w+)/(?P<isExcel>\w+)$', viewCount.count1, name="count1"),
    url(r'count1/(?P<year_id>\w+)/(?P<number>\w+)$', viewCount.count1, name="count1"),
    url(r'count1$', viewCount.count1, name="count1"),
    url(r'count2/(?P<type>\w+)/(?P<modeView>\w+)$', viewCount.count2, name="count2"),
    url(r'count2/(?P<type>\w+)/(?P<modeView>\w+)/(?P<year_id>\w+)/(?P<number>\w+)/(?P<index>\w+)$', viewCount.count2, name="count2"),
    url(r'count2/(?P<type>\w+)/(?P<modeView>\w+)/(?P<year_id>\w+)/(?P<number>\w+)/(?P<index>\w+)/(?P<isExcel>\w+)$', viewCount.count2, name="count2"),
    url(r'countSMS$', viewCount.countSMS, name="count_sms"),
    url(r'countSMS/(?P<type>\w+)$', viewCount.countSMS, name="count_sms"),
    url(r'countSMS/(?P<type>\w+)/(?P<day>\w+)/(?P<month>\w+)/(?P<year>\w+)/(?P<day1>\w+)/(?P<month1>\w+)/(?P<year1>\w+)$', viewCount.countSMS, name="count_sms"),

    url(r'printMarkBook$' ,  writeExcel.printMarkBook, name="print_mark_book"),
    url(r'printMarkBook/(?P<class_id>\w+)$' ,  writeExcel.printMarkBook, name="print_mark_book"),

    url(r'excelClassList$' ,  writeExcel.excelClassList, name="excel_class_list"),
    url(r'excelClassList/(?P<class_id>\w+)$' ,  writeExcel.excelClassList, name="excel_class_list"),

    url(r'printMarkForClass$' ,  writeExcel.printMarkForClass, name="print_mark_for_class"),
    url(r'printMarkForClass/(?P<termNumber>\w+)$' ,  writeExcel.printMarkForClass, name="print_mark_for_class"),
    url(r'printMarkForClass/(?P<termNumber>\w+)/(?P<class_id>\w+)$' ,  writeExcel.printMarkForClass, name="print_mark_for_class"),
    url(r'markExcelForAStudent/(?P<class_id>\w+)/(?P<student_id>\w+)/(?P<term_id>\w+)$' ,  writeExcel.markExcelForAStudent, name="mark_excel_for_a_student"),

    url(r'printDanhHieu$' ,  viewCount.printDanhHieu, name="print_danh_hieu"),
    url(r'printDanhHieu/(?P<year_id>\w+)/(?P<term_number>\w+)/(?P<type>\w+)$' ,  viewCount.printDanhHieu, name="print_danh_hieu"),
    url(r'printDanhHieu/(?P<year_id>\w+)/(?P<term_number>\w+)/(?P<type>\w+)/(?P<isExcel>\w+)$' ,  viewCount.printDanhHieu, name="print_danh_hieu"),

    url(r'printNoPass$' ,  viewCount.printNoPass, name="print_no_pass"),
    url(r'printNoPass/(?P<type>\w+)$' ,  viewCount.printNoPass, name="print_no_pass"),
    url(r'printNoPass/(?P<type>\w+)/(?P<isExcel>\w+)$' ,  viewCount.printNoPass, name="print_no_pass"),

)
