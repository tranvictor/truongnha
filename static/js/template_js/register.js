$(document).ready(function () {
    if (document.location.protocol == 'https:'){
        window.location.replace(
            'http://' + document.location.host + document.location.pathname);
    }
    // setting up layout
    var maxWidth = -1;
    $(".verticalLabel").each(function () {
        var width = parseInt($(this).css('width'));
        if (width > maxWidth) maxWidth = width;
    });
    $(".verticalLabel").each(function () {
        $(this).css('width', maxWidth);
    });

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
        var registerName = $("#registerName").val().replace(/^\s+|\s+$/g, '');
        if (registerName == "") {
            $("#registerName").css('border-color', 'red');
            $("#notify").showNotification("Họ và tên còn trống", 2000);
            return false;
        } else $("#registerName").css('border-color', '#999');
        var registerEmail = $("#registerEmail").val().replace(/^\s+|\s+$/g, '');
        if (!(registerEmail.split('@').length - 1 == 1 && registerEmail.split('.').length - 1 > 0)) {
            $("#registerEmail").css('border-color', 'red');
            $("#notify").showNotification("Email không tồn tại", 2000);
            return false;
        } else $("#registerEmail").css('border-color', '#999');
        var registerSchoolName = $("#registerSchoolName").val().replace(/^\s+|\s+$/g, '');
        if (registerSchoolName == "") {
            $("#registerSchoolName").css('border-color', 'red');
            $("#notify").showNotification("Tên trường còn trống", 2000);
            return false;
        } else $("#registerSchoolName").css('border-color', '#999');
        var registerPhone = $("#registerPhone").val().replace(/^\s+|\s+$/g, '');
        var registerSchoolAddress = $("#registerSchoolAddress").val().replace(/^\s+|\s+$/g, '');
        var registerSchoolLevel = $("#registerSchoolLevel").val();
        var registerSchoolProvince = $("#registerSchoolProvince").val();
        var recaptchaChallengeField = $("#recaptcha_challenge_field").val();
        var recaptchaResponseField = $("#recaptcha_response_field").val();
        // end checking
        if (self.text() == "Gửi") {
            var arg = { type:"POST",
                url:"",
                global:false,
                data:{ register_name:registerName,
                    register_phone:registerPhone,
                    register_email:registerEmail,
                    school_name:registerSchoolName,
                    school_level:registerSchoolLevel,
                    school_address:registerSchoolAddress,
                    school_province:registerSchoolProvince,
                    recaptcha_challenge_field:recaptchaChallengeField,
                    recaptcha_response_field:recaptchaResponseField},
                datatype:"json",
                success:function (json) {
                    if (json.success) {
                        $("#notify").showNotification("Đã đăng ký thành công", 2000);
                        window.location.replace(json.redirect);
                    } else {
                        $("#notify").showNotification(json.message, 2000);
                        Recaptcha.reload();
                    }
                },
                error:function () {
                    $("#notify").showNotification("Gặp lỗi khi gửi đăng ký", 2000);
                    Recaptcha.reload();
                }
            };
            $.ajax(arg);
        }
        return false;
    });
});
