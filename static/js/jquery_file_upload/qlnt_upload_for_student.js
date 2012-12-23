/*
 * jQuery File Upload Plugin JS Example 5.0.2
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2010, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://creativecommons.org/licenses/MIT/
 */



/*jslint nomen: true */
/*global $ */

$(function () {
    'use strict';
    function isNumeric(input){
        return (input - 0) == input && input.length > 0;
    }

    var id = window.location.pathname.split('/');
    var i = 0;
    for ( i=0; i < id.length; i++){
        if (isNumeric(id[i])){
            id = id[i];
            break;
        }
    }

    // Initialize the jQuery File Upload widget:
    $('#fileupload').fileupload({
        url: '/school/start_year/import/student/' + id +'/0',
        dataType: 'json',
        acceptFileTypes: /(\.|\/)(xls)$/i,
        maxNumberOfFiles: 1

    });

    $("#fileupload").bind('fileuploaddone', function(e, data){
            $("#notify").text("Đã lưu.");
            $("#notify").delay(1000).fadeOut('fast');
            if (data.result[0].process_message.replace(/ /g,'') != ''){
                $("#errorDetail").html(data.result[0].process_message);
                if (data.result[0].student_confliction){
                    $("#errorDetail > ul").append(
                            '<li>' + data.result[0].student_confliction +' ' + '</li>');
                    if (data.result[0].exist_student_in_class){
                        $("#errorDetail > ul").append('<li>'+
                            '<a id="update_existing" href="/school/start_year/import/student/'+id+
                            '/update" class="btn btn-primary">Cập nhật thông tin những học sinh trong lớp này.</a>'+'</li>'
                        );
                    }
                    if (data.result[0].exist_student_out_class){
                        $("#errorDetail > ul").append(
                            '<li>Nếu bạn muốn chuyển những học sinh đã tồn tại đến lớp này xin vui lòng sử' +
                                ' dụng chức năng chuyển lớp.</li>');
                    }
                    $("#update_existing").click(function(){
                        if ($(this).attr('href') != '')
                            $.ajax({
                                url: $(this).attr('href'),
                                dataType: 'json',
                                type: 'POST',
                                success: function(json){
                                    if (!json.success){
                                        $("#notify").showNotification(json.message);
                                    } else {
                                        $("#update_existing").text(json.message);
                                        $("#update_existing").attr('href', '');
                                    }
                                }
                            });
                        return false;
                    })
                }
                $("#errorDetail > ul").append('<li>' + 'Bạn đã nhập thành công '
                                                     + data.result[0].number_ok
                                                     + '/'
                                                     + data.result[0].number
                                                     +' học sinh.</li>');

                $("#errorDetail").show();
            } else {
                $("#errorDetail").hide();
            }
    });
});