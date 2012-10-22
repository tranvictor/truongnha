$(document).ready(function() {

    var $document = $(document);
    $("#notify").ajaxSuccess(function(event, request, settings, json) {
        if (json.message != null && json.message != '' && json.message != 'OK') {
            $(this).html("<ul>" + json.message + "</ul>");
            $(this).delay(10000).fadeOut('fast');
        }
        else if (json.message == 'OK') {
            $(this).text('Đã lưu');
            $(this).delay(2000).fadeOut('fast');
            //noinspection JSCheckFunctionSignatures
            location.reload('true');
        }
    });

    $("#upload_modal").on('hidden', function(){
        location.reload('true');
    });

    $("#upload-modal-exit").click(function(){
        $("#upload_modal").modal('hide');
        return false;
    });
    $("#move-modal-exit").click(function(){
        $("#move_modal").modal('hide');
        return false;
    });

    var $manualAddStudent = $(".manualAddStudent");
    $manualAddStudent.click(function(){
        var $addStudentForm = $("#addStudentForm");
        if ($addStudentForm.css('display') == 'none'){
            $addStudentForm.fadeIn(300);
            $manualAddStudent.text('Thôi thêm');
            $document.scrollTop(100000000);
        } else {
            $addStudentForm.fadeOut(300);
            $manualAddStudent.html('<i class="icon-plus"></i>Thêm');
        }
    });

    $("#move-submit").click(function(){
        var $this = $(this);
        var self = $this.parents('tr');
        var $selecteds = $(".selected");
        if ($selecteds.length == 0){
            $("#notify").showNotification("Bạn chưa chọn học sinh nào.");
            return false;
        }
        var moveToClId = $("#move_to_class_id").val();
        var d = '';
        for (var i=$selecteds.length; i--;){
            d += $($selecteds[i]).attr('class').split(' ')[0] + '-';
        }
        var arg = {
            data: {
                data: d,
                request_type: 'move',
                target: moveToClId
            },
            type: 'POST',
            url: '/school/movestudents',
            error: function(){
                $("#notify").showNotification("Có lỗi xảy ra.");
            },
            success: function() {
                $("#notify").showNotification("Đã chuyển xong.");
                $(".selected").remove();
                $("#checkbox_all").prop("checked",false);
            }
        };
        $.ajax(arg);
        return false;
    });

    $("#submitform").bind('submit', function() {
        var $this = $(this);
        var d = $this.serialize();
        d = d + '&request_type=add';
        var self = $this.parents('tr');
        var arg = {data: d,
            type: $this.attr('method'),
            url: $this.attr('action'),
            success:function(json) {
                if (!json.success) {
                    $("#notify").showNotification(json.message, 3000);
                } else {
                    $.ajaxSetup({
                        global: false
                    });
                    $("#student-table > tbody").append(json.student_detail);
                    var $forms = $("#submitform");
                    $forms.find('input:text').val('');
                    $forms.find('input#id_dan_toc').val('Kinh');
                    $("#notify").showNotification(json.message);
                }
            }
        };
        $.ajax(arg);
        return false;
    });

    $("#id_sms_phone").keydown(function (event) {
        if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode >= 96 && event.keyCode <= 105)) // 0-9 or numpad 0-9
        {
// check textbox value now and tab over if necessary
        }
        else if (event.keyCode != 8 && event.keyCode != 9 && event.keyCode != 46 && event.keyCode != 37 && event.keyCode != 39) // not esc, del, left or right
        {
            event.preventDefault();
        }
// else the key should be handled normally
    });

    var select = function() {
        var numberOfSelected;
        var $this = $(this);
        if ($this.hasClass('student')) {
            var id = $this.attr('class').split(' ')[0];
            var checkBoxId = '#checkbox_' + id;
            var checkBoxAll = '#checkbox_all';
            var n = 0;
            if ($this.hasClass('selected')) {
                $this.removeClass('selected');
                $(checkBoxId).prop("checked", false);
                n = $("input.studentCheckbox:checked").length;
                if (n == 1 || n == 0) {
                    $(checkBoxAll).prop("checked", false);
                }
                numberOfSelected = $("tr.selected").length;
                if (numberOfSelected == 0) {
                    $("#showChosenStudent").html("Chưa chọn học sinh nào");
                    $("#send").attr('disabled', 'disabled');
                } else {
                    $("#showChosenStudent").html((numberOfSelected).toString() + " học sinh");
                }
            } else {
                $this.addClass('selected');
                $(checkBoxId).prop("checked", true);
                $(checkBoxAll).prop("checked", true);
                numberOfSelected = $("tr.selected").length;
                $("#showChosenStudent").html((numberOfSelected).toString() + " học sinh");
                $("#send").removeAttr('disabled');
            }
        }
    };
    var delSelected = function() {
        if (!$("#checkbox_all").is(':checked')) {
            alert("Hãy chọn ít nhất một học sinh để xoá.");
            return false;
        }
        var answer = confirm('Bạn có muốn xóa những học sinh đã chọn không?');
        if (!answer) return false;
        var data = '';
        var $selected = $(".selected");
        for ( var i = $selected.length; i--;){
            data += $($selected[i]).attr('class').split(' ')[0] + '-';
        }
        var $notify = $("#notify").text("Đang xóa...").show();
        var arg = { type:"POST",
            url:"",
            global: false,
            data: {data:data, request_type:'del'},
            datatype:"json",
            success: function() {
                $notify.showNotification("Đã xóa xong");
                location.reload('true');
            }
        };
        $.ajax(arg);
        return false;
    };
    $("#delSelected").click(delSelected);

    $('#student-table').delegate('tr', 'click', select);
    // individual listener
    var selectAllStudent = function(){
        var $trs = $('tr.student');
        for (var i = $trs.length; i--;){
            var $tr = $($trs[i]);
            if (!$tr.hasClass('selected')){
                $tr.addClass('selected');
                var id = $tr.attr('class').split(' ')[0];
                $('#checkbox_' + id).prop("checked", true);
            }
        }
        $('#checkbox_all').prop("checked", true);
        $("#showChosenStudent").html(($trs.length).toString() + " học sinh");
        $("#send").removeAttr('disabled');
    };
    var deselectAllStudent = function(){
        var $trs = $('tr.student');
        for ( var i = $trs.length; i--;){
            var $tr = $($trs[i]);
            if ($tr.hasClass('selected')){
                $tr.removeClass('selected');
                var id = $tr.attr('class').split(' ')[0];
                $('#checkbox_' + id).prop("checked", false);
            }
        }
        $('#checkbox_all').prop("checked", false);
        $("#showChosenStudent").html("Chưa chọn học sinh nào");
        $("#send").attr('disabled', 'disabled');
    };

    $("#checkbox_all").click(function() {
        if ($("#checkbox_all").is(':checked'))
            selectAllStudent();
        else deselectAllStudent();

    });

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
            deselectAllStudent();
        }
    });
    $("#smsClose").click(function() {
        $("#smsWindow").fadeOut(400);
        deselectAllStudent();
    });
    $("#send").click(function() {
        var content = $("#smsContent").val();
        var studentList = "";
        $("tr.selected").each(function() {
            studentList += $(this).attr('class').split(" ")[0] + "-";
        });
        if (content.replace(/ /g, '') == '') {
            $("#notify").showNotification("Nội dung còn trống");
        } else {
            //noinspection JSUnusedGlobalSymbols
            var arg = { type:"POST",
                url:"",
                global: false,
                data: { content:content,
                    request_type:'send_sms',
                    include_name: $("#includeStudentName").is(':checked'),
                    student_list:studentList},
                datatype:"json",
                success: function(json) {
                    $("#notify").showNotification("Sẽ gửi " + json.number_of_sent + " tin nhắn trong chậm nhất 1h.");
                    $("#smsProgressbar").hide();
                    if (json.number_of_blank != '0' || json.number_of_failed != '0' || json.number_of_email_sent != '0') {
                        var html = "<ul>";
                        if (parseInt(json.number_of_blank) > 0)
                            html += "<li>" + json.number_of_blank + " học sinh không có số điện thoại.</li>";
                        if (parseInt(json.number_of_failed) > 0)
                            html += "<li>" + json.number_of_failed + " học sinh không gửi được tin nhắn</li>";
                        if (parseInt(json.number_of_email_sent) > 0)
                            html += "<li>" + json.number_of_email_sent + " email thay thế được gửi tới học sinh</li>";
                        html += "</ul>";
                        $("#smsErrorDetail").css('width', $("#smsContent").css('width'));
                        $("#smsErrorDetail").html(html).show();
                    } else {
                        deselectAllStudent();
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
            deselectAllStudent();
        }
    });
    // recover state when browser uses it's cache
    var checkedInput = $('table').find('input:checked');
    for (var i = checkedInput.length; i--;){
        var trParent = $(checkedInput[i]).parents('tr');
        if (!trParent.hasClass('thread')) trParent.trigger('click');
    }
    var setPosition = false;
    $("#add-student").click(function() {
        $("#student-table-div")
            .removeClass('span12')
            .addClass('span8');
        $("#add-student-div").css('display', 'block');

    });
    $("#add-student-cancel").click(function(){
        $("#add-student-div")
            .fadeOut(400)
            .css('display', 'none');

        $("#student-table-div")
            .removeClass('span8')
            .addClass('span12');

        $("#submitform").find("input").val("");

    });
    $("#add-student-submit").click(function(){
        $("#submitform").submit();
    });
    $("#activateAccount").click(function(){
        if (!$("#checkbox_all").is(':checked')) {
            alert("Hãy chọn ít nhất một học sinh để kích hoạt tài khoản.");
            return false;
        }
        var answer = confirm('Thông tin tài khoản sẽ được gửi qua Email và SMS. Hệ thống sẽ tạo lại mật khẩu' +
            ' cho những học sinh đã mở tài khoản.' + ' Bạn có muốn kích hoạt tài khoản những học sinh' +
            ' đã chọn không?');
        if (!answer) return false;
        var data = '';
        $(".selected").each(function() {
            data = data + $(this).attr('class').split(' ')[0] + '-';
        });
        $("#notify").text("Đang gửi thông tin tài khoản...");
        $("#notify").show();
        var arg = { type:"POST",
            url:"/school/activate/student/",
            global: false,
            data: {id_list:data},
            datatype:"json",
            success: function(data) {
                $("#notify").showNotification(data.message);
                var activated = data.activated_student.split('-');
                for (var i=0; i< activated.length; i++){
                    if (activated[i] != ''){
                        $('#lock-'+ activated[i]).removeClass('icon-lock').addClass('icon-key');
                    }
                }
                $('div#after-post-alert').html(
                    '<div id="alert" class="alert alert-block alert-error fade in" style="display: none;">' +
                        '<a class="close" data-dismiss="alert" href="#">×</a>' +
                        '</div>'
                );
                var alertMessage = '<ul>' + '<li>Số lượng học sinh đã kích hoạt tài khoản: ' + data.number + '</li>';
                if (data.number_cant_contact){
                    alertMessage += '<li>Số lượng học sinh thiếu Email hoặc số điện thoại nhắn tin: ' + data.number_cant_contact+ '</li>'
                }
                $('#alert').append( alertMessage)
                    .show()
                    .bind('close', function(){
                        deselectAllStudent();
                    });
            }
        };
        $.ajax(arg);
        return false;
    });
    $("#deactivateAccount").click(function(){
        if (!$("#checkbox_all").is(':checked')) {
            alert("Hãy chọn ít nhất một học sinh để khóa tài khoản.");
            return false;
        }
        var answer = confirm('Những tài khoản bị khóa sẽ không thể tiếp tục sử dụng hệ thống.' +
            ' Bạn có muốn khóa tài khoản những học sinh đã chọn không?');
        if (!answer) return false;
        var data = '';
        $(".selected").each(function() {
            data = data + $(this).attr('class').split(' ')[0] + '-';
        });
        $("#notify").text("Đang gửi thông tin tài khoản...");
        $("#notify").show();
        var arg = { type:"POST",
            url:"/school/deactivate/student/",
            global: false,
            data: {id_list:data},
            datatype:"json",
            success: function(data) {
                $("#notify").showNotification(data.message);
                var activated = data.deactivated_student.split('-');
                for (var i=0; i< activated.length; i++){
                    if (activated[i] != ''){
                        $('#lock-'+ activated[i]).removeClass('icon-key').addClass('icon-lock');
                    }
                }
            }
        };
        $.ajax(arg);
        return false;
    });
});


