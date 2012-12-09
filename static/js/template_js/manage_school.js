$(document).ready(function(){
    $(".accountInfo").hide();
    $("#schoolTable").css('width', $("#schoolTable").css('width'));
    var select = function() {
        if (!$(this).hasClass('thread') && !$(this).hasClass('form') && !$(this).hasClass('function')) {
            var id = $(this).attr('class').split(' ')[0];
            var checkboxid = '#checkbox_' + id;
            var checkboxall = '#checkbox_all';
            if ($(this).hasClass('selected')) {
                $(this).removeClass('selected');
                $(checkboxid).prop("checked", false);
                var n = $("input.schoolCheckbox:checked").length;
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
    $("tr.school").each(function() {
        $(this).click(select);
    });
    $("#checkbox_all").click(function() {
        var checkboxall = '#checkbox_all';
        if ($(checkboxall).is(':checked')) {
            $("tr.school").each(function() {
                var id = $(this).attr('class').split(' ')[0];
                var checkboxid = '#checkbox_' + id;
                if (!$(this).hasClass('selected'))
                    $(this).trigger('click');
            });
        }
        else {
            $("tr.school").each(function() {
                var id = $(this).attr('class').split(' ')[0];
                var checkboxid = '#checkbox_' + id;
                if ($(this).hasClass('selected'))
                    $(this).trigger('click');
            });
        }
    });

    var delSelected = function() {
        if (!$("#checkbox_all").is(':checked')) {
            alert("Bạn chưa chọn trường nào để xóa");
            return false;
        }
        var answer = confirm('Bạn có muốn xóa những trường đã chọn không?');
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
    $("#ActivateSelected").click(function(){
         if (!$("#checkbox_all").is(':checked')) {
            alert("Bạn chưa chọn trường nào để kích hoạt");
            return false;
        }
        var data = '';
        $(".selected").each(function() {
            data = data + $(this).attr('class').split(' ')[0] + '-';
        });
        $("#notify").text("Đang kích hoạt các trường...");
        $("#notify").show();
        var arg = { type:"POST",
            url:"",
            global: false,
            data: {data:data, request_type:'activate_school'},
            datatype:"json",
            success: function(json) {
                if (json.success){
                    $("#notify").showNotification(json.message);
                    var schools = json.schools;
                    schools = schools.split(',');
                    for ( var i=0; i< schools.length; i++){
                        var id = schools[i];
                        var theTr = $("."+id);
                        theTr.find('td.status').text("Đã kích hoạt");
                        }
                } else {
                    $("#notify").showNotification(json.message);
                }
            }
        };
        $.ajax(arg);
        return false;
    });
    //deactivate
    $("#DeactivateSelected").click(function(){
        if (!$("#checkbox_all").is(':checked')) {
            alert("Bạn chưa chọn trường nào để khóa");
            return false;
        }
        var data = '';
        $(".selected").each(function() {
            data = data + $(this).attr('class').split(' ')[0] + '-';
        });
        $("#notify").text("Đang khóa các trường...");
        $("#notify").show();
        var arg = { type:"POST",
            url:"",
            global: false,
            data: {data:data, request_type:'deactivate_school'},
            datatype:"json",
            success: function(json) {
                if (json.success){
                    $("#notify").showNotification(json.message);
                    var schools = json.schools;
                    schools = schools.split(',');
                    for ( var i=0; i< schools.length; i++){
                        var id = schools[i];
                        var theTr = $("."+id);
                        theTr.find('td.status').text("Đã khóa");
                    }
                } else {
                    $("#notify").showNotification(json.message);
                }
            }
        };
        $.ajax(arg);
        return false;
    });

    // show Activated
    $("#showActivated").click(function(){
        if ($(this).text() == "Ẩn các trường đã khóa"){
            $(".status").each(function(){
                if ($(this).text() == "Đã khóa"){
                    $(this).parent().hide();
                }
            });
            $(this).text("Hiện các trường đã khóa");
            var numberOfActivated = 0;
            $(".status").each(function(){
                if ($(this).text() == "Đã kích hoạt") numberOfActivated ++;
            });
            if (!numberOfActivated){
                $("thead").hide();
                jQuery('<p id="noSchoolLeft">Không có trường nào đang được kích hoạt.</p>').insertAfter($('#schoolTable'));
            }
        }else {
            $("#noSchoolLeft").remove();
            $("thead").show();
            $(".status").each(function(){
                if ($(this).text() == "Đã khóa"){
                    $(this).parent().show();
                }
            });
            $(this).text("Ẩn các trường đã khóa");
        }
    })

});