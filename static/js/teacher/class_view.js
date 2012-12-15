/**
 * Created with PyCharm.
 * User: Admin
 * Date: 12/13/12
 * Time: 9:09 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function () {
    $("#upload_modal").on('hidden', function(){
        location.reload('true');
    });

    $("#upload-modal-exit").click(function(){
        $("#upload_modal").modal('hide');
        return false;
    });
});