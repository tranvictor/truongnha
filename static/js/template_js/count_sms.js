$(document).ready(function(){
    triggerTooltip = function(){
        $(this).tooltip('show');
        return false;
    };
    $('#sms-table').delegate('.click-tooltip', 'click', triggerTooltip);

    $('#retextSms').click(function(){
        var smses = '';
        var $selecteds = $('tr.selected.failed');
        if ($selecteds.length == 0){
            $('#notify').showNotification('Bạn chưa chọn tin nhắn nào');
            return false;
        }
        for (var i= $selecteds.length; i--;){
            var smsId = $($selecteds[i]).attr('class').split(' ')[0];    
            smses += smsId + '-';
        }
        var arg = {
            data: {'smses': smses,
                'request_type': 'resend'},
            type: 'POST',
            url: '',
            success:function(json) {
                if (!json.success) {
                    $("#notify").showNotification(json.message, 10000);
                } else {
                    $("#notify").showNotification(json.message, 3000);
                }
            }
        };
        $.ajax(arg);
        return false;
    });


    var select = function() {
        var numberOfSelected;
        var $this = $(this);
        if ($this.hasClass('sms')) {
            var id = $this.attr('class').split(' ')[0];
            var $checkBoxId = $('#checkbox_' + id);
            if ($this.attr('data-status') != "failed"){
                $checkBoxId.prop("checked", false);
            } else {
                var $checkBoxAll = $('#checkbox_all');
                var n = 0;
                if ($this.hasClass('selected')) {
                    $this.removeClass('selected');
                    $checkBoxId.prop("checked", false);
                    n = $("input.studentCheckbox:checked").length;
                    if (n == 1 || n == 0) {
                        $checkBoxAll.prop("checked", false);
                    }
                } else {
                    $this.addClass('selected');
                    $checkBoxId.prop("checked", true);
                    $checkBoxAll.prop("checked", true);
                }
            }
        }
    };

    $('#sms-table').delegate('tr.failed', 'click', select);

    var selectAllSMS = function(){
        var $trs = $('tr.sms');
        for (var i = $trs.length; i--;){
            var $tr = $($trs[i]);
            if (!$tr.hasClass('selected') && $tr.attr('data-status')=="failed"){
                $tr.addClass('selected');
                var id = $tr.attr('class').split(' ')[0];
                $('#checkbox_' + id).prop("checked", true);
            }
        }
    };
    var deselectAllSMS = function(){
        var $trs = $('tr.sms');
        for (var i = $trs.length; i--;){
            var $tr = $($trs[i]);
            if ($tr.hasClass('selected')){
                $tr.removeClass('selected');
                var id = $tr.attr('class').split(' ')[0];
                $('#checkbox_' + id).prop("checked", false);
            }
        }
    };

    $("#checkbox_all").click(function() {
        if ($("#checkbox_all").is(':checked'))
            selectAllSMS();
        else deselectAllSMS();

    });

});
