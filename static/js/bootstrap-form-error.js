function clear_bootstrap_error() {
    $(".error").removeClass('error');
    $("#id___all__").removeClass("alert alert-error");
    $("span.help-inline").remove();
    $("#id___all__").empty();
}
function add_bootstrap_error(errs) {
    $.each(errs, function (key, val) {
        if (key == '__all__'){
            $("#id___all__").append(val);
            $("#id___all__").addClass("alert alert-error");
        }
        else{
            var id = "#id_" + key;
            var err_msg = '<span class="help-inline">' + val + '</span>';
            $(id).after(err_msg);
            $(id).parent().parent().addClass('error');
        }
    });
}