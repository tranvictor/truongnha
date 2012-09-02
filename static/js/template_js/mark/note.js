$(document).ready(function() {
	var currentIndex=0
	for(var i=1;i<length;i++)
	{
		var id="#edit_"+i;
		messageNote[i]=$(id).attr("title");
		$(id).click(function(){
			// setting up layout
			currentIndex=(this.id).split('_')[1];
			$("#editContent").val(messageNote[currentIndex]);
			var buttonOffsetTop = $(this).offset().top;
			var editOffsetTop   = $("#editWindow").offset().top;	
			if (($("#editWindow").css('display') == 'none') || (buttonOffsetTop!=editOffsetTop)){
				$("#saveNote").removeClass("disabled");
				$("#saveNote").html("Lưu");	
				var buttonOffsetTop = $(this).offset().top;
				var buttonOffsetLeft = $(this).offset().left;				
				var editWindow = $("#editWindow");				
				var editWindowWidth = parseInt(editWindow.css('width'));
				editWindow.css('position', 'absolute');
				editWindow.css('top', buttonOffsetTop);
				editWindow.css('left',buttonOffsetLeft-editWindowWidth-45);
				editWindow.slideDown(400);
				$("#editContent").focus();
			} 
			else $("#editWindow").slideUp(100);
		});		
	}	

	$("#editContent").keyup(function(e){
		var code = (e.keyCode) ? e.keyCode : e.which;
		if (code==27)
			$("#editClose").trigger("click")
		else	
		if (code==13)
			$("#saveNote").trigger("click");
		else
		{	
			$("#saveNote").removeClass("disabled");
			$("#saveNote").html("Lưu");	
		}	
	});	
	$("#saveNote").click(function(){
		var data1=$("#editContent").val().trim();
		data=idTeacher+"/"+idUser + "/"+idAr[currentIndex]+"/"+data1;
		var arg = { 
			type:"POST",
			url:"/school/saveNote",
			global: false,
			data: { 
				data:data,
			},
			datatype:"json",
			success: function(json) {
				//$("#editWindow").slideUp(400);
				$("#saveNote").addClass("disabled");
				//$("#saveNote").addClass("icon-pencil");
				$("#saveNote").html("Đã lưu");	
				$("#notify").showNotification("Đã Lưu");
				$("#editClose").trigger("click");
				var id="#edit_"+currentIndex;
				
				$(id).tooltip();
				$(id).attr("data-original-title", data1);
				messageNote[currentIndex]=data1;
				
				if (data1!="")
				{
	//						$(id).addClass("noted");
					//$(id).({content:data1});
					//alert(table.rows[parseInt(currentIndex)+2].cells[3*MAX_COL+7].innerHTML);
					if (!isSecondTerm)
						table.rows[parseInt(currentIndex)+2].cells[3*MAX_COL+7].innerHTML="<i class='icon-pencil'></i>";
					else		
						table.rows[parseInt(currentIndex)+2].cells[3*MAX_COL+9].innerHTML="<i class='icon-pencil'></i>";
				}	
				else	
				{
	//						$(id).removeClass("noted");
					if (!isSecondTerm)
						table.rows[parseInt(currentIndex)+2].cells[3*MAX_COL+7].innerHTML="<i class='icon-file'></i>";
					else		
						table.rows[parseInt(currentIndex)+2].cells[3*MAX_COL+9].innerHTML="<i class='icon-file'></i>";
					//$(id).unbind("hover");
				}
			},
			error: function(){
				$("#notify").showNotification("Gặp lỗi khi lưu dữ liệu");
			}
		};
		$.ajax(arg);			
	})
	$("#editClose").click(function(){
		$("#editWindow").slideUp(100);
	});
});
