$(document).ready(function () {
    Recaptcha.create("6LdfIc4SAAAAACxRkXpRGhyK-mHYUsCQIHwF42fc",
        "captcha-form",
        {
            theme:"white",
            custom_translations : {
                instructions_visual : "Nhập chuỗi ký tự trên:",
                instructions_audio : ":",
                play_again : "Nghe lại",
                cant_hear_this : "Không nghe được",
                visual_challenge : "Hiện ảnh khác",
                audio_challenge : "Nghe âm thanh khác",
                refresh_btn : "Đọc lại",
                help_btn : "Aiuto",
                incorrect_try_again : "Không đúng, hãy thử lại."
            }
        }
    );
    $("#id_forgetPasswordForm").submit(function () {
        clear_bootstrap_error();
        var arg = { type: "POST",
            global: false,
            data: $(this).serialize(),
            datatype: "json",
            success: function (json) {
                $("#notify").showNotification(json.message, 2000);
                if (json.success == false){
                    Recaptcha.reload();
                    add_bootstrap_error(json.err);
                }
            },
            error: function (json) {
                $("#notify").showNotification('Có vấn đề với kết nối tới hệ thống', 2000);
                Recaptcha.reload();
            }
        };
        $.ajax(arg);
        return false;
    });
});
