//
//
//
//
(function(window, undefined){
    var History = window.History;
    var document = window.document;
    var $window = $(window);
    // Check if Browser provides history features
    if (!History.enabled) return false;
    // Now we have history feature
    // Wait for document to be completed
    $(document).ready(function(){
        var rootUrl = History.getRootUrl();
        var $content = $('#inner-content');
        console.log(rootUrl);
        console.log($content);
        // This function ajaxifies for <a> element
        $.fn.ajaxify = function(){
            $this = $(this);
            $this.delegate('a.ajaxify', 'click', function(event){
                var $this = $(this);
                var url = $this.attr('href');
                var title = $this.attr('title');
                console.log(url);
                console.log(title);
                // Enable this continue if cmd or ctr button are hit
                // if ( event.which == 2 || event.metaKey ) { return true; }

                // Ajaxify this link
                History.pushState(null, title, url);
                event.preventDefault();
                return false;
            });
            return $this;
        };

        var headerToDiv = function(html){
			var result = String(html)
				.replace(/<\!DOCTYPE[^>]*>/i, '')
				.replace(/<(html|head|body|title|meta|script)([\s\>])/gi,
                        '<div class="document-$1"$2')
				.replace(/<\/(html|head|body|title|meta|script)\>/gi,
                        '</div>');

			return result;
		};

        $body = $(document.body);
        $body.ajaxify();
        console.log($body);
        $window.bind('statechange', function(){
            console.log('statechange is fired');
            var state = History.getState();
            var url = state.url;
            var relativeUrl = url.replace(rootUrl, '');
            // Notify user about the loading
            
            $content.animate({opacity:0}, 800);

            $.ajax({
                url: url,
                success: function(res, textStatus, jqXHR){
                    console.log('succeeded');
                    console.log(res.content);
                    loadedContent = $(headerToDiv(res.content))[0];
                    $loadedContent = $(loadedContent);
                    console.log($loadedContent);
                    console.log(loadedContent);
                    // Fetch the scripts
					$scripts = $loadedContent.find('.document-script');
					if ( $scripts.length ){
						$scripts.detach();
					}

					// Fetch the content
                    contentHtml = $loadedContent.html();
					if ( !contentHtml){
						document.location.href = url;
						return false;
					}
                    // Update the content
					$content.stop(true, true);
                    $content.html(contentHtml)
                            .ajaxify()
                            .css('opacity', 100).show();
                    /* you could fade in here if you'd like */
                    // Add the scripts
					$scripts.each(function(){
						var $script = $(this);
                        var scriptText = $script.text();
                        var scriptNode = document.createElement('script');
						scriptNode.appendChild(document.createTextNode(scriptText));
						contentNode.appendChild(scriptNode);
					});

					// Complete the change
                    scrollOptions = {
                        duration: 800,
                        easing:'swing'
                    };
					if ( $body.ScrollTo||false ){ $body.ScrollTo(scrollOptions); }
                    /* http://balupton.com/projects/jquery-scrollto */
					$window.trigger('statechangecomplete');

					// Inform Google Analytics of the change
					if ( typeof window._gaq !== 'undefined' ) {
						window._gaq.push(['_trackPageview', relativeUrl]);
					}

					// Inform ReInvigorate of a state change
					if ( typeof window.reinvigorate !== 'undefined'
                            && typeof window.reinvigorate.ajax_track !== 'undefined' ){
						reinvigorate.ajax_track(url);
						// ^ we use the full url here as that is what reinvigorate supports
					}
                },
                //error: function(jqXHR, textStatus, errorThrown){
                //    document.location.href = url;
				//	return false;
                //}
            });
        });
    });
})(window);
