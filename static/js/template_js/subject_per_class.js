$(document).ready(function() {
    (function($) {
        $.widget("ui.combobox", {
            _create: function() {
                var self = this,
                        select = this.element.hide(),
                        selected = select.children(":selected"),
                        value = selected.val() ? selected.text() : "";
                var input = this.input = $("<input class='id_teacher_id' placeholder='Nhập một số ký tự để chọn'>")
                        .insertAfter(select)
                        .val(value)
//                        .addClass("ui-widget ui-widget-content")
                        .autocomplete({
                            delay: 0,
                            minLength: 0,
                            source: function(request, response) {
                                var matcher = new RegExp($.ui.autocomplete.escapeRegex(request.term), "i");
                                response(select.children("option").map(function() {
                                    var text = $(this).text();
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
                                var teacher = ui.item.option.value;
                                $(this).parents("td").children("#id_teacher_id").val(teacher);

                                if (typeof attr !== 'undefined' && attr !== false && attr !== 'subject_form') {
                                    var id = $(this).parents("tr").attr('id').split(' ')[0];
                                    var data = { id: id, teacher: teacher, request_type:'teacher'};
                                    var arg = { type:"POST",
                                        url:"",
                                        data: data,
                                        datatype:"json",
                                        error: function() {
                                            $(".submitbutton").attr('disabled', false);
                                            $(".submitbutton").val('Lưu');
                                        }
                                    };
                                    $.ajax(arg);
                                    return false;
                                }

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

    $("#notify").ajaxSuccess(function(event, request, settings, json) {
        if (json.message != null) {
            $(this).html("<ul>" + json.message + "</ul>");
            $(this).delay(1000).fadeOut(10000);
        }
        else {
            $(this).text("Đã lưu");
            $(this).delay(1000).fadeOut('fast');
        }
    });

//    $(".submitbutton").attr("disabled", true);
    $("#add_subject_form").bind('submit', function() {
        var $this = $(this);
        var d = $this.serialize();
        d = d + '&request_type=add';
        var arg = { type:"POST",
            url:"",
            data: d,
            datatype:"json",
            success: function(json){
                if (json.success){
                    location.reload('true');
                }
                $("#notify").showNotification(json.message, 5000);
            },
            error: function() {
            }
        };
        $.ajax(arg);
        return false;
    });

    $("input[name=number_lesson]").each(function() {
        $(this).change(function() {
            var attr = $(this).parents("tr").attr('id');
            if (typeof attr !== 'undefined' && attr !== false && attr !== 'subject_form') {
                var id = $(this).parents("tr").attr('id').split(' ')[0];
                var value = $(this).val();
                var data = {value: value, id: id, request_type:'number_lesson'};
                var arg = { type:"POST",
                    url:"",
                    data: data,
                    datatype:"json",
                    error: function() {
//                        $(".submitbutton").attr('disabled', false);
//                        $(".submitbutton").val('Lưu');
                    }
                };
                $.ajax(arg);
                return false;
            }
        });
    });
    
//    $("select[name=type]").each(function() {
//        $(this).change(function() {
//            var attr = $(this).parents("tr").attr('id');
//            if (typeof attr !== 'undefined' && attr !== false && attr !== 'subject_form') {
//                var id = $(this).parents("tr").attr('id').split(' ')[0];
//                var type = $(this).val();
//                var data = { id: id, type: type, request_type:'type'};
//                var arg = { type:"POST",
//                    url:"",
//                    data: data,
//                    datatype:"json",
//                    error: function() {
//                        $(".submitbutton").attr('disabled', false);
//                        $(".submitbutton").val('Lưu');
//                    }
//                };
//                $.ajax(arg);
//                return false;
//            }
//
//        });
//    });

    $("select[name=primary]").each(function() {
        $(this).change(function() {
            var attr = $(this).parents("tr").attr('id');
            if (typeof attr !== 'undefined' && attr !== false && attr !== 'subject_form') {
                var id = $(this).parents("tr").attr('id').split(' ')[0];
                var primary = $(this).val();
                var data = { id: id, primary: primary, request_type:'primary'};
                var arg = { type:"POST",
                    url:"",
                    data: data,
                    datatype:"json",
                    error: function() {
//                        $(".submitbutton").attr('disabled', false);
//                        $(".submitbutton").val('Lưu');
                    }
                };
                $.ajax(arg);
                return false;
            }
        });
    });

    $("#teacher").each(function() {
        //$(this).hide();
        $(this).children("div").children("#id_teacher_id").addClass("combobox");
    });

    $("select[name=teacher_id]").each(function(){
        if (!$(this).hasClass("combobox")){
            $(this).hide()
        }
    });

    $(".deletion").each(function() {
            $(this).click(function() {
                if (!confirm("Bạn có chắc chắn xóa không?")) return false;
                var attr = $(this).parents("tr").attr('id');
                if (typeof attr !== 'undefined' && attr !== false && attr !== 'subject_form') {
                    var id = $(this).parents("tr").attr('id').split(' ')[0];
                    var data = { id: id, request_type:'xoa'};
                    var arg = { type:"POST",
                        url:"",
                        data: data,
                        datatype:"json",
                        error: function() {
                        },
                        success: function(json) {
                            $("#notify").showNotification(json.message, 5000);
                            location.reload('true');
                        }
                    };
                    $.ajax(arg);
                    return false;
                }
            });
        });

    $("input[name=hs]").each(function() {
        $(this).change(function() {
            var attr = $(this).parents("tr").attr('id');
            if (typeof attr !== 'undefined' && attr !== false && attr !== 'subject_form') {
                var id = $(this).parents("tr").attr('id').split(' ')[0];
                var val = $(this).val();
                var data = { id: id, hs: val, request_type:'hs'};
                var arg = { type:"POST",
                    url:"",
                    data: data,
                    datatype:"json",
                    error: function() {
//                        $(".submitbutton").attr('disabled', false);
//                        $(".submitbutton").val('Lưu');
                    },
                    success: function() {
                    }
                };
                $.ajax(arg);
                return false;
            }
        });
    });

    $("input[name=nx]").each(function() {
        $(this).change(function() {
            var attr = $(this).parents("tr").attr('id');
            if (typeof attr !== 'undefined' && attr !== false && attr !== 'subject_form') {
                var id = $(this).parents("tr").attr('id').split(' ')[0];
                var val = $(this).is(':checked');
                var data = { id: id, nx: val, request_type:'nx'};
                var arg = { type:"POST",
                    url:"",
                    data: data,
                    datatype:"json",
                    error: function() {
//                        $(".submitbutton").attr('disabled', false);
//                        $(".submitbutton").val('Lưu');
                    },
                    success: function() {
                    }
                };
                $.ajax(arg);
                return false;
            }
        });
    });
});