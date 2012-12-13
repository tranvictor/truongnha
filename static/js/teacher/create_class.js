$(document).ready(function () {
    var callback = function(json){
        var html = '<div class="row-fluid">' +
                   '<a class="span12 btn-success btn ajaxify" href="' + 
                    json.class_url +
                   '" title="Quản lý lớp ' + json.class_name + '">' +
                   '<h3>' + json.class_name + '</h3>' +
                   '<p>Sĩ số: </p>' + 
                   '<p>Ghi chú: ' + json.class_note + '</p>' + 
                   '</a> </div>'
        var newClass = $(html);
        $('#menu-classes').prepend(newClass);
    };
    $("#createClassForm").ajaxForm({
        'callback': callback});
});
