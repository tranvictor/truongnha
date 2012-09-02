
// It contains the function which to initiate data using in mark table.
// It also has the functions to set sent scores, set uneditable scores 
// and contains some utility functions to convert data from digital score to comment score 
// and reverse.
function setArrayId(id)
{
	indexId++;
	idAr[indexId] = id;
}
function checkSent(x)
{
	if (x=='1')
		return 1;
	else 
		return 0;
}
function setSentMark(str)
{
	//alert(str);
	var sents=str.split('|')
	for (var i in sents){
		var ss=sents[i].split('*')
		for (var j in ss){		
			if (i<3)
				sentMark[indexId][parseInt(i)*MAX_COL+parseInt(j)+1]=checkSent(ss[j]);
			else
			if (isSecondTerm && (3*MAX_COL+parseInt(i)-2==3*MAX_COL+2))
				sentMark[indexId][3*MAX_COL+3]=checkSent(ss[j]);
			else	
				sentMark[indexId][3*MAX_COL+parseInt(i)-2]=checkSent(ss[j]);
		}		
	}
}

function setSentHk1(str)
{
	//alert(str);
	var sents=str.split('|')
	if (sents[4])
		sentMark[indexId][3*MAX_COL+2]=1;
}

function convertToDigit(value)
{
	var value1=value.toLowerCase();
	
	if (value1=="đ")
		return 7
	else	
	if (value1=='cđ')	
		return 1
	else
		return -1;
}
function convertToChar(value)
{
	value=value.trim();
	
	if (value=="")
		value=-1;
		
	if (value>=5)
		return "Đ";
	else
	if (value>=0)			
		return "CĐ";
	else
		return "";			
}

function convertToComment()
{
	console.log("chao");
	for (var i=1;i<length;i++)
		for(var j=1;j<SIZE;j++)
			if (table.rows[i+2].cells.length>j+5)			
				table.rows[i+2].cells[j+4].innerHTML = convertToChar(table.rows[i+2].cells[j+4].innerHTML)
}	
function setEditable(data)
{
	
	if (!enableChangeMark)
		return;
	var datas=data.split('|');			
	for (var i in datas){
		var ds=datas[i].split('*')
		for (var j in ds){				
			if (ds[j]=="")
				time=timeNow;					
			else
				time=parseInt(ds[j]);
			//alert(timeNow-time);	
			if ((timeNow-time) >timeToEdit+0.00001)
			{
				if (i<3)
					enableEdit[indexId][parseInt(i)*MAX_COL+parseInt(j)+1]=0;
				else
				if (isSecondTerm && (3*MAX_COL+parseInt(i)-2==3*MAX_COL+2))
					enableEdit[indexId][3*MAX_COL+3]=0;
				else
					enableEdit[indexId][3*MAX_COL+parseInt(i)-2]=0;
			}
			else{
				if (i<3)
					enableEdit[indexId][parseInt(i)*MAX_COL+parseInt(j)+1]=1;
				else	
				if (isSecondTerm && (3*MAX_COL+parseInt(i)-2==3*MAX_COL+2))
					enableEdit[indexId][3*MAX_COL+3]=1;
				else	
					enableEdit[indexId][3*MAX_COL+parseInt(i)-2]=1;
			}				
		}		
	}
}
function setSentTbNam(data)
{
	if (data=="True")
		sentMark[indexId][3*MAX_COL+4]=1;
	else	
		sentMark[indexId][3*MAX_COL+4]=0;
}
function setEditableTbNam(time)
{
	if (time=="None")  return;
	if ((timeNow-time)/60.0 >timeToEdit)
		enableEdit[indexId][3*MAX_COL+4] = 0;	
}
function convertBeforeSend(data,isComment)
{
	if (!isComment) 
		return data
	else
	if (data=="Đ")
		return "D"
	else
	if (data=="CĐ")
		return "CD"
	else	
	if (data=="MG")
		return "duoc mien giam"
	else
		alert("loi");		
}
