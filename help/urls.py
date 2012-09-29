from django.conf.urls.defaults import patterns, url
from school import shortlink

urlpatterns = patterns('',
    # Add, remove, change personal information
    (r'^$', 'help.views.help'),
    (r'^sitemap$', 'help.views.sitemap'),
    (r'^menu$', 'help.views.menu'),

    (r'^welcome$', 'help.views.welcome'),

    (r'^lienhe$', 'help.views.lienhe'),
    (r'^dangky$', 'help.views.dangky'),
    (r'^dangnhap$', 'help.views.dangnhap'),
    (r'^home$', 'help.views.home'),
    (r'^taikhoan$', 'help.views.taikhoan'),
    (r'^thietlap$', 'help.views.thietlap'),
    (r'^thoikhoabieu$', 'help.views.thoikhoabieu'),
    (r'^baocao$', 'help.views.baocao'),
    (r'^giaovien$', 'help.views.giaovien'),
    (r'^lop-chunhiem$', 'help.views.lop_chunhiem'),
    (r'^lop$', 'help.views.lop'),
    (r'^lop-diem$', 'help.views.lop_diem'),
    (r'^lop-hanhkiem$', 'help.views.lop_hanhkiem'),
    (r'^lop-sapxep$', 'help.views.lop_sapxep'),
    (r'^lop-diemdanh$', 'help.views.lop_diemdanh'),
    (r'^lop-lichhoc$', 'help.views.lop_lichhoc'),
    (r'^lop-tongket$', 'help.views.lop_tongket'),
    (r'^lop-xeploai$', 'help.views.lop_xeploai'),
    (r'^lop-monhoc$', 'help.views.lop_monhoc'),
    (r'^lop-nhantin$', 'help.views.lop_nhantin'),
    (r'^lop-chuyenlop$', 'help.views.lop_chuyenlop'),

    (r'^giaovien-home$', 'help.views.giaovien_home'),
    (r'^giaovien-diem$', 'help.views.giaovien_diem'),
    (r'^giaovien-lopchunhiem$', 'help.views.giaovien_lopchunhiem'),
    (r'^giaovien-giaovien$', 'help.views.giaovien_giaovien'),
    (r'^giaovien-caclop$', 'help.views.giaovien_caclop'),
    (r'^giaovien-truong$', 'help.views.giaovien_truong'),

    #    (r'^home-hocsinh$', 'help.views.hocsinh'),
#    (r'^hocsinh-lophoc$', 'help.views.'),

    )
