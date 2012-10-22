$(document).ready(function() {
	/*
	$('input[type=text]').focus(function(e) {
		highLight(this);
	}
	);

	$('input[type=text]').blur(function() {
			loseHighLight(this);
	  }
	);
	$('input[type=text]').mouseup(
		function(e) {
			e.preventDefault();
		}
	);
	*/		
	/*
	$("#import").click(function() {
		$("#fileupload").dialog('open');
	});		
	$("#fileupload").dialog({
		modal : true,
		buttons: {
			Đóng: function() {
				location.reload('true');
				$(this).dialog('close');
			}
		},
		close: function() {
				location.reload('true');
		},
		autoOpen: false,
		width: 700,
		height: 400,
		maxWidth: 700,
		maxHeight: 400,
		title: "Nhập điểm từ file Excel"
	});
	*/
	
	$("#buttonExport").click(function() {
		//alert("chao");
		$("#dialogExport").dialog('open');
	});	
		
	$("#dialogExport").dialog({
		modal : true,
		zIndex: 3999,
		buttons: {
			Thôi: function() {
				$(this).dialog('close');
			}
		},
		autoOpen: false,
		width: 700,
		height: 200,
		maxWidth: 700,
		maxHeight: 400,
		title: "Lấy mẫu excel với số cột tùy ý"
	});
	
	$("#finishExport").click(function(){
		var colMieng   = document.getElementById("colMiengExport").value;
		var col15Phut  = document.getElementById("col15PhutExport").value;
		var colMotTiet = document.getElementById("colMotTietExport").value;
		this.href="/school/exportMark/" + termChoice + "/" + subjectChoice + "/" + colMieng+"/"+col15Phut+"/"+colMotTiet;
		$("#dialogExport").dialog("close");
		//alert("hello");
	});		
});
