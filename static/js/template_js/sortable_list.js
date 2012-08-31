/**
 * Created by PyCharm.
 * User: vutran
 * Date: 7/30/11
 * Time: 12:46 AM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function(){

    var windowHeight = $(window).height();

    
    $("#sortableList").sortable({
        placeholder: 'ui-state-highlight'
    });
    $("#sortableList").disableSelection();

    $("li.sortable").each(function(){
        $(this).hover(function(){
            $(this).addClass('ui-state-hover');
        }, function(){
            $(this).removeClass('ui-state-hover');
        });
    });

    $("li.sortable").each(function(){
        $(this).click(function(){
            if (!$(this).hasClass('ui-state-focus')){
                $(".ui-state-focus").removeClass('ui-state-focus');
                $(this).addClass('ui-state-focus');
            }
        });
    });

    $("li.sortable").each(function(){
        $(this).dblclick(function(){
            if ($(".ui-state-active").length >0){
                var oldSelected = $(".ui-state-active");
                oldSelected.children('span.icon').hide();
                oldSelected.removeClass('ui-state-active');
                $("#sortableList").append("<li id='tempNode'> </li>");
                var temp = $("#tempNode");
                oldSelected.before(temp);
                $(this).after(oldSelected);
                temp.before($(this));
                temp.remove();
            } else {
                $(this).children('span.icon').show();
                $(this).addClass('ui-state-active');
            }
        });
    });

    var theFocus = $("#sortableList > li:first").addClass('ui-state-focus');
    var saveState = $("#sortableList").html();


    $("#cancel_list_sorting").click(function(){
        $("#sortableList").html(saveState);
        $("li.sortable").each(function(){
            $(this).hover(function(){
                $(this).addClass('ui-state-hover');
            }, function(){
                $(this).removeClass('ui-state-hover');
            });
        });

        $("li.sortable").each(function(){
            $(this).click(function(){
                if (!$(this).hasClass('ui-state-focus')){
                    $(".ui-state-focus").removeClass('ui-state-focus');
                    $(this).addClass('ui-state-focus');
                }
            });
        });

        $("li.sortable").each(function(){
            $(this).dblclick(function(){
                if ($(".ui-state-active").length >0){
                    var oldSelected = $(".ui-state-active");
                    oldSelected.children('span.icon').hide();
                    oldSelected.removeClass('ui-state-active');
                    $("#sortableList").append("<li id='tempNode'> </li>");
                    var temp = $("#tempNode");
                    oldSelected.before(temp);
                    $(this).after(oldSelected);
                    temp.before($(this));
                    temp.remove();
                } else {
                    $(this).children('span.icon').show();
                    $(this).addClass('ui-state-active');
                }
            });
        });

        return false;
    })

    function scrollPage( theFocus, extra ){
        var offset = theFocus.offset().top;
        if (!extra) extra = 0;
        if (offset - $(document).scrollTop() >= windowHeight ||
            offset - $(document).scrollTop() < 0){
            // scroll the document
            $('html,body').animate({scrollTop: offset + extra}, 500);
        }
    }

    $(document).keydown( function(event){
        var theSelected = $(".ui-state-active");
        if (theSelected.length >0){
            // selected an element => moving that element to organize elements.
            if ( event.which == 38){
                // up arrow key
                var prev = theSelected.prev('li.sortable');
                if (prev.length > 0){
                    prev.before(theSelected);
                    scrollPage(prev, -windowHeight/2);
                }
            } else if ( event.which == 40){
                // down arrow key
                var next = theSelected.next('li.sortable');
                if (next.length >0) {
                    next.after(theSelected);
                    scrollPage(next, -windowHeight/2);
                }
            } else if ( event.which == 13){
                theSelected.removeClass('ui-state-active');
                theSelected.children('span.icon').hide();
            }
        } else {
            theFocus = $(".ui-state-focus");
            if ( event.which == 38){
                var prev = theFocus.prev('li.sortable');
                if ( prev.length > 0){
                    prev.addClass('ui-state-focus');
                    theFocus.removeClass('ui-state-focus');
                    scrollPage(prev, -windowHeight/2);
                }
            } else if ( event.which == 40){
                var next = theFocus.next('li.sortable');
                if ( next.length > 0) {
                    next.addClass('ui-state-focus');
                    theFocus.removeClass('ui-state-focus');
                    scrollPage(next, -windowHeight/2);
                }

            } else if ( event.which == 13){
                theFocus.children('span.icon').show();
                theFocus.addClass('ui-state-active');
            }
        }

        return false;
    });

    // save button
    $("#save").click( function(){
        var data = "";
        $("#sortableList > li").each(function(){
            var id = $(this).attr('id');
            var index = $(this).parents().children().index($(this)) + 1;
            data = data + id + '_' + index + '/';
        });

        var arg = { type:"POST",
            url: $("#ajax_to").text(),
            data:{data: data},
            datatype:"json",
            success: function(){
                // restore original state of table
                saveState = $("#sortableList").html();
                $('span#index').each(function(){
                    var theLi = $(this).parents('li');
                    $(this).text(theLi.parents().children().index(theLi) +1 );
                    saveState = $("#sortableList").html();
                });
            }
        };
        $.ajax(arg);
    })



});