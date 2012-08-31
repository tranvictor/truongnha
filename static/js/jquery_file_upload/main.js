/*
 * jQuery File Upload Plugin JS Example 6.5.1
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2010, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 */

/*jslint nomen: true, unparam: true, regexp: true */
/*global $, window, document */

$(function () {
    'use strict';

    // Initialize the jQuery File Upload widget:
    $('#fileupload').fileupload({
        url: '/school/import/teacher/0',
        dataType: 'json',
        acceptFileTypes: /(\.|\/)(xls)$/i,
        maxNumberOfFiles: 5
    });

    $("#fileupload").bind('fileuploaddone', function(e, data){
        $("#notify").text("Đã lưu.");
        $("#notify").delay(1000).fadeOut('fast');
        if (data.result[0].process_message.replace(/ /g,'') != ''){
            $("#errorDetail").html(data.result[0].process_message);
            if (data.result[0].teacher_confliction){
                $("#errorDetail > ul").append(
                    '<li>' + data.result[0].teacher_confliction +' ' +
                        '<a id="update_existing" href="/school/import/teacher/update" class="btn btn-primary">Cập nhật những giáo viên này.</a>'+
                        '</li>');
                $("#update_existing").click(function(){
                    if ($(this).attr('href') != '')
                        $.ajax({
                            url: "/school/import/teacher/update",
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
                +' giáo viên.</li>');

            $("#errorDetail").show();
        } else {
            $("#errorDetail").hide();
        }
    });


//    if (window.location.hostname === 'blueimp.github.com') {
//        // Demo settings:
//        $('#fileupload').fileupload('option', {
//            url: '//jquery-file-upload.appspot.com/',
//            maxFileSize: 5000000,
//            acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i,
//            resizeMaxWidth: 1920,
//            resizeMaxHeight: 1200
//        });
//        // Upload server status check for browsers with CORS support:
//        if ($.support.cors) {
//            $.ajax({
//                url: '//jquery-file-upload.appspot.com/',
//                type: 'HEAD'
//            }).fail(function () {
//                $('<span class="alert alert-error"/>')
//                    .text('Upload server currently unavailable - ' +
//                            new Date())
//                    .appendTo('#fileupload');
//            });
//        }
//    } else {
//        // Load existing files:
//        $('#fileupload').each(function () {
//            var that = this;
//            $.getJSON(this.action, function (result) {
//                if (result && result.length) {
//                    $(that).fileupload('option', 'done')
//                        .call(that, null, {result: result});
//                }
//            });
//        });
//    }

});
