$(document).ready(function () {

    var $document = $(document);
    $("#notify").ajaxSuccess(function(event, request, settings, json) {
        var $this = $(this);
        if (json.message != null && json.message != '' && json.message != 'OK') {
            $this.html("<ul>" + json.message + "</ul>");
            $this.delay(1000).fadeOut(10000);
        }
        else if (json.message == 'OK') {
            $this.text('Đã lưu');
            $this.delay(1000).fadeOut('fast');
            //noinspection JSCheckFunctionSignatures
            location.reload('true');
        }
    });

    $('#send-sms').click(function(){
        var students = '';
        var $selecteds = $('tr.selected.student');
        if ($selecteds.length == 0){
            $('#notify').showNotification('Bạn chưa chọn học sinh nào');
            return false;
        }
        for (var i= $selecteds.length; i--;){
            var stId = $($selecteds[i]).attr('class').split(' ')[0];    
            students += stId + '-';
        }
        var arg = {
            data: { 'students': students,
                    'request_type': 'send'},
            type: 'POST',
            url: '',
            success:function(json) {
                if (!json.success) {
                    $("#notify").showNotification(json.message, 10000);
                } else {
                }
            }
        };
        $.ajax(arg);
        return false;
    });

    var select = function() {
        var numberOfSelected;
        var $this = $(this);
        if ($this.hasClass('student')) {
            var id = $this.attr('class').split(' ')[0];
            var $checkBoxId = $('#checkbox_' + id);
            if ($this.attr('data-contact') == " "){
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

    $('#student-table').delegate('tr', 'click', select);

    var selectAllStudent = function(){
        var $trs = $('tr.student');
        for (var i = $trs.length; i--;){
            var $tr = $($trs[i]);
            if (!$tr.hasClass('selected') && $tr.attr('data-contact')!=" "){
                $tr.addClass('selected');
                var id = $tr.attr('class').split(' ')[0];
                $('#checkbox_' + id).prop("checked", true);
            }
        }
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
    };

    $("#checkbox_all").click(function() {
        if ($("#checkbox_all").is(':checked'))
            selectAllStudent();
        else deselectAllStudent();

    });

    var $tds = $('td');
    for (var i = $tds.length; i--;){
        var $this = $($tds[i]);
        if ($this.css('display') != 'none'){
            $this.css('width', parseInt($this.css('width')));
        }
    }

   // recover state when browser uses it's cache
    var checkedInput = $('table').find('input:checked');
    for (var i = checkedInput.length; i--;){
        var trParent = $(checkedInput[i]).parents('tr');
        if (!trParent.hasClass('thread')) trParent.trigger('click');
    }
});
