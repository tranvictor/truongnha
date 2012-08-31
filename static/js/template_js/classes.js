/**
 * Created by vu.tran54.
 * User: vu.tran54
 * Date: 2/18/12
 * Time: 4:53 AM
 */
$(document).ready(function(){
    (function($) {
        var get_text_from_id = function(teacher_id){
            var text = "--------";
            $('#teacher-source').find('option').each(function(){
                if (parseInt($(this).val(), 10) == parseInt(teacher_id, 10)) text = $(this).text();
            });
            return text;
        }
        $.widget("ui.combobox", {
            _create: function() {
                var self = this,
                    select = this.element.hide(),
                    selected = select.children(":selected"),
                    value = selected.val() ? $.trim(selected.text()) : "";
                var input = this.input = $("<input class='id_teacher_id'>")
                    .insertAfter(select)
                    .val(value)
                    .autocomplete({
                        delay: 0,
                        minLength: 0,
                        source: function(request, response) {
                            var matcher = new RegExp($.ui.autocomplete.escapeRegex(request.term), "i");
                            response(select.children("option").map(function() {
                                var text = $.trim($(this).text());
                                if ( !request.term || matcher.test(text) )
                                    return {
                                        label: text.replace(
                                            new RegExp(
                                                "(?![^&;]+;)(?!<[^<>]*)(" +
                                                    $.ui.autocomplete.escapeRegex(request.term) +
                                                    ")(?![^<>]*>)(?![^&;]+;)", "gi"
                                            ), "<strong>$1</strong>"),
                                        value: text,
                                        option: this
                                    };
                            }));
                        },
                        select: function(event, ui) {
                            ui.item.option.selected = true;
                            self._trigger("selected", event, {
                                item: ui.item.option
                            });
                            this.value = ui.item.option.text;
                            var attr = $(this).parents("tr").attr('id');
                            var selected_teacher = ui.item.option.value;
                            var id = $(this).parents("tr").attr('id');
                            var current_teacher = $(this).parents("tr").attr('teacher');
                            if (current_teacher == selected_teacher) return false;
                            var data = { id: id, teacher_id:selected_teacher, request_type:'update'};
                            var arg = { type:"POST",
                                url:"",
                                data: data,
                                global: false,
                                datatype:"json",
                                success:function(json){
                                    if (json.success) {
                                        $("#notify").showNotification("Đã lưu");
                                        $("#" + id).attr('teacher', selected_teacher);
                                    }
                                    else {
                                        $("#notify").showNotification(json.message);
                                        $("#" + id).find("input").val(get_text_from_id(current_teacher));
                                    }
                                },
                                error:function(){
                                    $("#notify").showNotification("Có lỗi xảy ra khi gửi dữ liệu.");
                                }
                            }
                            $.ajax(arg);
                            return false;

                        },
                        change: function(event, ui) {
                            if (!ui.item) {
                                var matcher = new RegExp("^" + $.ui.autocomplete.escapeRegex($(this).val()) + "$", "i"),
                                    valid = false;
                                select.children("option").each(function() {
                                    if ($(this).text().match(matcher)) {
                                        this.selected = valid = true;
                                        return false;
                                    }
                                });
                                if (!valid) {
                                    // remove invalid value, as it didn't match anything
                                    $(this).val("");
                                    select.val("");
                                    input.data("autocomplete").term = "";
                                    return false;
                                }
                            }
                        }
                    });

                input.data("autocomplete")._renderItem = function(ul, item) {
                    return $("<li></li>")
                        .data("item.autocomplete", item)
                        .append("<a>" + item.label + "</a>")
                        .appendTo(ul);
                };
            }
        });
    })(jQuery);

    $(function() {
        $(".combobox").each(function() {
            $(this).combobox();
        });
    });

    $(".class-delete").click(function(){
        var classID = $(this).attr('forclass');
        if (!confirm("Bạn có chắc chắn muốn xóa?")) return false;
        var arg = { type:"GET",
            url:"school/deleteClass/" + classID,
            global: false,
            success:function(json){
                if (json == "OK"){
                    $("#notify").showNotification("Đã xóa.");
                    $("#"+classID).remove();
                } else if (json == "Not Empty Class"){
                    $("#notify").showNotification("Không thể xóa lớp còn học sinh.")
                }
            },
            error:function(){
                $("#notify").showNotification("Có lỗi xảy ra khi gửi dữ liệu.");
            }
        };
        $.ajax(arg);
        return false;
    });
});