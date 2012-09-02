// this file contains the functions which to save score.
// It caculates average score automatically when having final score and 
// caculates final score of year if having final score of term 1 and term 2.  

var table   = document.getElementById("markTable");	
var needToConfirm = false;
window.onbeforeunload = function confirmExit(e)
{
	if (document.getElementById("buttonSave").style.display=="")
	{
		if (document.getElementById("messageChanging").innerHTML!="Đã lưu")
			needToConfirm=true;
		else	needToConfirm=false;
	}		
	else	needToConfirm=false;
	
	if (needToConfirm)
		return  "Đang lưu điểm. Xin vui lòng ấn cancel(ở lại trang này) để lưu nốt." ;	
}

function calculateOldAr()
{
	var exp1=/[,]/g	
	for(var i=1;i<length;i++)
		for(var j=1; j <SIZE ; j++)
			if (table.rows[i+2].cells.length>j+5){
				var value=table.rows[i+2].cells[j+4].innerHTML;										
				value=value.replace(exp1,'.');
				
				if (isComment)
				{
					oldAr[i][j]=value;	
					if (value=="")
						oldAr[i][j]=-1;
				}	
				else
				{						
					oldAr[i][j]=parseFloat(value);
					if (isNaN(oldAr[i][j]))
						oldAr[i][j]=-1;
				}		
			}		
}
//can doan code nay la vi can kiem tra xem diem tren server co giong o client hay ko
			
		/*	
		var tb =document.getElementById(id.toString());
		if (tb)
		{ 			
			var value=tb.value;
			if (value==undefined)
				value=tb.innerHTML;
			value=value.replace(exp1,'.');
			if (!isComment)
			{	
				oldAr[i][j]=parseFloat(value);
				if (isNaN(oldAr[i][j]))
					oldAr[i][j]=-1;
			}
			else
			{
				oldAr[i][j]=value;	
				if (value=="")
					oldAr[i][j]=-1;
			}	
		}
		else
			oldAr[i][j]=-1;
		*/	
			

function calculateNewArray(newAr)
{
	var ok=false;
	var str="";
	if (!isComment)
	{
		for(var i=1;i<length;i++)
			for(var j=1;j<SIZE;j++)
			{		
				if (table.rows[i+2].cells.length>j+5){
					var value=table.rows[i+2].cells[j+4].innerHTML;					
					
					var exp1=/[,]/g
					value=value.replace(exp1,'.');		
					newAr[i][j]=parseFloat(value);
					
					if (isNaN(newAr[i][j]))
						newAr[i][j]=-1;
				}		
				
				/*	
				if ((!isNaN(newAr[i][j])) && (newAr[i][j]>10))
					{
						var tb=document.getElementById(id.toString()); 
						acceptDigits(tb);
						newAr[i][j]=parseFloat(tb.value);
					}
				if (newAr[i][j].toString().length>4)	
				{
					var tb=document.getElementById(id.toString()); 					
					tb.value=tb.value.substring(0,4);
					newAr[i][j] = parseFloat(tb.value);
				}
				if (isNaN(newAr[i][j]))
					newAr[i][j]=-1;
				*/	
			}
			var cell = mainInput.parentElement;
			if (cell){
				var colIndex = cell.cellIndex;
				if (colIndex)
				{
					var rowIndex = cell.parentNode.rowIndex;
					newAr[rowIndex-2][colIndex-4]=parseFloat(mainInput.value);
					if (isNaN(newAr[rowIndex-2][colIndex-4]))
						newAr[rowIndex-2][colIndex-4]=-1;
					
				}	
			}
			
		for(var i=1;i<length;i++)
			for(var j=1;j<SIZE;j++)
				if ((newAr[i][j] != oldAr[i][j]) && (newAr[i][j]!='MG')&& ( !ok))
				{
					if (document.getElementById("messageChanging")){
						document.getElementById("messageChanging").innerHTML="Lưu ngay";
						document.getElementById("buttonSave").disabled="";
						document.getElementById("buttonSave").style.display="";
						latestTime= (new Date()).getTime();
						ok=true;
					}	
				}	
	}
	else
	{
		//writeNew();
		//writeOld();
		for(var i=1;i<length;i++)
			for(var j=1;j<SIZE;j++)
			{
				if (table.rows[i+2].cells.length>j+5){
					var value=table.rows[i+2].cells[j+4].innerHTML;
					if (value=="")
						newAr[i][j]=-1;
					else
						newAr[i][j]=value;
				}		
				else
					newAr[i][j]=-1;					
			}
			
		var cell = mainInput.parentElement;
		if (cell){
			var colIndex = cell.cellIndex;
			if (colIndex)
			{
				var rowIndex = cell.parentNode.rowIndex;
				newAr[rowIndex-2][colIndex-4]=mainInput.value.trim();
				if (newAr[rowIndex-2][colIndex-4]=="")
					newAr[rowIndex-2][colIndex-4]=-1;
			}	
		}
			
		for(var i=1;i<length;i++)
			for(var j=1;j<SIZE;j++)
				if ((newAr[i][j] != oldAr[i][j]) && ((newAr[i][j]!='MG')) && ( !ok))
				{
					if (document.getElementById("messageChanging")){
						document.getElementById("messageChanging").innerHTML="Lưu ngay";
						document.getElementById("buttonSave").disabled="";
						document.getElementById("buttonSave").style.display="";
						latestTime= (new Date()).getTime();
						ok=true;
					}	
				}	
				
	}
	
	if (!ok)
	{
		if (document.getElementById("messageChanging")){		
			document.getElementById("messageChanging").innerHTML="Đã lưu";
			document.getElementById("buttonSave").disabled ="disabled";
		}	
	}	
}

