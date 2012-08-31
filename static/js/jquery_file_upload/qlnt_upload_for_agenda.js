/**
 * Created by PyCharm.
 * User: leeyun
 * Date: 2/3/12
 * Time: 11:29 PM
 * To change this template use File | Settings | File Templates.
 */
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
    var i = 0, subject_id = 0;
    for ( i=0; i < id.length; i++){
        if (isNumeric(id[i])){
            subject_id = id[i];
            break;
        }
    }

    // Initialize the jQuery File Upload widget:
    $('#fileupload').fileupload({
        url: '/school/import/subjectAgenda/' + subject_id,
        dataType: 'json',
        acceptFileTypes: /(\.|\/)(xls)$/i,
        maxNumberOfFiles: 1
    });

    $("#fileupload").bind('fileuploaddone', function(e, data){
            $("#notify").text("Đã lưu.");
            $("#notify").delay(1000).fadeOut('fast');
            if (data.result[0].process_message.replace(/ /g,'') != ''){
                $("#errorDetail").html(data.result[0].process_message);
                $("#errorDetail > ul").append('<li>Chương trình học đã được cập nhật</li>');
                $("#errorDetail").show();
            } else {
                $("#errorDetail").hide();
            }
    });

});