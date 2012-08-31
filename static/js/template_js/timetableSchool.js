/**
 * Created by PyCharm.
 * User: leeyun
 * Date: 2/11/12
 * Time: 10:58 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function() {

    $("#upload_modal").on('hidden', function(){
        location.reload('true');
    });
    $("#upload-modal-exit").click(function(){
        $("#upload_modal").modal('hide');
        return false;
    });

    $("#changeTeacher").click(function() {
        if ($(this).hasClass('checked')) {
            $(this).removeClass('checked');
            $(this).html('Hiện giáo viên dạy');
            $(".teacher").each(function() {
                $(this).hide();
            })
        } else {
            $(this).addClass('checked');
            $(this).html('Ẩn giáo viên dạy');
            $(".teacher").each(function() {
                $(this).show();
            })
        }
    });
});