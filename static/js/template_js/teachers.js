/**
 * Created by vu.tran54.
 * User: vu.tran54
 * Date: 3/3/12
 * Time: 6:47 AM
 */

$(document).ready(function() {

    $("#notify").ajaxSuccess(function(event, request, settings, json) {
        var $this = $(this);
        if (json.message != null && json.message != '' && json.message != 'OK') {
            $this.html("<ul>" + json.message + "</ul>");
            $this.delay(1000).fadeOut(10000);
        }
        else if (json.message == 'OK') {
            $this.text('Đã lưu');
            $this.delay(1000).fadeOut('fast');
            location.reload('true');
        }
    });

    $("#id_team_id").change(function(){
        var team_id = $(this).val();
        var group_select = $("#id_group_id");
        group_select.find('option.dyn').remove();
        $("option."+team_id).each(function(){
            $(this).clone().appendTo(group_select);
        });
    });
    $("#submitaddTeacher").click(function(){
        $("#submitform").submit();
    });
    $("#submitform").bind('submit', function() {
        var $this = $(this);
        var d = $this.serialize();
        d = d + '&request_type=add';
        var arg = {data: d,
            type: $this.attr('method'),
            url: $this.attr('action'),
            success:function(json) {
                if (!json.success) {
                    $("#notify").showNotification(json.message, 3000);
                    $("#id_birthday").parents("td").append(json.birthday);
                    $("#id_first_name").parents("td").append(json.first_name);
                } else {
                    $("#notify").showNotification(json.message, 3000);
                    $("#teacher_table > tbody").append(json.new_teacher);
                }
            }
        };
        $.ajax(arg);
        return false;
    });

    $("#id_sms_phone").keydown(function (event) {
        if ((event.keyCode >= 48 && event.keyCode <= 57)
            || (event.keyCode >= 96 && event.keyCode <= 105)){
        }
        else if (event.keyCode != 8 && event.keyCode != 9
            && event.keyCode != 46 && event.keyCode != 37 && event.keyCode != 39){
            event.preventDefault();
        }
    });
    $("#upload_modal").on('hidden', function(){
        location.reload('true');
    });
    $("#upload-modal-exit").click(function(){
        $("#upload_modal").modal('hide');
        return false;
    });
    $("#rename-team-modal-exit").click(function(){
        $("#rename-team-modal").modal('hide');
        return false;
    });
    $("#rename-team-form").bind('submit',function(){
        var name = $('#rename-team-input').val().replace(/^\s+|\s+$/g, '');
        if (name == ''){
            $("#notify").showNotification('Tên còn trống', 2000);
            return false;
        }
        var $parentDiv = $('#rename-team-modal');
        var id = $parentDiv.attr('data-toggle');
        var request_type = $parentDiv.attr('request-type');
        var association = $parentDiv.attr('association').replace('.', '\\\\.');
        var arg = {
            data: {
                id: id,
                name: name,
                request_type: request_type
            },
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            success:function(json) {
                if (!json.success) {
                    $("#notify").showNotification(json.message, 3000);
                } else {
                    $("#notify").showNotification(json.message, 2000);
                    $(association).html(name);
                    $parentDiv.modal('hide');
                }
            }
        };
        $.ajax(arg);
        return false;
    });

    var select = function() {
        var numberOfSelected;
        var $this = $(this);
        if ($this.hasClass('teacher')) {
            var id = $this.attr('class').split(' ')[0];
            var checkBoxId = '#checkbox_' + id;
            var checkBoxAll = '#checkbox_all';
            var n = 0;
            if ($this.hasClass('selected')) {
                $this.removeClass('selected');
                if ($this.hasClass('activated-True')){
                    $this.find('input.accountStatus').tooltip('hide');
                }
                $(checkBoxId).prop("checked", false);
                n = $("input.teacherCheckbox:checked").length;
                if (n == 0) {
                    $(checkBoxAll).prop("checked", false);
                }
                numberOfSelected = $("tr.selected").length;
                if (numberOfSelected == 0) {
                    $("#showChosenTeacher").html("Chưa chọn giáo viên nào");
                    $("#send").attr('disabled', 'disabled');
                } else {
                    $("#showChosenTeacher").html((numberOfSelected).toString() + " giáo viên");
                }
            } else {
                $this.addClass('selected');
                $(checkBoxId).prop("checked", true);
                $(checkBoxAll).prop("checked", true);
                numberOfSelected = $("tr.selected").length;
                $("#showChosenTeacher").html((numberOfSelected).toString() + " giáo viên");
                $("#send").removeAttr('disabled');
            }
        }
    };
    var delSelected = function() {
        if (!$("#checkbox_all").is(':checked')) {
            alert("Hãy chọn ít nhất một giáo viên để xoá.");
            return false;
        }
        var answer = confirm('Bạn có muốn xóa những giáo viên đã chọn không?');
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
            success: function() {
                $("#notify").showNotification("Đã xóa xong");
                //noinspection JSCheckFunctionSignatures
                location.reload('true');
            }
        };
        $.ajax(arg);
        return false;
    };
    $("#delete").click(delSelected);
    $('#teacher_table').delegate('tr.teacher', 'click', select);
    // individual listener
    var selectAllVisibleTeacher = function(){
        $("tr").each(function() {
            if (!$(this).hasClass('selected') && $(this).css('display') != 'none')
                $(this).trigger('click');
        });
    };
    var deselectAllTeacher = function(){
        $("tr").each(function() {
            if ($(this).hasClass('selected'))
                $(this).trigger('click');
        });
    };

    $("#checkbox_all").click(function() {
        if ($("#checkbox_all").is(':checked'))
            selectAllVisibleTeacher();
        else deselectAllTeacher();

    });

    $("#activateAccount").click(function(){
        if (!$("#checkbox_all").is(':checked')) {
            alert("Hãy chọn ít nhất một giáo viên để kích hoạt tài khoản.");
            return false;
        }
        var answer = confirm('Thông tin tài khoản sẽ được gửi qua Email và SMS. Hệ thống sẽ tạo lại mật khẩu cho những giáo viên đã mở tài khoản.' + ' Bạn có muốn kích hoạt tài khoản những giáo viên đã chọn không?');
        if (!answer) return false;
        var data = '';
        $(".selected").each(function() {
            if ($(this).hasClass('activated-True')){
                $(this).find('input.accountStatus').tooltip('show');
            } else {
                data = data + $(this).attr('class').split(' ')[0] + '-';
            }
        });
        $("#notify").text("Đang gửi thông tin tài khoản...");
        $("#notify").show();
        var arg = { type:"POST",
            url:"/school/activate/teacher/",
            global: false,
            data: {id_list:data},
            datatype:"json",
            success: function(data) {
                $("#notify").showNotification(data.message);
                var activated = data.activated_teacher.split('-');
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
                var alertMessage = '<ul>' + '<li>Số lượng giáo viên đã kích hoạt tài khoản: ' + data.number + '</li>';
                if (data.number_cant_contact){
                    alertMessage += '<li>Số lượng giáo viên thiếu Email hoặc số điện thoại nhắn tin: ' + data.number_cant_contact+ '</li>'
                }
                $('#alert').append( alertMessage)
                           .show()
                           .bind('close', function(){
                                deselectAllTeacher();
                            });
            }
        };
        $.ajax(arg);
        return false;
    });
    var setPosition = false;
    $(".add_teacher_button").click(function() {
//        var addTeacherWindow = $("#add-teacher-div");
//        if (!setPosition){
//            var addTeacherWindowWidth = addTeacherWindow.width();
//            var windowWidth = $(window).width();
//            addTeacherWindow.css('position', 'fixed');
//            addTeacherWindow.css('bottom', 0);
//            addTeacherWindow.css('left', windowWidth - addTeacherWindowWidth);
//            setPosition = true;
//        }
//        addTeacherWindow.slideDown(400);

        $("#teachers-nav").css('display', 'none');
        $("#teacher-list-div").removeClass('span9');
        $("#teacher-table-div").removeClass('span12').addClass('span8');
        $("#add-teacher-div").css('display', 'block');
        return true;
    });
    $(".add-teacher-exit").click(function(){
        $("#add-teacher-div").css('display', 'none');
        $("#teacher-table-div").removeClass('span8').addClass('span12');
        $("#teacher-list-div").addClass('span9');;
        $("#teachers-nav").css('display', 'block');

        $(".errorlist").remove();
        $("#id_first_name").val("");
        $("#id_birthday").val("");
        $("#id_major").val("");
        $("#id_team_id").val("");
    });
    $("#textSms").click(function() {
        // setting up layout
        if ($("#smsWindow").css('display') == 'none') {
            var buttonOffsetTop = $(this).offset().top;
            var contentWidth = parseInt($("#content").css('width'));
            var smsWindow = $("#smsWindow");
            var smsWindowWidth = parseInt(smsWindow.css('width'));
            smsWindow.css('position', 'absolute');
            smsWindow.css('top', buttonOffsetTop + 30);
            smsWindow.css('left', contentWidth - smsWindowWidth );
            smsWindow.slideDown(400);
        } else {
            $("#smsWindow").slideUp(400);
            deselectAllTeacher();
        }
    });

    $("#smsClose").click(function() {
        $("#smsWindow").fadeOut(400);
        deselectAllTeacher();
    });
    $("#send").click(function() {
        var content = $("#smsContent").val();
        var teacherList = "";
        $("tr.selected").each(function() {
            teacherList += $(this).attr('class').split(" ")[0] + "-";
        });
        if (content.replace(/ /g, '') == '') {
            $("#notify").showNotification("Nội dung còn trống");
        } else {
            var arg = { type:"POST",
                url:"",
                global: false,
                data: { content:content,
                    request_type:'send_sms',
                    teacher_list:teacherList},
                datatype:"json",
                success: function(json) {
                    if (json.message){
                        $("#notify").showNotification(json.message);
                    } else if (json.number_of_sent){
                        $("#notify").showNotification("Sẽ gửi " + json.number_of_sent + " tin nhắn trong chậm nhất 1h.");
                    }
                    $("#smsProgressbar").hide();
                    if (json.number_of_blank != '0' || json.number_of_failed != '0' || json.number_of_email_sent != '0') {
                        var html = "<ul>";
                        if (parseInt(json.number_of_blank) > 0)
                            html += "<li>" + json.number_of_blank + " giáo viên không có số điện thoại.</li>";
                        if (parseInt(json.number_of_failed) > 0)
                            html += "<li>" + json.number_of_failed + " giáo viên không gửi được tin nhắn</li>";
                        if (parseInt(json.number_of_email_sent) > 0)
                            html += "<li>" + json.number_of_email_sent + " email thay thế được gửi đến giáo viên";
                        html += "</ul>";
                        $("#smsErrorDetail").css('width', $("#smsContent").css('width'));
                        $("#smsErrorDetail").html(html).show();
                    } else {
                        deselectAllTeacher();
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
    $(document).keydown(function(e){
        if (e.which == 27 && $("#smsWindow").css('display') != 'none'){
            // press esc to close sms window
            $("#smsWindow").fadeOut(400);
            deselectAllTeacher();
        }
    });
    $(".rename-team").bind('click',function(){
        $("#rename-team-modal").attr('request-type', 'rename-team')
            .attr('data-toggle', $(this).attr('class').split(' ')[0])
            .attr('association', '#'+$(this).attr('association'));
        $('#modal-header').html('Sửa tên tổ');
        $('#input-label').html('Tên mới:');
        $('#rename-team-input').val($('#'+$(this).attr('association')).text());
        $('#rename-team-submit').val('Đổi tên');
        $('#rename-team-modal').modal('show');
    });
    $(".rename-group").bind('click', function(){
        $("#rename-team-modal").attr('request-type', 'rename-group')
            .attr('data-toggle', $(this).attr('class').split(' ')[0])
            .attr('association', '#'+$(this).attr('association'));
        $('#modal-header').html('Sửa tên nhóm');
        $('#input-label').html('Tên mới:');
        $('#rename-team-input').val($('#'+$(this).attr('association')).text());
        $('#rename-team-submit').val('Đổi tên');
        $('#rename-team-modal').modal('show');
    });
    $(".add-team").bind('click', function(){
        $("#rename-team-modal").attr('request-type', 'add-team')
            .attr('data-toggle', 'none')
            .attr('association', 'none');
        $('#modal-header').html('Thêm tổ');
        $('#input-label').html('Tên:');
        $('#rename-team-submit').val('Thêm tổ');
        $('#rename-team-modal').modal('show');
    });
    $(".add-group").bind('click', function(){
        $("#rename-team-modal").attr('request-type', 'add-group')
            .attr('data-toggle', $(this).attr('class').split(' ')[0])
            .attr('association', 'none');
        $('#modal-header').html('Thêm nhóm');
        $('#input-label').html('Tên:');
        $('#rename-team-submit').val('Thêm nhóm');
        $('#rename-team-modal').modal('show');
    });

    // recover state when browser uses it's cache
    var $inputs = $('input:checked');
    for (var i=$inputs.length; i--;){
        var trParent = $($inputs[i]).parents('tr');
        if (!trParent.hasClass('thread')) trParent.trigger('click');
    }
    // bootstrap pills filter
    var filter = function(aspect, groupValue, teamValue, clicker){
        if (aspect == 'team'){
            $('.teacher-team').each(function(){
                if ($(this).attr('data-toggle') == teamValue){
                    $(this).parents('tr.teacher').show();
                } else {
                    $(this).parents('tr.teacher').hide();
                }
            });
        } else if (aspect == 'group'){
            var value = teamValue+'-'+groupValue;
            console.log(value);
            $('tr.teacher').each(function(){
                if ( $(this).attr('data-toggle') == value){
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
        } else if (aspect == 'all'){
            $('tr.teacher').show();
        }
        if (!clicker.hasClass('active')){
            $('.active').removeClass('active');
            clicker.addClass('active');
        }
    };
    $(".team").bind('click', function(){
        filter('team', '',$(this).attr('data-toggle'), $(this));
        return false;
    });
    $(".group").bind('click', function(){
        filter('group',
                $(this).attr('data-toggle'),
                $(this).parents('li.team').attr('data-toggle'),
                $(this));
        $('div#dump').trigger('click');
        return false;
    });
    $("#team-all").click(function(){
        filter('all','', '', $(this));
        return false;
    });
    $(".remove-team").click(function(){
        var answer = confirm('Bạn có muốn xóa tổ này không?');
        if (!answer) return false;
        var id = $(this).attr('class').split(' ')[0];
        $("#notify").text("Đang xóa...");
        $("#notify").show();
        var arg = { type:"POST",
            url:"",
            global: false,
            data: {id:id, request_type:'delete_team'},
            datatype:"json",
            success: function(json) {
                $("#notify").showNotification("Đã xóa xong");
                location.reload('true');
            }
        };
        $.ajax(arg);
        return false;
    });
    $(".remove-group").click(function(){
        var answer = confirm('Bạn có muốn xóa nhóm này không?');
        if (!answer) return false;
        var id = $(this).attr('class').split(' ')[0];
        $("#notify").text("Đang xóa...");
        $("#notify").show();
        var arg = { type:"POST",
            url:"",
            global: false,
            data: {id:id, request_type:'delete_group'},
            datatype:"json",
            success: function(json) {
                $("#notify").showNotification("Đã xóa xong");
                location.reload('true');
            }
        };
        $.ajax(arg);
        return false;
    });
});

