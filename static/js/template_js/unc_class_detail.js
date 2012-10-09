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
    $('#classify').click(function (){
        var $selecteds = $('tr.selected');
        if ($selecteds.length == 0) {
            $("#notify").showNotification('Bạn chưa chọn học sinh nào');
        } else {
            $('#classify-modal').modal('show');
        }
    });
    $("#classify-modal-exit").click(function(){
        $("#classify-modal").modal('hide');
        return false;
    });

    $('#graduate').click(function(){
        var students = '';
        var $selecteds = $('tr.selected');
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
                    'request_type': 'graduate'},
            type: 'POST',
            url: '',
            success:function(json) {
                if (!json.success) {
                    $("#notify").showNotification(json.message, 3000);
                } else {
                    location.reload('true');
                }
            }
        };
        $.ajax(arg);
        return false;
    });
    $('#submit').click(function(){
        var classId = $('#class_id').val(); 
        var students = '';
        var $selecteds = $('tr.selected');
        if ($selecteds.length == 0){
            $('#notify').showNotification('Bạn chưa chọn học sinh nào');
            return false;
        }
        for (var i= $selecteds.length; i--;){
            var stId = $($selecteds[i]).attr('class').split(' ')[0];    
            console.log(stId);
            students += stId + '-';
        }
        var arg = {
            data: { 'students': students,
                    'class_id': classId,
                    'request_type': 'classify'
                    },
            type: 'POST',
            url: '',
            success:function(json) {
                if (!json.success) {
                    $("#notify").showNotification(json.message, 3000);
                } else {
                    location.reload('true');
                }
            }
        };
        $.ajax(arg);
        return false;
    });
    var select = function() {
        var numberOfSelected;
        var $this = $(this);
        var $classify = $('#classify');
        var $clModal = $('#classify-modal');
        if ($this.hasClass('student')) {
            var id = $this.attr('class').split(' ')[0];
            var $checkBoxId = $('#checkbox_' + id);
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
    };

    $('#student-table').delegate('tr', 'click', select);

    var selectAllStudent = function(){
        var $trs = $('tr');
        for (var i = $trs.length; i--;){
            var $tr = $($trs[i]);
            if (!$tr.hasClass('selected')) $tr.trigger('click');
        }
    };
    var deselectAllStudent = function(){
        var $trs = $('tr');
        for ( var i = $trs.length; i--;){
            var $tr = $($trs[i]);
            if ($tr.hasClass('selected')) $tr.trigger('click');
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

    // key function
    $document.keydown(function(e){
        if (e.which == 27 && $("#classifyWindow").css('display') != 'none'){
            // press esc to close sms window
            deselectAllStudent();
            $("#classifyWindow").fadeOut(400);
        }
    });
    // recover state when browser uses it's cache
    var checkedInput = $('table').find('input:checked');
    for (var i = checkedInput.length; i--;){
        var trParent = $(checkedInput[i]).parents('tr');
        if (!trParent.hasClass('thread')) trParent.trigger('click');
    }
});


