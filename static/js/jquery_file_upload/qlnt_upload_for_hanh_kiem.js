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
    var id = window.location.pathname.split('/');
    var class_id = id[id.length - 1];


    // Initialize the jQuery File Upload widget:
    $('#fileupload').fileupload({
        url: '/school/import/hanh_kiem/' + class_id,
        dataType: 'json',
        acceptFileTypes: /(\.|\/)(xls)$/i,
        maxNumberOfFiles: 1

    });

    $("#fileupload").bind('fileuploaddone', function(e, data){
            $("#notify").text("Đã lưu.");
            $("#notify").delay(1000).fadeOut('fast');
            if (data.result[0].process_message.replace(/ /g,'') != ''){
                $("#errorDetail").html(data.result[0].process_message);
                $("#errorDetail > ul").append('<li> Hạnh kiểm đã được cập nhật</li>');
                $("#errorDetail").show();
            } else {
                $("#errorDetail").hide();
            }
    });
});
