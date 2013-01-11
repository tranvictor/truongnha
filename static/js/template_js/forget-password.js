$(document).ready(function () {
    $("#id_forgetPasswordForm").submit(function () {
        clear_bootstrap_error();
        var arg = { type: "POST",
            global: false,
            data: $(this).serialize(),
            datatype: "json",
            success: function (json) {
                $("#notify").showNotification(json.message, 2000);
                if (json.success == false){
                    add_bootstrap_error(json.err);
                }
            },
            error: function (json) {
                $("#notify").showNotification('Có vấn đề với kết nối tới hệ thống', 2000);
            }
        };
        $.ajax(arg);
        return false;
    });
});
