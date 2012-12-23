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
	if (id[2]=='markForTeacher')
		var urlString=id[4]+'/'+id[5];
	else	
		var urlString=id[3]+'/'+id[5];
		
	//alert(urlString);	
    // Initialize the jQuery File Upload widget:
	$("#upload_modal").on('hidden', function(){
		location.reload('true');
	});
	$("#upload-modal-exit").click(function(){
		$("#upload_modal").modal('hide');
		return false;
	});
	//$("#upload_modal").modal('show');
	$("#noUpdate").click(function(){
		//alert("chao");
		$("#upload_modal").modal('hide');
	});
	$("#update").click(function(){
		$.ajax({
			global:false,
			url: "/school/importMark/"+urlString+"/0",
			dataType: 'json',
			type: 'POST',
			success: function(data){
				$("#errorDetail").text(data.message);
				$("#diffMessage").css("display","none");
			}
		});		
	});		
	
    $('#fileupload').fileupload({
		
        url: "/school/importMark/"+urlString,
        dataType: 'json',
        acceptFileTypes: /(\.|\/)(xls)$/i,
        maxNumberOfFiles: 10

    });
	
    $("#fileupload").bind('fileuploaddone', function(e, data){
            if (data.result[0].success){
                $("#notify").text("Đã lưu.");
                $("#notify").delay(1000).fadeOut('fast');
                /*
                if (data.result[0].process_message.replace(/ /g,'') != ''){
                    $("#errorDetail").html(data.result[0].process_message);
                    if (data.result[0].student_confliction){
                        $("#errorDetail > ul").append('<li>' + data.result[0].student_confliction +'</li>');
                    }
                    $("#errorDetail > ul").append('<li>' + 'Bạn đã nhập thành công '
                                                         + data.result[0].number_ok
                                                         + '/'
                                                         + data.result[0].number
                                                         +' học sinh.</li>');


                } else {
                    $("#errorDetail").hide();
                }
                */
                $("#errorDetail").text('');

                if (data.result[0].absentMessage!='')
                {
                    $("#errorDetail").append("Không có họ tên hoặc ngày sinh của những học sinh sau:<br>");
                    $("#errorDetail").append("<table class='table'>"+data.result[0].absentMessage+"</table>");
                    $("#errorDetail").show();
                }
                if (data.result[0].validateMessage!='')
                {
                    $("#errorDetail").append(data.result[0].validateMessage);
                    $("#errorDetail").show();
                }
				
                if (data.result[0].editMarkMessage!='')
                {
                    $("#errorDetail").append(data.result[0].editMarkMessage);
                    $("#errorDetail").show();
                }
				else
                if (data.result[0].diffMessage[0])
                {
                    var str = "Có "+data.result[0].numberDiff+" điểm ở các ô sau khác so với bảng điểm hiện thời:<br>"+data.result[0].diffMessage[0]+"<br>";
                    $("#errorDetail").append(str);
                    $("#errorDetail").append("Bạn có muốn cập nhập không ?");
                    $("#diffMessage").show();
                }
                else
                    $("#errorDetail").append(data.result[0].message);

                $("#errorDetail").show();
            } else{
                $("#errorDetail").text('');
                $("#notify").showNotification(data.result[0].message, 5000);
                $("#errorDetail").append(data.result[0].message);
                $("#errorDetail").show();
            }
			 	
    });


    //$("#startUpload").attr('disabled', 'disabled');
    //$("#startUpload").addClass('ui-button-disabled ui-state-disabled');

    
    // Load existing files:
    /*$.getJSON($('#fileupload form').prop('action'), function (files) {
        var fu = $('#fileupload').data('fileupload');
        fu._adjustMaxNumberOfFiles(-files.length);
        fu._renderDownload(files)
            .appendTo($('#fileupload .files'))
            .fadeIn(function () {
                // Fix for IE7 and lower:
                $(this).show();
            });
    });
*/
    // Open download dialogs via iframes,
    // to prevent aborting current uploads:
    $('#fileupload .files a:not([target^=_blank])').live('click', function (e) {
        e.preventDefault();
        $('<iframe style="display:none;"></iframe>')
            .prop('src', this.href)
            .appendTo('body');
    });

});