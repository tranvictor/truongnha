/**
 * Created by PyCharm.
 * User: vutran
 * Date: 2/10/12
 * Time: 9:36 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function(){
    $("#source_id").change(function(){
        $(this).children("option[value=-1]").remove();
        $("#notify").showNotification("Đang tải dữ liệu xin vui lòng chờ");
        var data = {request_type:'source',
            class_id: $(this).val()
        };
        var arg = {
            data : data,
            type: "POST",
            dataType: "json",
            url: "/school/movestudents",
            global: false,
            success: function(json){
                $("#target_id").empty();
                $("#students_table").empty();
                $("#target_id").append(json.ClassList);
                $("#students_table").append(json.table);
                $("#selectAll").show();
                $("#moveSelected").show();
            }
        };
        $.ajax(arg);
        return false;
    });
    var moveSelected = function() {
        if ($("#target_id").val() == -1){
            alert("Bạn chưa chọn lớp để học sinh chuyển tới");
            return false;
        }
        if (!$("#checkbox_all").is(':checked')) {
            alert("Bạn chưa chọn học sinh nào để chuyển lớp.");
            return false;
        }
        var answer = confirm('Bạn có muốn chuyển những học sinh đã chọn không?');
        if (!answer) return false;
        $("#moveSelected").attr('disabled',true);
        var data = '';
        $(".selected").each(function() {
            data = data + $(this).attr('class').split(' ')[0] + '-';
        });
        $("#notify").text("Hệ thống đang chuyển học sinh.\nQuá trình có thể diễn ra lâu xin bạn vui lòng chờ.");
        $("#notify").show();
        var arg = { type:"POST",
            url: "/school/movestudents",
            global: false,
            data: {data:data, request_type:'move',
                target:$("#target_id").val()
            },
            datatype:"json",
            error: function(){
                $("#notify").showNotification("Có lỗi xảy ra.");
                $("#moveSelected").attr('disabled',false);
            },
            success: function() {
                $("#notify").showNotification("Đã chuyển xong.");
                $("#moveSelected").attr('disabled',false);
                $(".selected").remove();
                $("#checkbox_all").prop("checked",false);
            }
        };
        $.ajax(arg);
        return false;
    };
    var select = function() {
        if ($(this).hasClass('student')) {
            var id = $(this).attr('class').split(' ')[0];
            var checkboxid = '#checkbox_' + id;
            var checkboxall = '#checkbox_all';
            if ($(this).hasClass('selected')) {
                $(this).removeClass('selected');
                $(checkboxid).prop("checked", false);
                var n = $("input:checked").length;
                if (n == 1) $(checkboxall).prop("checked", false);
            } else {
                $(this).addClass('selected');
                $(checkboxid).prop("checked", true);
                $(checkboxall).prop("checked", true);
            }
        }
    };
    $("tr").live("click",select);

    var selectAllStudent = function(){
        $("tr").each(function() {
            if (!$(this).hasClass('selected'))
                $(this).trigger('click');
        });
    };
    var deselectAllStudent = function(){
        $("tr").each(function() {
            if ($(this).hasClass('selected'))
                $(this).trigger('click');
        });
    };

    $("#checkbox_all").live('click', function() {
        if ($("#checkbox_all").is(':checked'))
            selectAllStudent();
        else deselectAllStudent();

    });
    $("#selectAll").live("click",function() {
        $("#students_table tr").each(select);
        return false;
    });
    $("#moveSelected").click(moveSelected);
});