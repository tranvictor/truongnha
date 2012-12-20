/**
 * Created with PyCharm.
 * User: Admin
 * Date: 12/20/12
 * Time: 11:32 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function () {
    var callback = function(json){
        window.location = json.class_url;
    };
    $("#createStudentForm").ajaxForm({
        'callback': callback});
});
