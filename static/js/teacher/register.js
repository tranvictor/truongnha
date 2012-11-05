$(document).ready(function () {
    // setting up layout
    Recaptcha.create("6LdfIc4SAAAAACxRkXpRGhyK-mHYUsCQIHwF42fc",
        "captcha-form",
        {
            theme:"white",
            callback:Recaptcha.focus_response_field,
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

    $("#sendRegister").click(function () {
        var self = $(this);
        // check validity
        var registerName = $("#id_name").val().replace(/^\s+|\s+$/g, '');
        if (registerName == "") {
            $("#id_name").css('border-color', 'red');
            $("#notify").showNotification("Họ và tên còn trống", 2000);
            return false;
        } else $("#id_name").css('border-color', '#CCC');
        var registerPhone = $("#id_phone").val().replace(/^\s+|\s+$/g, '');
        if (registerPhone == "") {
            $("#id_phone").css('border-color', 'red');
            $("#notify").showNotification("Số điện thoại còn trống", 2000);
            return false;
        } else $("#id_phone").css('border-color', '#CCC');
        var registerEmail = $("#id_email").val().replace(/^\s+|\s+$/g, '');
        if (!(registerEmail.split('@').length - 1 == 1
                && registerEmail.split('.').length - 1 > 0)) {
            $("#id_email").css('border-color', 'red');
            $("#notify").showNotification("Email không tồn tại", 2000);
            return false;
        } else $("#id_email").css('border-color', '#CCC');
                var recaptchaChallengeField = $("#recaptcha_challenge_field").val();
        var recaptchaResponseField = $("#recaptcha_response_field").val();
        // end checking
        if (self.text() == "Gửi") {
            var arg = { type:"POST",
                url:"",
                global:false,
                data:{ name:registerName,
                    phone:registerPhone,
                    email:registerEmail,
                    recaptcha_challenge_field:recaptchaChallengeField,
                    recaptcha_response_field:recaptchaResponseField},
                datatype:"json",
                success:function (json) {
                    if (json.success) {
                        $("#notify").showNotification("Đã đăng ký thành công", 2000);
                        window.location.replace(json.redirect);
                    } else {
                        $("#notify").showNotification(json.message, 2000);
                    }
                },
                error:function () {
                    $("#notify").showNotification("Gặp lỗi khi gửi đăng ký", 2000);
                }
            };
            $.ajax(arg);
        }
        return false;
    });
});
