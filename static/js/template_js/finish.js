$(document).ready(function(){
    var classes = '';
    var clLableDone = true;
    var updateClassLabels = function(classes){
        var $classLabelPreview = $("#class_label_preview");
        var schoolLevel = $classLabelPreview.attr('data-toggle');
        var grades = schoolLevel=='2'?([9, 8, 7, 6]):([12, 11, 10]);
        for (var j=grades.length; j--;){
            var grade = grades[j];
            var $ulGrade = $('#grade-'+grade).html('');
            for (var i=classes.length; i--;){
                var cl = classes[i].split(' ');
                if (parseInt(cl[0]) == grade){
                    $ulGrade.append($('<li>'+classes[i]+'</li>'));
                }
            }
        }
    };
    $(".changeTerm").click(function(){
        var con = confirm("Bạn đang chọn chức năng chuyển kỳ. Sau khi thực hiện hệ thống sẽ chuyển sang kì học mới." +
            " Các điểm nhập vào hệ thống sau thời điểm chuyển kỳ sẽ được tính cho kì học mới. " +
            "Bạn có chắc chắn muốn chuyển không?");
        if (!con) return false;
    });
    $('#setup').click(function(){
        if ($(this).hasClass('disabled')) return false;
        var cur_year = parseInt($(this).attr('data-toggle')); 
        var year_time = parseInt($(this).attr('data-year-time'));
        if (year_time - cur_year < 1) {
            $('#notify').showNotification("Bạn đang ở năm học hiện tại rồi.");
            return false;
        }
        $.ajax({
            url: '/api/setting',
            global: false,
            success: function(data){
                classes = data['classes'];
                updateClassLabels(classes);
                // done preparing class labels preview
                $('#class_label_preview').slideDown(400);
                return false;
            } 
        });
        return false;
    });
    $('#update_class_label').click(function(){
        clLableDone = false;
        $('#start_year').addClass('disabled');
        var $classLabel = $('#class_labels');
        $('#class_label').val(classes.join(', '));
        $classLabel.slideDown(400);
        return false;
    });
    $('#save_class_label').click(function(){
        var schoolLevel = $("#class_label_preview").attr('data-toggle');
        var classLabels = $('#class_label').val() + ',';
        var check;
        if (schoolLevel == '2'){
            check = classLabels.match(/(\s*(6|7|8|9)\s*[^,]+,)+/g);
        } else {
            check = classLabels.match(/(\s*(10|11|12)\s*[^,]+,)+/g);
        }
        if (!check || check.length != 1 || check[0].length != classLabels.length){
            $('#notify').showNotification("Danh sách lớp không đúng");
            $('#class_label').focus();
        } else {
            $.ajax({
                url: '/api/setting/',
                type: 'POST',
                data: { class_labels: classLabels },
                success: function(data){
                    if (data.success){
                        $('#notify').showNotification("Nhập thành công danh sách lớp");
                        var classes = data.setting;
                        updateClassLabels(classes);
                        $('#start_year').removeClass('disabled');
                        $('#class_labels').slideUp(400);
                        clLableDone = true;
                    } else {
                        $('#notify').showNotification("Danh sách lớp không đúng");
                    }
                }
            });
        }
    });
    $('#start_year').click(function(){        
        if (clLableDone) $('#notify').showNotification("Hệ thống đang khởi tạo năm mới. Bạn vui lòng đợi trong chốc lát.", 40000);
        return clLableDone;
    });
});
