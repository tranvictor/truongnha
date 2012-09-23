//			the functions for sending sms

function setEmpty() {
    for (var i = 1; i < length; i++)
        for (var j = 1; j < SIZE; j++)
            if (table.rows[i + 2].cells.length > j + 5) {
                if (enableEdit[i][j])
                    table.rows[i + 2].cells[j + 4].className = "normal";
                else if (((j < 3 * MAX_COL + 2) || (isComment)) && (enableChangeMark))
                    table.rows[i + 2].cells[j + 4].className = "noedit";
                else
                    table.rows[i + 2].cells[j + 4].className = "normal";
            }
}
function showMessageTable(mode) {
    if (mode == 0) {
//        Nhập điểm
        cancelAll();
        setEmpty();
        document.getElementById("show_SMS_buttons").style.display = "";
        document.getElementById("hide_SMS_buttons").style.display = "none";
        activeMode = 0;

        for (var i = 1; i < length; i++) {
            var name = "rowCheckbox" + i;
            document.getElementById(name).style.display = "none";
        }
        for (var i = 1; i < SIZE; i++) {
            var name = "colCheckbox" + i;
            if (document.getElementById(name))
                document.getElementById(name).style.display = "none";
        }
        document.getElementById("checkAllRow").style.display = "none";
    }
    else {
//            Nhắn tin
        cancelAll();
        document.getElementById("show_SMS_buttons").style.display = "none";
        document.getElementById("hide_SMS_buttons").style.display = "";
        activeMode = 1;
        for (var i = 1; i < length; i++) {
            var name = "rowCheckbox" + i;
            document.getElementById(name).style.display = "";
        }
        for (var i = 1; i < SIZE; i++) {
            var name = "colCheckbox" + i;
            if (document.getElementById(name))
                document.getElementById(name).style.display = "";
        }
        document.getElementById("checkAllRow").style.display = "";
    }
}
function selectAllToSend() {
    for (var i = 1; i < length; i++)
        for (var j = 1; j < SIZE; j++)
            if (newAr[i][j] != -1)
                table.rows[i + 2].cells[j + 4].className = "selected";

    for (var i = 1; i < length; i++)
        for (var j = 0; j < 5; j++)
            table.rows[i + 2].cells[j].className = "selected";

    for (var i = 1; i < length; i++) {
        //table.rows[i+2].className="selected";
        var name = "rowCheckbox" + i;
        document.getElementById(name).checked = true;
    }

    for (var i = 1; i < SIZE + 5; i++) {
        var name = "colCheckbox" + i;
        if (document.getElementById(name))
            document.getElementById(name).checked = true;

        if ((table.rows[2].cells[i-1]) && (i!= 3 && i!=4 && (i!=5)))
            table.rows[2].cells[i-1].className = "selected";
    }
    document.getElementById("checkAllRow").checked = true;
}
function cancelAll() {
    for (var i = 1; i < length; i++)
        for (var j = 1; j < SIZE; j++)
            if ((table.rows[i + 2].cells.length > j + 5) && (newAr[i][j] != -1))

                if (sentMark[i][j] == 1)
                    table.rows[i + 2].cells[j + 4].className = "sent";
                else if (!enableEdit[i][j] && ((j < 3 * MAX_COL + 2) || (isComment)) && (enableChangeMark))
                    table.rows[i + 2].cells[j + 4].className = "noedit";
                else if (i % 2 == 1)
                    table.rows[i + 2].cells[j + 4].className = "mark-odd";
                else
                    table.rows[i + 2].cells[j + 4].className = "mark-even";
    for (var i = 1; i < length; i++)
        for (var j = 0; j < 5; j++)
            table.rows[i + 2].cells[j].className = "";

    for (var i = 1; i < length; i++) {
        table.rows[i + 2].className = "";
        var name = "rowCheckbox" + i;
        document.getElementById(name).checked = false;
    }
    for (var i = 1; i < SIZE + 5; i++) {
        var name = "colCheckbox" + i;
        if (document.getElementById(name))
            document.getElementById(name).checked = false;
        if ((table.rows[2].cells[i-1]) && (i!= 3 && i!=4 && (i!=5)))
            table.rows[2].cells[i - 1].className = "";
    }
    document.getElementById("checkAllRow").checked = false;
}
function selectNoSent() {
    cancelAll();
    for (var i = 1; i < length; i++)
        for (var j = 1; j < SIZE; j++)
            if ((newAr[i][j] != -1) && (sentMark[i][j] == 0)) {
                table.rows[i + 2].cells[j + 4].className = "selected";
            }
}

