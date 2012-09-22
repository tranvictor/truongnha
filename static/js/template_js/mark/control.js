// this file contains the functions which to control mark table
// for example add columns, delete columns, validate data, move to another cell

function focusCell(cell)
{
	if (!enableChangeMark)
		return;
	var cellIndex = cell.cellIndex;
	var rowIndex  = cell.parentElement.rowIndex;	
	if (!enableEdit[rowIndex-2][cellIndex-4]) 
		return;	
	
	if (!firstClick)
		mainInput.parentElement.innerHTML=mainInput.value;
	else
		mainInput.style.display="";
	firstClick=false;
		
	mainInput.value=cell.innerHTML;
	cell.innerHTML="";
	if (isComment)
		validateComment()
	else	
		acceptDigits();
	cell.appendChild(mainInput);
	mainInput.focus();	
}
function returnMove()
{
	return move;
}
function direction(cell,valueOfMove)
{
	var lengthList = length - 1;	
	var colIndex = cell.cellIndex; 
	var rowIndex  = cell.parentNode.rowIndex;	
	if (valueOfMove==1)			
	while(true){
		if (rowIndex-2==lengthList)
			break;
		else		
			rowIndex+=1;	
		if (enableEdit[rowIndex-2][colIndex-4]) 	
			break;		
	}
	else
	while(true){
		if (colIndex-4==SIZE)
			break;
		else
			if (colIndex==4+maxColMieng)
				colIndex=5+MAX_COL;
			else	
			if (colIndex==4+MAX_COL+maxCol15Phut)
				colIndex=5+2*MAX_COL;
			else		
			if (colIndex==4+2*MAX_COL+maxColMotTiet)
				colIndex=5+3*MAX_COL;					
			else		
				colIndex+=1;							
		if (enableEdit[rowIndex-2][colIndex-4]) 	
			break;								
	}
	if (enableEdit[rowIndex-2][colIndex-4]){
		mainInput.parentElement.innerHTML=mainInput.value;			
		mainInput.value= table.rows[rowIndex].cells[colIndex].innerHTML;
		table.rows[rowIndex].cells[colIndex].innerHTML="";
		table.rows[rowIndex].cells[colIndex].appendChild(mainInput);	
		if (isComment)
			validateComment()
		else	
			acceptDigits();	
		mainInput.focus();
	}	
}	
function acceptDigits()
{
		
		/*
		if (tb.value=="-")
		{
			tb.value="10";
			return;
		}
		*/
		
		var exp = /[^((\d).,)]/g;
		mainInput.value=mainInput.value.replace(exp,'');		
		
		var exp1 = /[,]/g;
		mainInput.value=mainInput.value.replace(exp1,'.');		
		
		
		var value=mainInput.value;
		//kiem tra xem no co nhieu hon hai dau cham hay ko
		
		var countDot=0;
		for(var i=0;i<value.length;i++)
			if (value.charAt(i)==".") 
				countDot++;
				
		if (countDot>1)
			mainInput.value=value.substring(0,value.length-1);
			
		if (mainInput.value.length>4)	
			mainInput.value=mainInput.value.substring(0,4);
			
		var number=parseFloat(mainInput.value);
		if ((10<number ) && (number<100))
		{
			var temp=number/10;
			mainInput.value=temp.toString();
		}
		if (number>=100)
			mainInput.value=mainInput.value.substring(0,2);				
		if ((mainInput.value.length==2) && (mainInput.value[0]=='0'))
		{
			var temp = number / 10;
			mainInput.value = temp.toString();
		}		
}
function isEmptyCol(colIndex,excepCol)
{
	if (excepCol==undefined) 
		excepCol=0;
	for(var i=1;i<length;i++)
		if ((table.rows[i+2].cells[colIndex].innerHTML.trim()!="") && (i+2!=excepCol))
			return false;
	if (excepCol>0)		
		if (mainInput.value.length>0)
			return false;
	return true;
}	
function setDisplayCol(colIndex,value)
{
	table.rows[1].cells[colIndex-5].style.display=value;
	table.rows[2].cells[colIndex-3].style.display=value;
	for(var i=1;i<length;i++)	
		table.rows[i+2].cells[colIndex].style.display=value;	
}
function addColMieng(rowIndex,colIndex)
{
	var ok=false;
	if ((colIndex==4+maxColMieng ) && (maxColMieng<	MAX_COL)){
		if (mainInput.value.length>0)
		{
			document.getElementById("colMieng").colSpan+=1;
			maxColMieng+=1;		
			setDisplayCol(colIndex+1,"");
		}
	}	
	else
		if ((colIndex==3+maxColMieng ) && (maxColMieng>MAX_VIEW_COL_MIENG )){	
			if (isEmptyCol(colIndex,rowIndex) && isEmptyCol(colIndex+1)  && (mainInput.value.length==0))
			{
				document.getElementById("colMieng").colSpan-=1;
				maxColMieng-=1;		
				//alert("chao1");
				setDisplayCol(colIndex+1,"none");					
				while ((maxColMieng > MAX_VIEW_COL_MIENG)){
					if (isEmptyCol(colIndex-1))
					{
						document.getElementById("colMieng").colSpan-=1;
						setDisplayCol(colIndex,"none");
						maxColMieng-=1;
						colIndex--;	
					}
					else break;	
				}
				
				table.rows[rowIndex].cells[colIndex].appendChild(mainInput);
				mainInput.focus();
			}	
		}		
}
function addCol15Phut(rowIndex,colIndex)
{
	var ok=false;
	if ((colIndex==4+MAX_COL+maxCol15Phut ) && (maxCol15Phut<	MAX_COL)){
		if (mainInput.value.length>0)
		{
			document.getElementById("col15Phut").colSpan+=1;
			maxCol15Phut+=1;		
			setDisplayCol(colIndex+1,"");
		}
	}	
	else
		if ((colIndex==3+MAX_COL+maxCol15Phut ) && (maxCol15Phut>MAX_VIEW_COL_15PHUT )){	
			if (isEmptyCol(colIndex,rowIndex) && isEmptyCol(colIndex+1)  && (mainInput.value.length==0))
			{
				document.getElementById("col15Phut").colSpan-=1;
				maxCol15Phut-=1;		
				//alert("chao1");
				setDisplayCol(colIndex+1,"none");					
				while ((maxCol15Phut>MAX_VIEW_COL_15PHUT )){
					if (isEmptyCol(colIndex-1))
					{
						document.getElementById("col15Phut").colSpan-=1;
						setDisplayCol(colIndex,"none");
						maxCol15Phut-=1;
						colIndex--;	
					}
					else break;	
				}
				
				table.rows[rowIndex].cells[colIndex].appendChild(mainInput);
				mainInput.focus();
			}	
		}		
}
function addColMotTiet(rowIndex,colIndex)
{
	var ok=false;
	if ((colIndex==4+2*MAX_COL+maxColMotTiet ) && (maxColMotTiet<	MAX_COL)){
		if (mainInput.value.length>0)
		{
			document.getElementById("colMotTiet").colSpan+=1;
			maxColMotTiet+=1;		
			setDisplayCol(colIndex+1,"");
		}
	}	
	else
		if ((colIndex==3+2*MAX_COL+maxColMotTiet ) && (maxColMotTiet>MAX_VIEW_COL_MOT_TIET )){	
			if (isEmptyCol(colIndex,rowIndex) && isEmptyCol(colIndex+1)  && (mainInput.value.length==0))
			{
				document.getElementById("colMotTiet").colSpan-=1;
				maxColMotTiet-=1;		
				//alert("chao1");
				setDisplayCol(colIndex+1,"none");					
				while ((maxColMotTiet>MAX_VIEW_COL_MOT_TIET )){
					if (isEmptyCol(colIndex-1))
					{
						document.getElementById("colMotTiet").colSpan-=1;
						setDisplayCol(colIndex,"none");
						maxColMotTiet-=1;
						colIndex--;	
					}
					else break;	
				}
				
				table.rows[rowIndex].cells[colIndex].appendChild(mainInput);
				mainInput.focus();
			}	
		}		
}
function addCol()
{
	var cell     = mainInput.parentElement; 
	var colIndex = cell.cellIndex;
	var rowIndex = cell.parentNode.rowIndex;
	addColMieng(rowIndex,colIndex);
	addCol15Phut(rowIndex,colIndex);
	addColMotTiet(rowIndex,colIndex);	
}

