$(document).ready(function(){
    $(".accountInfo").hide();
    $("#tableFunction").css('width', $("#registerTable").css('width'));
    var select = function() {
        var numberOfSelected;
        if (!$(this).hasClass('thread') && !$(this).hasClass('form') && !$(this).hasClass('function')) {
            var id = $(this).attr('class').split(' ')[0];
            var checkboxid = '#checkbox_' + id;
            var checkboxall = '#checkbox_all';
            if ($(this).hasClass('selected')) {
                $(this).removeClass('selected');
                $(checkboxid).prop("checked", false);
                var n = $("input.registerCheckbox:checked").length;
                if (n == 1 || n==0) {
                    $(checkboxall).prop("checked", false);
                }
                numberOfSelected = $("tr.selected").length;
                if (numberOfSelected == 0) {
                    $("#showChosenRegister").html("Chưa chọn đăng ký nào");
                    $("#send").attr('disabled', 'disabled');
                } else {
                    $("#showChosenRegister").html((numberOfSelected).toString() + " đăng ký");
                }
            } else {
                $(this).addClass('selected');
                $(checkboxid).prop("checked", true);
                $(checkboxall).prop("checked", true);
                numberOfSelected = $("tr.selected").length;
                $("#showChosenRegister").html((numberOfSelected).toString() + " đăng ký");
                $("#send").removeAttr('disabled');
            }
        }
    };
    $("tr.register").each(function() {
        $(this).click(select);
    });
    $("#checkbox_all").click(function() {
        var checkboxall = '#checkbox_all';
        if ($(checkboxall).is(':checked')) {
            $("tr.register").each(function() {
                var id = $(this).attr('class').split(' ')[0];
                var checkboxid = '#checkbox_' + id;
                if (!$(this).hasClass('selected'))
                    $(this).trigger('click');
            });
        }
        else {
            $("tr.register").each(function() {
                var id = $(this).attr('class').split(' ')[0];
                var checkboxid = '#checkbox_' + id;
                if ($(this).hasClass('selected'))
                    $(this).trigger('click');
            });
        }
    });

    var delSelected = function() {
        if (!$("#checkbox_all").is(':checked')) {
            alert("Bạn chưa chọn đăng ký nào để xóa");
            return false;
        }
        var answer = confirm('Bạn có muốn xóa những đăng ký đã chọn không?');
        if (!answer) return false;
        var data = '';
        $(".selected").each(function() {
            data = data + $(this).attr('class').split(' ')[0] + '-';
        });
        $("#notify").text("Đang xóa...");
        $("#notify").show();
        var arg = { type:"POST",
            url:"",
            global: false,
            data: {data:data, request_type:'del'},
            datatype:"json",
            success: function(json) {
                if (json.success){
                    $("#notify").showNotification("Đã xóa xong");
                    location.reload('true');
                } else {
                    $("#notify").showNotification(json.message);
                }

            }
        };
        $.ajax(arg);
        return false;
    };
    $("#delSelected").click(delSelected);
    $("#createSelected").click(function(){
         if (!$("#checkbox_all").is(':checked')) {
            alert("Bạn chưa chọn đăng ký nào để tạo tài khoản");
            return false;
        }
        var data = '';
        $(".selected").each(function() {
            data = data + $(this).attr('class').split(' ')[0] + '-';
        });
        $("#notify").text("Đang tạo tài khoản...");
        $("#notify").show();
        var arg = { type:"POST",
            url:"",
            global: false,
            data: {data:data, request_type:'create_acc'},
            datatype:"json",
            success: function(json) {
                if (json.success){
                    $("#notify").showNotification(json.message);
                    var accounts = json.account_info;
                    accounts = accounts.split(',');
                    for ( var i=0; i< accounts.length; i++){
                        account = accounts[i];
                        if ( account != ""){
                            var id = account.split('-')[0];
                            var username = account.split('-')[1];
                            var password = account.split('-')[2];
                            var theTr = $("."+id);
                            if (theTr.find('td.username').length){
                                theTr.find('td.username').text(username);
                                theTr.find('td.password').text(username);
                            } else {
                                theTr.append('<td class="username" style="padding-left: 4px;">'+username+'</td>');
                                theTr.append('<td class="password" style="padding-left: 4px;">'+password+'</td>');
                            }
                            theTr.find('td.status').text("Đã cấp");
                        }
                    }
                    $(".accountInfo").show();
                    $("#tableFunction").css('width', $("#registerTable").css('width'));
                } else {
                    $("#notify").showNotification(json.message);
                }
            }
        };
        $.ajax(arg);
        return false;
    });

    // show registered
    $("#showRegistered").click(function(){
        if ($(this).text() == "Ẩn đăng ký đã cấp"){
            $(".status").each(function(){
                if ($(this).text() == "Đã cấp"){
                    $(this).parent().hide();
                }
            });
            $(this).text("Hiện đăng ký đã cấp");
            var numberOfUnregistered = 0;
            $(".status").each(function(){
                if ($(this).text() == "Chưa cấp") numberOfUnregistered ++;
            });
            if (!numberOfUnregistered){
                $("thead").hide();
                jQuery('<p id="noRegisterLeft">Không có đăng ký nào chưa cấp tài khoản.</p>').insertAfter($('#registerTable'));
            }
        }else {
            $("#noRegisterLeft").remove();
            $("thead").show();
            $(".status").each(function(){
                if ($(this).text() == "Đã cấp"){
                    $(this).parent().show();
                }
            });
            $(this).text("Ẩn đăng ký đã cấp");

        }
    });

    var $document = $(document);
    var deselectAllRegister = function(){
        var $trs = $('tr.register');
        for ( var i = $trs.length; i--;){
            var $tr = $($trs[i]);
            if ($tr.hasClass('selected')){
                $tr.removeClass('selected');
                var id = $tr.attr('class').split(' ')[0];
                $('#checkbox_' + id).prop("checked", false);
            }
        }
        $('#checkbox_all').prop("checked", false);
        $("#showChosenRegister").html("Chưa chọn đăng ký nào");
        $("#send").attr('disabled', 'disabled');
    };

    $("#textSms").click(function() {
        // setting up layout
        if ($("#smsWindow").css('display') == 'none') {
            var buttonOffsetTop = $(this).offset().top;
            var contentWidth = parseInt($("#content").css('width'));
            var smsWindow = $("#smsWindow");
            var smsWindowWidth = parseInt(smsWindow.css('width'));
            smsWindow.css('position', 'absolute')
                .css('top', buttonOffsetTop + 30)
                .css('left', contentWidth - smsWindowWidth )
                .slideDown(400);
        } else {
            $("#smsWindow").slideUp(400);
            deselectAllRegister();
        }
    });
    $("#smsClose").click(function() {
        $("#smsWindow").fadeOut(400);
        deselectAllRegister();
    });
    $("#send").click(function() {
        var content = $("#smsContent").val();
        var registerList = "";
        $("tr.selected").each(function() {
            registerList += $(this).attr('class').split(" ")[0] + "-";
        });
        if (content.replace(/ /g, '') == '') {
            $("#notify").showNotification("Nội dung còn trống");
        } else {
            //noinspection JSUnusedGlobalSymbols
            var arg = { type:"POST",
                url:"",
                global: false,
                data: { content:content,
                    request_type:'send_email',
                    register_list:registerList},
                datatype:"json",
                success: function(json) {
                    if (json.message){
                        $("#notify").showNotification(json.message);
                    $("#smsProgressbar").hide();
                    deselectAllRegister();
                    $("#smsWindow").fadeOut(300);
                    }
                },
                error: function() {
                    $("#notify").showNotification("Gặp lỗi khi gửi tin nhắn");
                    $("#smsProgressbar").hide();
                }
            };
            $("#smsProgressbar").css('width', $("#smsContent").css('width'));
            $("#smsProgressbar").show();
            $.ajax(arg);
        }

        return false;
    });

    // key function
    $document.keydown(function(e){
        if (e.which == 27 && $("#smsWindow").css('display') != 'none'){
            // press esc to close sms window
            $("#smsWindow").fadeOut(400);
            deselectAllRegister();
        }
    });

});