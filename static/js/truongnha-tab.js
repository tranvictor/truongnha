/**
 * Created by PyCharm.
 * User: vutran
 * Date: 2/17/12
 * Time: 8:54 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function(){
    // toggle tab
    // all of the li tag under an ul that classed tabTreeList will be considered as tab labels
    $("#tabTreeList > li").each(function(){
        $(this).bind('click', function(){
            if (!$(this).hasClass('truongnha-current-tab')){
                $(".truongnha-current-tab").removeClass('truongnha-current-tab');
                $(this).addClass('truongnha-current-tab')
            }
            return false;
        });
    });
    $(".default-tab").removeClass('default-tab').trigger('click');

});