function getCookie(name) {
var cookieValue = null;
	if (document.cookie && document.cookie != '') {
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
var cookieValue = getCookie('csrftoken'); 

function doneSaveMark(data)
{
	
	var responseId=parseInt(data.message);
	if (responseId<currentId)
		resetOldAr();
	else
	{	
		currentId = responseId;
		updateOldAr();
		var currentTime = (new Date()).getTime();
		if ((currentTime-latestTime)>1500)
		{
			document.getElementById("messageChanging").innerHTML="Đã lưu";
			document.getElementById("buttonSave").disabled="disabled";
		}	
	}		
}	
function sendToServerMark(data)
{
    var arg = { 
		beforeSend: function(xhrObj){		
			xhrObj.setRequestHeader("X-CSRFToken",cookieValue );
		},
        global: false,					
		type:"POST",
		url:"/school/saveMark",
		data:{data:data, request_type:'sms'},
		datatype:"json",
		success:function(d){
			doneSaveMark(d);
		}
	};
	$.ajax(arg);
}

function addColor(source, average,activeMode)
{
	if (activeMode == 1)
		return source.replace("gioi","").replace("yeu","")
	else
	if (average >= 8){
		source = source.replace("yeu","");
		if (source.search("gioi") == -1)
			source +=" gioi";
	}
	else
	if (average <5){
		source = source.replace("gioi","");
		if (source.search("yeu") == -1)
			source +=" yeu";
	}
	else{
		source = source.replace("yeu","");
		source = source.replace("gioi","");
	}	
	return source;		
}

function viewAverage()
{
	//writeNew(newAr);
	calculateNewArray(newAr);	
	var sum=0;
	var factor=0;
	if (isSecondTerm) var t= 3*MAX_COL+3
	else  var t = 3*MAX_COL+2;

	//alert(table.rows[3].cells.length);
	
	for(var i=1;i<length;i++){
		if ((newAr[i][3*MAX_COL+1]!=-1) && (newAr[i][3*MAX_COL+1]!="MG"))
		{
			sum=newAr[i][3*MAX_COL+1]*3;
			factor=3;
			
			for(var j=1;j<2*MAX_COL+1;j++)
			if (newAr[i][j]!=-1)
			{
				sum=sum+newAr[i][j];
				factor++;
			}
			
			for(var j=2*MAX_COL+1;j<3*MAX_COL+1;j++)
			if (newAr[i][j]!=-1)
			{
				sum=sum+newAr[i][j]*2;
				factor=factor+2;
			}
			var averageValue = Math.round(sum/factor *10+0.00000001)/10;
			newAr[i][t]=averageValue;
			
			if ((averageValue-Math.floor(averageValue))<0.01)				
				table.rows[i+2].cells[t+4].innerHTML= averageValue+".0";
			else	
				table.rows[i+2].cells[t+4].innerHTML= averageValue;
								
			if (isSecondTerm)
				if (newAr[i][3*MAX_COL+2]!=-1)
				{
					var value= (averageValue*2+newAr[i][3*MAX_COL+2])/3; 
						value= Math.round(value * 10+0.0000001)/10;
						
					if ((value-Math.floor(value))<0.01)				
						table.rows[i+2].cells[SIZE+3].innerHTML=value+".0";
					else
						table.rows[i+2].cells[SIZE+3].innerHTML=value;

					newAr[i][3*MAX_COL+4]=value;
				}				
		}
		else
		if	(table.rows[i+2].cells[t+4].innerHTML!="MG")
		{	
			table.rows[i+2].cells[t+4].innerHTML="";
			
			newAr[i][t]=-1;
			if (isSecondTerm)
			{
				table.rows[i+2].cells[SIZE+3].innerHTML="";					
				newAr[i][SIZE+3]=-1;
			}	
		}
		if (isSecondTerm)
			if (mgHK1[i] && mgHK2[i]){
				table.rows[i+2].cells[SIZE+3].innerHTML="MG";
				table.rows[i+2].cells[SIZE+2].innerHTML="MG";
			}
			else	
			if (mgHK1[i] && (!mgHK2[i])){
				table.rows[i+2].cells[SIZE+3].innerHTML=table.rows[i+2].cells[t+4].innerHTML;					
				table.rows[i+2].cells[SIZE+1].innerHTML="MG";
			}	
			else
			if ((!mgHK1[i]) && mgHK2[i]){	
				table.rows[i+2].cells[SIZE+3].innerHTML=table.rows[i+2].cells[t+3].innerHTML;					
				table.rows[i+2].cells[SIZE+2].innerHTML="MG";
			}		
	}
	
	if (isSecondTerm)
		var maxCol  = 3*MAX_COL+5;
	else
		var maxCol  = 3*MAX_COL+3;
	
	for(var i=1;i<length;i++){
		for(var j=1;j<maxCol;j++)
			if (newAr[i][j]!= -1)
				table.rows[i+2].cells[j+4].className = addColor(table.rows[i+2].cells[j+4].className,newAr[i][j],activeMode);
	}
}

	function updateOldAr()
	{
		for(var i=1;i<length;i++)
			for(var j=1;j<SIZE;j++)
				oldAr[i][j] = tempNewAr[i][j];
	}
	function update()
	{
		//writeNew(newAr);	
		//writeNew();
		//writeOld();
		if (isComment)
			calculateNewArray(newAr);
		var str="";
		for(var i=1;i<length;i++)
		{
			var numberString="";
			var valueString ="";
			for(var j=1;j<SIZE;j++)
				if (newAr[i][j]!=oldAr[i][j] && (newAr[i][j]!='MG'))
				{					
					numberString=numberString+j+"*";
					if (isComment)
						valueString =valueString+convertToDigit(newAr[i][j].toString())+"*"; 
					else	
						valueString =valueString+newAr[i][j]+"*"; 
				}
			if (numberString!="")	
				str=str+"/"+idAr[i]+":"+numberString+":"+valueString;												
		}
		
		if (str!="")
		{
			numberId++;
			sendToServerMark(numberId+"/"+idTeacher+"/"+primary+"/"+isComment+str);
			/*
			var currentTime = (new Date()).getTime();
			if ((currentTime-latestTime)>1500)
			{
				document.getElementById("messageChanging").innerHTML="Đang lưu";
				document.getElementById("buttonSave").disabled="disabled";			
			}
			*/	
		}
		else
		{
			document.getElementById("messageChanging").innerHTML="Đã lưu";
			document.getElementById("buttonSave").disabled="disabled";			
		}	
		for(var i=1;i<length;i++)
			for(var j=1;j<SIZE;j++)
				tempNewAr[i][j] = newAr[i][j];		
		
	}
	function writeOld()
	{
		var str="";
		for(var i=1;i<length;i++)
		{
			for(var j=0;j<SIZE;j++)
			{
				str=str+oldAr[i][j]+" ";
			}		
			str=str+"<p>"
		}	
		str+="<br><br>";
		document.getElementById("myDiv2").innerHTML = str;
	}	
	function writeNew(newAr)
	{
		var str="";
		for(var i=1;i<length;i++)
		{
			for(var j=0;j<SIZE;j++)
			{
				str=str+newAr[i][j]+" ";
			}		
			str=str+"<p>"
		}	
		document.getElementById("myDiv3").innerHTML = str;
		
	}
	function setNoEdit()
	{
		for(var i=1;i<length;i++)
			for(var j=1;j<3*MAX_COL+2;j++)
			if (!enableEdit[i][j])
				table.rows[i+2].cells[j+4].className="noedit";
		if (isComment)
		{
			for(var i=1;i<length;i++)
				if (!isSecondTerm){
					if (!enableEdit[i][3*MAX_COL+2])
						table.rows[i+2].cells[3*MAX_COL+2+4].className="noedit";
				}
				else
				for(var j=3*MAX_COL+2;j<3*MAX_COL+5;j++)
					if (!enableEdit[i][j])
						table.rows[i+2].cells[j+4].className="noedit";
		}	
	}
	function viewColorForComment()
	{	
		if (isSecondTerm)
			var maxCol  = 3*MAX_COL+5;
		else
			var maxCol  = 3*MAX_COL+3;
		
		for(var i=1;i<length;i++){
			for(var j=1;j<maxCol;j++)
				if (newAr[i][j]!= -1)
					{
						var value = newAr[i][j];
						var className = table.rows[i+2].cells[j+4].className;						
						if (value =="Đ")
							className = className.replace('yeu','');
						else
						if (value =="CĐ")
							if (value.search("yeu") == -1)
								value +=" yeu";							
						table.rows[i+2].cells[j+4].className = value;
					}				
		}
		
	}
	function viewAverageCol()
	{
		if (isSecondTerm)
			var numberCol = 3*MAX_COL + 5;
		else
			var numberCol = 3*MAX_COL + 3;		
		for(var i=1;i < numberCol;i++)
		{
			var ok = false;
			var sum = 0;
			var factor = 0;
			for(var j=1;j<length;j++)
			if (newAr[j][i] != -1){
				ok = true;
				sum+=newAr[j][i];
				factor++;
			}
			if (ok) {
				var value = sum / factor;
				value = Math.round(value * 10+0.0000001)/10
				table.rows[length+2].cells[i].innerHTML = value;
			}
			else
				table.rows[length+2].cells[i].innerHTML = "";
			table.rows[length+2].cells[i].style.display = table.rows[length+1].cells[i+4].style.display;
			table.rows[length+2].cells[i].style.textAlign = table.rows[length+1].cells[i+4].style.textAlign;
		}
	}