function validateComment()
{
	var ok=true;	
	var value=mainInput.value.toLowerCase();;
	var length=value.length;
	
	if ((value!="đ") && (value!="cđ") && (value!="c"))	
		mainInput.value=value.substring(0,length-1).toUpperCase();
	
	
	if ((value=='đ') || (value=='d'))
		mainInput.value='Đ'
	else
	if ((value=='cđ') || (value=='c') )
		mainInput.value='CĐ';	
}

function  control(cell,event)
{
	timetime1 = (new Date()).getTime();
	if (isComment)
		validateComment();
	else	
		acceptDigits();
	addCol();	
	
	//ntrolDirection(tb,event);				
	/*
	var keyCode = event.keyCode;
	if ((keyCode==37) || (keyCode==38)|| (keyCode==39) || (keyCode==40)
		|| (keyCode==32) || (keyCode==13) || (keyCode==9))
		tb.select();
	*/	
}	
		
function controlDirection(cell,event)
{
	//ert("ttt");
	//alert(event);
	var keycode=event.keyCode;
	var colIndex = cell.cellIndex; 
	var rowIndex  = cell.parentNode.rowIndex;
	var lengthList = length - 1;	
	var	 ok=false;
	if ((keycode==32) | (keycode==13) | (keycode==9))
	{
		valueOfMove=returnMove();
		direction(cell,valueOfMove);
	}	
	else
	{	
		if ((keycode==40))
		{
			while(true){
				if (rowIndex-2==lengthList)
					break;
				else
					rowIndex+=1;	
				if (enableEdit[rowIndex-2][colIndex-4]) 	
				{
					ok=true;
					break;	
				}	
			}
		}
		else
		if (keycode==38)
		{
			while(true){
				if (rowIndex-2==1)
					break;
				else
					rowIndex-=1;	
				if (enableEdit[rowIndex-2][colIndex-4]) 	
				{
					ok=true;
					break;	
				}	
			}
		}
		else
		if (keycode==37)
		{	
			while(true){
				if (colIndex-4==1)
					break;
				else
				if (colIndex==5+MAX_COL)
					colIndex=4+maxColMieng;
				else	
				if (colIndex==5+2*MAX_COL)
					colIndex=4+MAX_COL+maxCol15Phut;
				else		
				if (colIndex==5+3*MAX_COL)
					colIndex=4+2*MAX_COL+maxColMotTiet;					
				else		
					colIndex-=1;
					
				if (enableEdit[rowIndex-2][colIndex-4]) 	
				{
					ok=true;
					break;	
				}	
			}	
		}
		else
		if (keycode==39)
		{	
			while(true){
				if (colIndex-4==SIZE)
					break;
				else				
				if (colIndex==4+maxColMieng)
					colIndex=5+MAX_COL;
				else	
				if (colIndex==4+MAX_COL+maxCol15Phut)
					colIndex=5+2*MAX_COL;
				else		
				if (colIndex==4+2*MAX_COL+maxColMotTiet)
					colIndex=5+3*MAX_COL;					
				else		
					colIndex+=1;
					
				if (enableEdit[rowIndex-2][colIndex-4]) 	
				{
					ok=true;
					break;	
				}	
			}		
		}
		if (ok){
			mainInput.parentElement.innerHTML=mainInput.value;			
			mainInput.value= table.rows[rowIndex].cells[colIndex].innerHTML;
			table.rows[rowIndex].cells[colIndex].innerHTML="";
			table.rows[rowIndex].cells[colIndex].appendChild(mainInput);
			if (isComment)
				validateComment();
			else	
				acceptDigits();	
				
			mainInput.focus();
			
		}	
	}	
	timetime2 = (new Date()).getTime();
	//alert(timetime2-timetime1);
}
	$(document).ready(function() {
		var time1 = new Date().getTime();
		$("#markTable").delegate('td[id^="cell_"]',"click",function(){
			focusCell(this);
			checkToSend(this);
		});
		$("#markTable").delegate('td[id^="cell_"]',"keyup",function(event){
			control(this,event); 
			controlDirection(this,event);							
		});
		$("#markTable").delegate('td[id^="cell__"]',"click",function(){
			select(this);
		});
		$("#markTable").delegate('th[id^="col_"]',"click",function(){
			checkCol(this);
		});
		$("#nextcell").click(function(){
			if (move == 1){ 
				$("#textNextcell").text("Nhập điểm theo cột");
			}	
			else{	
				$("#textNextcell").text("Nhập điểm theo hàng");
			}	
			move = 1 - move;
		});
		var time2 = new Date().getTime();
		console.log(time2-time1);	
	});			
