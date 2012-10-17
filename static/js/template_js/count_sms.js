$(document).ready(function(){
    triggerTooltip = function(){
        $(this).tooltip('show');
        return false;
    };
    $('#sms-table').delegate('.click-tooltip', 'click', triggerTooltip);
});
