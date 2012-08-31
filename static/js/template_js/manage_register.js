$(document).ready(function(){
    $(".accountInfo").hide();
    $("#tableFunction").css('width', $("#registerTable").css('width'));
    var select = function() {
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
            } else {
                $(this).addClass('selected');
                $(checkboxid).prop("checked", true);
                $(checkboxall).prop("checked", true);
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
                $("tr.thread").hide();
                jQuery('<p id="noRegisterLeft">Không có đăng ký nào chưa cấp tài khoản.</p>').insertAfter($('#tableFunction'));
            }
        }else {
            $("#noRegisterLeft").remove();
            $("tr.thread").show();
            $(".status").each(function(){
                if ($(this).text() == "Đã cấp"){
                    $(this).parent().show();
                }
            });
            $(this).text("Ẩn đăng ký đã cấp");

        }
    })

});