/**
 * Created with PyCharm.
 * User: Admin
 * Date: 12/13/12
 * Time: 9:09 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function () {
    'use strict';

    var id = window.location.pathname.split('/');
    var i = 0, cl_id = 0, teacher_id = 0;
    for ( i=0; i < id.length; i++){
        if (id[i] == 'teacher') teacher_id = id[i+1];
        else if (id[i] == 'class') cl_id = id[i+1];
    }

    $("#upload_modal").on('hidden', function(){
        location.reload('true');
    });

    $("#upload-modal-exit").click(function(){
        $("#upload_modal").modal('hide');
        return false;
    });
    $('#student-table-div').tnTable();

    var delSelected = function() {
        if (!$("#checkbox_all").is(':checked')) {
            alert("Hãy chọn ít nhất một học sinh để xoá.");
            return false;
        }
        var answer = confirm('Bạn có muốn xóa những học sinh đã chọn không?');
        if (!answer) return false;
        var data = '';
        var $selected = $(".selected");
        for ( var i = $selected.length; i--;){
            data += $($selected[i]).attr('data-id').split(' ')[0] + '-';
        }
        var $notify = $("#notify").text("Đang xóa...").show();
        var arg = { type:"POST",
            url:'/teacher/' + teacher_id +'/class/' + cl_id +'/student/delete',
            global: false,
            data: {data:data, request_type:'del'},
            datatype:"json",
            success: function(json) {
                $notify.showNotification(json.message);
                location.reload('true');
            },
            error:function(){
                $notify.showNotification("Có lỗi xảy ra");
            }
        };
        $.ajax(arg);
        return false;
    };
    $("#delSelected").click(delSelected);
});
