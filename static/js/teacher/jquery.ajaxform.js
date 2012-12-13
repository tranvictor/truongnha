/**
 * @depends jquery
 * @name jquery.ajaxForm
 */

/**
 * jQuery Aliaser
 */
(function(window, undefined){
    // Prepare
    var init = function( options ) {
        return this.each(function(){
            var $this = $(this);
            var data = $this.data('ajaxForm');
               // If the plugin hasn't been initialized yet
            if (!data){
                var url;
                if (options && 'url' in options){
                    url = options['url'];
                } else {
                    url = $this.attr('action');
                    if (url == undefined){
                        url = '';
                    }
                }
                var type;
                if (options && 'type' in options){
                    type = options['type'];
                } else {
                    type = $this.attr('method');
                    if (type == undefined){
                        type = 'post';
                    }
                }
                var success;
                if (options && 'success' in options){
                    var temp = options['success'];
                    if (typeof temp === 'function'){
                        success = temp;
                    } else {
                        $.error( 'Sucess option must be a function. ');
                        return false;
                    }
                } else {
                    success = methods.success;
                }
                var error;
                if (options && 'error' in options){
                    var temp = options['error'];
                    if (typeof temp === 'function'){
                        error = temp;
                    } else {
                        $.error( 'Error option must be a function. ');
                        return false;
                    }
                } else {
                    error = methods.error;
                }
                $(this).data('ajaxForm', {
                    target : $this,
                    url : url,
                    success : success,
                    error : error
                });
                // bind post event
                $this.bind('submit', function(){
                    $this.find(".error").removeClass('error');
                    $this.find("span.help-inline").remove();
                    var d = $this.serialize();
                    var arg = {
                        data: d,
                        type: type,
                        url: url,
                        error: error,
                        success: success,
                        global: false,
                    }
                        $.ajax(arg);
                    return false;
                });
            }
        });
    };

    var add_bootstrap_error = function(errs) {
        console.log(errs);
        $.each(errs, function (key, val) {
            var id = "#" + key;
            var err_msg = '<span class="help-inline">' + val + '</span>';
            $(id).after(err_msg);
            $(id).parent().parent().addClass('error');
        });
    };

    var success = function(json){
        console.log(json);
        $('#notify').showNotification(json.message, 3000);
        if (json.success == false){
            add_bootstrap_error(json.error);
        }
        return false;
    };

    var error = function(json){
        $('#notify').showNotification('Hệ thống gặp lỗi khi kết nối tới máy chủ', 3000);
        return false;
    }

    var methods = {
        init : init,    
        error : error,
        success : success
    };

    $.fn.ajaxForm = function( method ) {

        if ( methods[method] ) {
            return methods[method].apply( this,
                    Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.ajaxForm' );
        }    

    };
})(window);

