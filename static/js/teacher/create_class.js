$(document).ready(function () {
    var callback = function(json){
        var html = '<div class="row-fluid">' +
                   '<a class="span12 btn-success btn ajaxify" href="' + 
                    json.class_url + '" ' +
                   'id="class-' + json.class_id + '" ' +
                   'title="Quản lý lớp ' + json.class_name + '">' +
                   '<h3 class="pull-left">' + json.class_name + '</h3>' +
                   '<p title="Sĩ số" class="pull-right">0</p>' + 
                   '</a> </div>'
        var newClass = $(html);
        $('#menu-classes').prepend(newClass);
    };
    $("#createClassForm").ajaxForm({
        'callback': callback});
});