function checkToSend(tb) {
    var rowIndex = tb.parentNode.rowIndex;
    var cellIndex = tb.cellIndex;
    /*
     if (enableEdit[rowIndex-2][cellIndex-4])
     document.getElementById(name).focus();
     */
    if ((activeMode == 1) && (newAr[rowIndex - 2][cellIndex - 4] != -1)) {
        if (tb.className != "selected")
            tb.className = "selected";
        else if (sentMark[rowIndex - 2][cellIndex - 4])
            tb.className = "sent";
        else if ((!enableEdit[rowIndex - 2][cellIndex - 4]) && ((cellIndex - 4 < 3 * MAX_COL + 2) || (isComment)) && (enableChangeMark))
            tb.className = "noedit";
        else if (rowIndex % 2 == 1)
            tb.className = "mark-odd";
        else
            tb.className = "mark-even";
    }
}
function doneSMS(data) {
    var message = data.message;
    console.log(message);

    var sum = 0, successSum = 0;
    var ok = false;
    for (var i = 1; i < length; i++) {
        var str = "-" + idAr[i] + "-";
        var answerIdx = message.search(str);
        if (answerIdx != -1) {
            successSum += 1;
            for (var j = 1; j < SIZE; j++)
                if (tempSent[i][j] == 1)
                    sentMark[i][j] = 1;
        }
        ok = false;
        for (var j = 1; j < SIZE; j++)
            if (tempSent[i][j] == 1)
                ok = true;
        if (ok)
            sum += 1;
    }

    var str = "Đã gửi thành công " + successSum + " / " + sum + " học sinh";
    $("#notify").showNotification(str, 10000);
    cancelAll();
}
function sendToServerSMS(data) {
    var arg = {
        beforeSend:function (xhrObj) {
            xhrObj.setRequestHeader("X-CSRFToken", cookieValue);
        },
        type:"POST",
        global:false,
        url:"/school/sendSMSMark",
        data:{data:data, request_type:'sms'},
        datatype:"json",
        success:function (d) {
            doneSMS(d);
        }
    };
    $.ajax(arg);
}
function emptyTempSent() {
    for (var i = 1; i < length; i++)
        for (var j = 1; j < SIZE; j++)
            tempSent[i][j] = 0;
}
///////////////////////////////////
function sendSMS() {
    if (!isComment)
        viewAverage();
    var str = "";
    emptyTempSent();
    for (var i = 1; i < length; i++) {
        var number = "";
        var value = "";
        var ok = false;
        for (var j = 1; j < SIZE; j++)
            if (newAr[i][j] != -1)
                if (table.rows[i + 2].cells[j + 4].className == "selected") {
                    ok = true;
                    number = number + j + "*";
                    value = value + convertBeforeSend(newAr[i][j], isComment) + "*";
                    tempSent[i][j] = 1;
                }
        if (ok)
            str = str + "/" + idAr[i] + ":" + number + ":" + value;
    }

    if (str != "") {
        $("#notify").showNotification("Đang gửi tin nhắn...", 10000);
        sendToServerSMS(str);
        //$("#notify").showNotification("Đang gửi tin nhắn...", 2000);
    }
    else
        $("#notify").showNotification("Chưa chọn điểm nào để gửi.", 2000);
}
function select(tb) {
    if (activeMode == 0) return;
    var number = tb.parentNode.rowIndex;
    var name = "rowCheckbox" + (number - 2);
    if (document.getElementById(name).checked) {
        document.getElementById(name).checked = false;
        var i = number - 2;
        for (var j = 1; j < SIZE; j++)
            if (newAr[i][j] != -1)
                if (sentMark[i][j] == 1)
                    table.rows[i + 2].cells[j + 4].className = "sent";
                else if ((!enableEdit[i][j]) && ((j < 3 * MAX_COL + 2) || (isComment)) && (enableChangeMark))
                    table.rows[i + 2].cells[j + 4].className = "noedit"
                else if (i % 2 == 1)
                    table.rows[i + 2].cells[j + 4].className = "mark-odd";
                else
                    table.rows[i + 2].cells[j + 4].className = "mark-even";
        for (var j = 0; j < 5; j++)
            table.rows[i + 2].cells[j].className = "";
    }
    else {
        document.getElementById(name).checked = true;
        var i = number - 2;
        for (var j = 1; j < SIZE; j++)
            if (newAr[i][j] != -1)
                table.rows[i + 2].cells[j + 4].className = "selected";

        for (var j = 0; j < 5; j++)
            table.rows[i + 2].cells[j].className = "selected";
    }
}
function checkCol(tb, rowIndex) {
    if (activeMode == 0) return;
    var rowIndex = tb.parentElement.rowIndex;
    if (rowIndex == 1)
        var number = tb.cellIndex + 1;
    else
        var number = tb.cellIndex - 4;
			
    var boxName = "colCheckbox" + number;

    var temp = document.getElementById(boxName)

    if (tb.className == "selected") {
        table.rows[2].cells[number + 4].className = "";
        temp.checked = false;
    }
    else {
        table.rows[2].cells[number + 4].className = "selected";
        temp.checked = true;
    }


    if (temp.checked == true) {
        for (var i = 1; i < length; i++)
            if (newAr[i][number] != -1)
                table.rows[i + 2].cells[number + 4].className = "selected";
    }
    else {
        for (var i = 1; i < length; i++)
            if (newAr[i][number] != -1)
                cancelCell(i, number);
    }
}

function cancelCell(x, y) {
    var tb = table.rows[x + 2].cells[y + 4];
    if (sentMark[x][y] == 1)
        tb.className = "sent";
    else if ((!enableEdit[x][y]) && ((y < 3 * MAX_COL + 2) || (isComment)) && (enableChangeMark))
        tb.className = "noedit"
    else if (x % 2 == 1)
        tb.className = "mark-odd";
    else
        tb.className = "mark-even";
}

function checkAll(tb) {
    if (tb.checked == false)
        cancelAll()
    else
        selectAllToSend();
}

//writeNew(enableEdit);
