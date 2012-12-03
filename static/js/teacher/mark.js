$(document).ready(function(){
    var big_value = 9999;
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
    function new_class(hs){
        var cl = hs + '-' + big_value;
        big_value = big_value - 1;
        cl = String(cl);
        cl = cl.replace('.','dot');
        return cl;
    }
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
    console.log($('#add-column-model'));
    $("#btn-add-mark").click(function(){
        $("#add-column-modal").modal("show");
        return false;
    });
    $("#add-column-modal").on("hide",function(){
        clear_bootstrap_error();
        $("#id_hs").val('');
    });
    $("#add-column-button").click(function(){
        clear_bootstrap_error();
        var value = $("#id_hs").val();
        if (isNaN(value) || (value == '')){
            var err = {'id_hs':'Hệ số phải là một số thực'};
            add_bootstrap_error(err);
        }
        else{
            var colspan = parseInt($("#hs-thread").attr("colspan"));
            colspan = colspan + 1;
            var cl = new_class(value);
            $("#hs-thread").attr("colspan",colspan);
            var th = '<th class="'+ cl +'"><input type="text" disabled="disabled" value=' + value + '></th>';
            var td = '<td class="'+ cl +'"><input type="text" value=""></td>';
            $("#hs-row").append(th);
            $(".student-mark").append(td);
            $("#add-column-modal").modal("hide");
        }
        return false;
    });
    $("#btn-edit-hs").click(function(){
        $("td > input").attr("disabled","disabled");
        $("th > input").attr("disabled",false);
        $("#btn-edit-mark").show();
        $(this).hide();
        return false;
    });
    $("#btn-edit-mark").click(function(){
        $("th > input").attr("disabled","disabled");
        $("td > input").attr("disabled",false);
        $("#btn-edit-hs").show();
        $(this).hide();
        return false;
    });
    $("tbody").delegate("td > input","blur",function(){
        var std_info = $(this).parent().parent().attr('id').split('-');
        var student_id = std_info[1];
        var cl = $(this).parent().attr('class');
        var selected = 'th.' + cl + '> input';
        var hs = $(selected).val();
        var value = $(this).val();
        var old_value = $(this).attr('data-diem');
        var csrf = getCookie("csrftoken");
        var $input = $(this);
        var tem1 = parseFloat(old_value);
        var tem2 = parseFloat(value);
        if((tem1 == tem2 )||(isNaN(tem1)&&isNaN(tem2))) return false;
        if ($(this).hasClass('old-mark')){
            var mark_id = $(this).attr('id');
            if (value == ''){
                var url = '/teacher/' + teacher_id + '/class/' + class_id +
                    '/student/' + student_id + '/mark/' + mark_id+ '/remove';
                var args = {
                    type:'POST',
                    'url':url,
                    'global':false,
                    'data':{
                        'diem':value,
                        'hs':hs,
                        'csrfmiddlewaretoken':csrf
                    },
                    datatype:"json",
                    success: function(json){
                        if(json.success){
                            $input.removeClass('old-mark');
                            $input.attr('data-diem',value);
                        }
                    }
                };
            }
            else{
                var url = '/teacher/' + teacher_id + '/class/' + class_id +
                    '/student/' + student_id + '/mark/' + mark_id+ '/modify';
                var args = {
                    type:'POST',
                    'url':url,
                    'global':false,
                    'data':{
                        'diem':value,
                        'hs':hs,
                        'csrfmiddlewaretoken':csrf
                    },
                    datatype:"json",
                    success: function(json){
                        if(json.success){
                            $input.attr('data-diem',value);
                        }
                    }
                };
            }
        }
        else{
            var url = '/teacher/' + teacher_id + '/class/' + class_id + '/student/' + student_id + '/mark/create';
            var args = {
                type:'POST',
                'url':url,
                'global':false,
                'data':{
                    'diem':value,
                    'hs':hs,
                    'csrfmiddlewaretoken':csrf
                },
                datatype:"json",
                success: function(json){
                    if(json.success){
                        $input.addClass('old-mark');
                        $input.attr("id",json.mark);
                        $input.attr('data-diem',value);
                    }
                }
            };
        }
        $.ajax(args);
    });
    $("thead").delegate("th > input","blur",function(){
        var hs = $(this).val();
        var old_hs = $(this).attr('data-heso');
        var old_class = $(this).parent().attr('class');
        var new_cl = new_class(hs);
        var selected = "td." + old_class;
        var id_list = "";
        var csrf = getCookie("csrftoken");
        var tem1 = parseFloat(hs);
        var tem2 = parseFloat(old_hs);
        if((tem1 == tem2 )||(isNaN(tem1)&&isNaN(tem2))) return false;
        $(selected).each(function(){
            var id = $("> input",this).attr('id');
            console.log(id);
            if (id){
                id_list = id_list + id + "-";
            }
        });
        id_list = id_list.substring(0, id_list.length - 1);
        var url = '/teacher/' + teacher_id + '/class/' + class_id + '/mark/modify';
        var args = {
            type:'POST',
            'url':url,
            'global':false,
            'data':{
                'id_list':id_list,
                'hs':hs,
                'csrfmiddlewaretoken':csrf
            },
            datatype:"json",
            success:function(json){
                if(json.success){
                    var select = '.' + old_class;
                    $(select).addClass(new_cl);
                    $(old_class).removeClass(old_class);
                }
            }
        };
        $.ajax(args);
    });
    $("input").focus(function(){
        $(this).select();
        return false;
    });
    $("input[name=diem]").on('keyup',key_up_diem );
    $("input[name=heso]").on('keyup', function (event) {
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
    });
});
