/**
 * Created by Vim.
 * User: vutran
 * Date: 8/4/11
 * Time: 6:05 AM
 *
 */
var applyListener = function () {

    $("input.datepicker").datepicker({
        format:'dd/mm/yyyy',
        weekStart:1
    });

};

$(document).ready(function () {
    var $document = $(document);
    // setting up css to render page in the right way
    //    $("footer").css('width',$(document).width());
    // end setting up
    // xss prevention
    function toAscii(str) {
        str = str.replace(/^\s+|\s+$/g, ''); // trim
        str = str.toLowerCase();
        // remove accents, swap ñ for n, etc
        var from = "àáäâèéëêìíïîòóöôùúüûñçảãạăắằẳẵặâầấẩẫậoóòỏõọuúùủũụêềếểễệeèéẻẽẹôồốổỗộơờớởỡợìỉĩíịyỳýỷỹỵ";
        var to = "aaaaeeeeiiiioooouuuuncaaaaaaaaaaaaaaaoooooouuuuuueeeeeeeeeeeeooooooooooooiiiiiyyyyyy";
        for (var i = 0, l = from.length; i < l; i++) {
            str = str.replace(new RegExp(from.charAt(i), 'g'), to.charAt(i));
        }
        return str;
    }

    $.fn.is_harmful = function (origin) {
        origin = toAscii(origin);
        origin = origin.replace(/\//g, ' ')
            .replace(/-/g, ' ')
            .replace('@', ' ')
            .replace('Nhanh:', '')
            .replace('nhanh:', '');
        var check = origin.match(/\d+:\d+/g);
        if (check && check.length == 1
                && check[0].length == origin.length) return false;
        if ($.encoder.encodeForHTML(
                    $.encoder.canonicalize(origin)) != origin) return true;
        return $.encoder.encodeForJavascript(
                $.encoder.canonicalize(origin)) != origin;

    };

    $('form').bind('submit', function () {
        var ok = true;
        var $textInputs = $document.find('input:text');
        for (var i = $textInputs.length; i--;) {
            var $this = $($textInputs[i]);
            var origin = $this.val();
            if ($this.is_harmful(origin)) {
                $this.focus();
                $this.showNotification("Thông tin bạn vừa nhập có chứa mã độc.");
                ok = false;
            }
        }
        if (!ok) return false;
    });

    // end xss prevention
    // jquery global function
    $.fn.disableNotification = function () {
        $(".notify-widget-pane").hide();
    };
    $.fn.enabelNotification = function () {
        $(".notify-widget-pane").show();
    };
    $.fn.showNotification = function (msg, duration) {
        $("#notify").enabelNotification();
        $("#notify").text(msg);
        $("#notify").fadeIn('fast');
        if (!duration || typeof duration != 'number') duration = 3000;
        $("#notify").data('delay', setTimeout(function () {
                $("#notify").stop(true, true).fadeOut('fast');
            },
            duration));
    };

    // local functions.
    $("#notify").ajaxStart(function () {
        $(this).text("Đang gửi dữ liệu lên máy chủ...");
        $(this).fadeIn('fast');
    });

    $("#notify").ajaxSuccess(function (event, request, settings) {
        $(this).text("Đã lưu.");
        $(this).data('delay', setTimeout(function () {
                $("#notify").stop(true, true).fadeOut('fast');
            },
            2000));
    });

    $("#notify").ajaxError(function (event, request, settings) {
        $(this).text("Gặp lỗi khi gửi dữ liệu tới máy chủ");
        $(this).data('delay', setTimeout(function () {
                $("#notify").stop(true, true).fadeOut('fast');
            },
            3000));
    });

    // every listener that wants to apply to DOM elements.
    applyListener();

    $(document).delegate("input:text", 'focusout', function () {
        var origin = $(this).val();
        if (origin.length > 1000) {
            $(this).focus();
            $("#notify").showNotification("Thông tin bạn vừa nhập quá dài.");
        }
        else if ($(this).is_harmful(origin)) {
            $(this).focus();
            $(this).showNotification("Thông tin bạn vừa nhập có chứa mã độc.");
        }
    });

    $("input:text").live('focus', function () {
        if (!$(this).hasClass('tiptipfocus')) {
            $(this).select();
            return false;
        }
    });

    $.ajaxSetup({
        beforeSend:function (xhr, settings) {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != "") {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }

            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }

            var ok = true;
            var $textInputs = $('input:text')
            for (var i = $textInputs.length; i--;) {
                var $this = $($textInputs[i]);
                var origin = $this.val();
                if (origin.length > 1000) {
                    $this.focus();
                    $("#notify").showNotification("Thông tin bạn vừa nhập quá dài.");
                    ok = false;
                } else if ($this.is_harmful(origin)) {
                    $this.focus();
                    $("#notify").showNotification(
                        "Thông tin bạn vừa nhập có chứa mã độc.");
                    ok = false;
                }
            }
            if (!ok) return false;
        }
    });

    $("#feedback").click(function () {
        if ($("#feedbackWindow").css('display') == 'none') {
            var feedbackWindow = $("#feedbackWindow");
            var feedbackWindowWidth = parseInt(feedbackWindow.css('width'));
            feedbackWindow.css('position', 'absolute')
                .css('top', $(this).offset().top + $(this).outerHeight())
                .css('left', $(this).offset().left + $(this).outerWidth() - feedbackWindowWidth)
                .slideDown(350, function () {
                    $('#feedbackContent').focus();
                });
        } else $("#feedbackWindow").slideUp(350);
        return false;
    });

    $("#feedbackClose").click(function () {
        $("#feedbackWindow").fadeOut(400);
        return false;
    });

    $("#sendFeedback").click(function () {
        var content = $("#feedbackContent").val();
        var userName;
        var userEmail;
        if ($("#feedbackUsername").length > 0) {
            userName = $("#feedbackUsername").val().replace(/^\s+|\s+$/g, '');
            //TODO: validate
        }
        if ($("#feedbackUserEmail").length > 0) {
            userEmail = $("#feedbackUserEmail").val().replace(/^\s|\s+$/g, '');
            //TODO: validate
        }
        if (content.replace(/ /g, '') == '') {
            $("#notify").showNotification("Nội dung còn trống", 3000);
        } else {
            var arg = {
                type:"POST",
                global:false,
                url:"/app/feedback/",
                data:{
                    content:content,
                    username:userName,
                    userEmail:userEmail,
                    feedback_url:window.location.href
                },
                datatype:"json",
                success:function (json) {
                    if (json.success) {
                        $("#feedbackWindow").fadeOut(400);
                        $("#notify").showNotification("Đã gửi góp ý", 3000);
                    } else {
                        $("#notify").showNotification("Không gửi được góp ý lên máy chủ", 2000);
                    }
                }
            };
            $.ajax(arg);
        }

        return false;
    });

    var url = window.location.pathname; 
    var re = RegExp('\/class\/[0-9]+\/');
    var str = String(re.exec(url));
    var class_id = String(RegExp('[0-9]+').exec(str));
    var href = $('#class-' + class_id).addClass('active');

    $(window).scroll(function () {
        if ($(window).scrollTop() > 0) {
            $(".fixed-top").css("position", "fixed");
            $(".fixed-top").css("top", "0");
        }
        if ($(window).scrollTop() <= 0) {
            $(".fixed-top").css("position", "relative");
            $(".fixed-top").css("top", $(".smartBannerIdentifier").offset);
        }
    });

});

