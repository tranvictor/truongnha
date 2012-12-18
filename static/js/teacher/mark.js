$(document).ready(function(){
    var edit_hs = false;
    function acceptDigits(val){
        var exp = /[^((\d).,)]/g;
        val=val.replace(exp,'');

        var exp1 = /[,]/g;
        val=val.replace(exp1,'.');
        if(isNaN(val)) return '';
        var countDot=0;
        for(var i=0;i<val.length;i++)
            if (val.charAt(i)==".")
                countDot++;

        if (countDot>1)
            val=val.substring(0,value.length-1);

        if (val.length>4)
            val=val.substring(0,4);

        var number=parseFloat(val);
        if ((10<number ) && (number<100))
        {
            var temp=number/10;
            val=temp.toString();
        }
        if (number>=100)
            val=val.substring(0,2);
        if ((val.length==2) && (val[0]=='0'))
        {
            var temp = number / 10;
            val = temp.toString();
        }
        return val;
    }
    function acceptDigitsHs(val){
        var exp = /[^((\d).,)]/g;
        val=val.replace(exp,'');
        var exp1 = /[,]/g;
        val=val.replace(exp1,'.');
        if(isNaN(val)) return '';
        return val;
    }
    function key_up_diem(event) {
        var $this;
        var cellIndex;
        if (event.keyCode == 37) {
            $this = $(this).parents("tr");
            cellIndex = $(this).parent("td").index() - 1;
            $this.children().eq(cellIndex).find("input").focus();
            return false;
        }
        if (event.keyCode == 38) {
            $this = $(this).parent("td");
            cellIndex = $this.index();
            $this.closest('tr').prev().children().eq(cellIndex).find("input").focus();
            return false;
        }
        if (event.keyCode == 39) {
            $this = $(this).parents("tr");
            cellIndex = $(this).parent("td").index() + 1;
            $this.children().eq(cellIndex).find("input").focus();
            return false;
        }
        if (event.keyCode == 40 || event.keyCode == 13) {
            $this = $(this).parent("td");
            cellIndex = $this.index();
            $this.closest('tr').next().children().eq(cellIndex).find("input").focus();
            return false;
        }
        var val = $(this).val();
        val = acceptDigits(val);
        $(this).val(val);
    }
    function key_up_heso(event){
        var $this;
        var cellIndex;
        if (event.keyCode == 37) {
            $this = $(this).parents("tr");
            cellIndex = $(this).parent("th").index() - 1;
            $this.children().eq(cellIndex).find("input").focus();
            return false;
        }
        if (event.keyCode == 39) {
            $this = $(this).parents("tr");
            cellIndex = $(this).parent("th").index() + 1;
            $this.children().eq(cellIndex).find("input").focus();
            return false;
        }
        var val = $(this).val();
        val = acceptDigitsHs(val);
        $(this).val(val);
    }
    function add_he_so(){
        clear_bootstrap_error();
        var value = $("#id_hs").val();
        var url = '/teacher/' + teacher_id + '/class/' + class_id + '/heso/create';
        var args = {
            type:'POST',
            'url':url,
            'global':false,
            'data':{
                'hs':value
            },
            datatype:"json",
            success: function(json){
                $("#notify").showNotification(json.message);
                if(json.success){
                    add_new_column(json.heso,value);
                    $("#add-column-modal").modal("hide");
                }
                else{
                    add_bootstrap_error(json.error);
                }
            }
        }
        $.ajax(args);
        return false;
    }
    function edit_he_so() {
        var value = $(this).val();
        var old_value = $(this).attr('data-heso');
        var cl = $(this).parent().attr('class');
        var $input = $(this);
        var tem1 = parseFloat(value);
        var tem2 = parseFloat(old_value);
        if ((tem1 == tem2 ) || (isNaN(tem1) && isNaN(tem2))) return false;
        if (value == '') {
            var i = confirm('Bạn có chắc chắn muốn xóa cột điểm này không?');
            if (i){
                var url = '/teacher/' + teacher_id + '/class/' + class_id +
                    '/heso/' + cl + '/remove';
                var args = {
                    type:'POST',
                    'url':url,
                    'global':false,
                    'data':{},
                    datatype:"json",
                    success:function (json) {
                        $("#notify").showNotification(json.message);
                        if (json.success) {
                            var selected = '.' + cl;
                            $(selected).remove();
                        }
                    }
                };
            }
            else{
                $(this).val(old_value);
                return false;
            }
        }
        else {
            var url = '/teacher/' + teacher_id + '/class/' + class_id +
                '/heso/' + cl + '/modify';
            var args = {
                type:'POST',
                'url':url,
                'global':false,
                'data':{
                    'hs':value
                },
                datatype:"json",
                success:function (json) {
                    if (json.success) {
                        $("#notify").showNotification('Đã lưu.');
                        $input.attr('data-heso', value);
                    }
                    else $("#notify").showNotification(json.message);
                }
            };
        }
        $.ajax(args);
    }
    function edit_mark(){
        var std_info = $(this).parent().parent().attr('id').split('-');
        var student_id = std_info[1];
        var cl = $(this).parent().attr('class');
        var value = $(this).val();
        var old_value = $(this).attr('data-diem');
        var $input = $(this);
        var tem1 = parseFloat(old_value);
        var tem2 = parseFloat(value);
        if((tem1 == tem2 )||(isNaN(tem1)&&isNaN(tem2))) return false;
        if ($(this).hasClass('old-mark')){
            var mark_id = $(this).attr('id');
            if (value == ''){
                var url = '/teacher/' + teacher_id + '/class/' + class_id +
                    '/student/' + student_id + '/heso/' + cl +
                    '/mark/' + mark_id + '/remove';
                var args = {
                    type:'POST',
                    'url':url,
                    'global':false,
                    'data':{},
                    datatype:"json",
                    success: function(json){
                        if(json.success){
                            $("#notify").showNotification('Đã lưu');
                            $input.removeClass('old-mark');
                            $input.attr('data-diem',value);
                        }
                        else $("#notify").showNotification(json.message);
                    }
                };
            }
            else{
                var url = '/teacher/' + teacher_id + '/class/' + class_id +
                    '/student/' + student_id  + '/heso/' + cl +
                    '/mark/' + mark_id+ '/modify';
                var args = {
                    type:'POST',
                    'url':url,
                    'global':false,
                    'data':{
                        'diem':value
                    },
                    datatype:"json",
                    success: function(json){
                        if(json.success){
                            $("#notify").showNotification('Đã lưu');
                            $input.attr('data-diem',value);
                        }
                        else $("#notify").showNotification(json.message);
                    }
                };
            }
        }
        else{
            var url = '/teacher/' + teacher_id + '/class/' + class_id +
                '/student/' + student_id  + '/heso/' + cl + '/mark/create';
            var args = {
                type:'POST',
                'url':url,
                'global':false,
                'data':{
                    'diem':value
                },
                datatype:"json",
                success: function(json){
                    if(json.success){
                        $("#notify").showNotification('Đã lưu');
                        $input.addClass('old-mark');
                        $input.attr("id",json.mark);
                        $input.attr('data-diem',value);
                    }
                    else $("#notify").showNotification(json.message);
                }
            };
        }
        $.ajax(args);
    }
    function add_new_column(hs_id, value){
        var colspan = parseInt($("#hs-thread").attr("colspan"));
        colspan = colspan + 1;
        $("#hs-thread").attr("colspan",colspan);
        if (edit_hs){
            var th = '<th class="'+ hs_id +'"><input type="text" name="heso" value="' +
                value + '" data-heso="'+ value + '"></th>';
            var td = '<td class="'+ hs_id +'"><input type="text" name="diem" disabled="disabled" value=""></td>';
        }
        else{
            var th = '<th class="'+ hs_id +'"><input type="text" disabled="disabled" name="heso" value="' +
                value + '" data-heso="'+ value + '"></th>';
            var td = '<td class="'+ hs_id +'"><input type="text" name="diem" value=""></td>';
        }
        $("#hs-row").append(th);
        $(".student-mark").append(td);
    }
    $("#btn-add-mark").click(function (){
        $("#add-column-modal").modal("show");
        return false;
    });
    $("#add-column-modal").on("hide",function (){
        clear_bootstrap_error();
        $("#id_hs").val('');
    });
    $("#add-column-button").click(add_he_so);
    $("#btn-edit-hs").click(function (){
        edit_hs = true;
        $("td > input").attr("disabled","disabled");
        $("th > input").attr("disabled",false);
        $("#btn-edit-mark").show();
        $(this).hide();
        return false;
    });
    $("#btn-edit-mark").click(function (){
        edit_hs = false;
        $("th > input").attr("disabled","disabled");
        $("td > input").attr("disabled",false);
        $("#btn-edit-hs").show();
        $(this).hide();
        return false;
    });
    $("#mark_body").delegate("td > input", "blur", edit_mark);
    $("#mark_head").delegate("th > input", "blur", edit_he_so);
    $("#mark_body").delegate("input[name=diem]", "keyup", key_up_diem);
    $("#mark_head").delegate("input[name=heso]", "keyup", key_up_heso);
});
