/**
 * @depends jquery
 * @name jquery.tnTable
 */

/**
 * jQuery Aliaser
 */
(function(window, undefined){
    // Prepare
    var $table;
    var internalMethods = {
        select : function() {
            var $row = $(this);
            if ($row.hasClass('selectable')) {
                var id = $row.attr('data-id');
                var checkBoxId = '#checkbox_' + id;
                var checkBoxAll = '#checkbox_all';
                var n;
                if ($row.hasClass('selected')) {
                    $row.removeClass('selected');
                    $(checkBoxId).prop("checked", false);
                    n = --$table.data('tnTable').numSelected;
                    if (n == 0) {
                        $(checkBoxAll).prop("checked", false);
                    }
                } else {
                    $row.addClass('selected');
                    $(checkBoxId).prop("checked", true);
                    $(checkBoxAll).prop("checked", true);
                    $table.data('tnTable').numSelected++;
                }
            }
            //Can add callback here
        },
        selectAll : function(){
            var selectables = $table.find('.selectable');
            var checkBoxAll = '#checkbox_all';
            var num = 0;
            var len = selectables.length;
            for (i=len; i--;){
                var $row = $(selectables[i]);
                if ($row.css('display') != 'none'){
                    num ++;
                }
                if (!$row.hasClass('selected')){
                    var checkBox = $('#checkbox_' + $row.attr('data-id'));
                    checkBox.prop('checked', true);
                    $row.addClass('selected');
                }
            }
            $(checkBoxAll).prop('checked', true);
            $table.data('tnTable').numSelected = num;
        },
        deselectAll : function(){
            var selectables = $table.find('.selectable');
            var checkBoxAll = '#checkbox_all';
            var len = selectables.length;
            for (i=len; i--;){
                var $row = $(selectables[i]);
                if ($row.hasClass('selected')){
                    var checkBox = $('#checkbox_' + $row.attr('data-id'));
                    checkBox.prop('checked', false);
                    $row.removeClass('selected');
                }
            }
            $(checkBoxAll).prop('checked', false);
            $table.data('tnTable').numSelected = 0;
        }
    };
    var methods = {
        init : function( options ) {
            return this.each(function(){
                $table = $this = $(this); //The table
                var data = $this.data('tnTable');
                // If the plugin hasn't been initialized yet
                if (!data){
                    $(this).data('tnTable', {
                        numSelected : 0
                    });
                    $this.delegate('.selectable',
                            'click', internalMethods.select);
                    $('#checkbox_all').click(function(){
                        if (!$(this).is(':checked')) internalMethods.deselectAll()
                        else internalMethods.selectAll()
                    });
                }});
        },
        getNumSelected : function(){
            return $table.data('tnTable').numSelected;
        },
        getSelected : function(){
            return $table.find('selected')
        }
    }

    $.fn.tnTable = function( method ) {

        if ( methods[method] ) {
            return methods[method].apply( this,
                    Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.tnTable' );
        }    

    };
})(window);

