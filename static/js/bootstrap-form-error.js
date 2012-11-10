function clear_bootstrap_error() {
    $(".error").removeClass('error');
    $("span.help-inline").remove();
}
function add_bootstrap_error(errs) {
    $.each(errs, function (key, val) {
        var id = "#" + key;
        var err_msg = '<span class="help-inline">' + val + '</span>';
        $(id).after(err_msg);
        $(id).parent().parent().addClass('error');
    });
}