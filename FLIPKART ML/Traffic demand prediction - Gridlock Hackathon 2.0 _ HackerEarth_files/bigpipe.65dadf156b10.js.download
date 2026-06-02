var debug = false;

var LOAD_SECTION_MAP = {}

function fetch_pagelets(id) {
    var json_str = '{}';
    if (typeof(id) === 'undefined')
        json_str = $('#bigpipe-json').html();
    else
        json_str = $('#bigpipe-json-'+id).html();

    if (json_str == null)
        return;

    json_str = json_str.trim();
    if (json_str == '')
        return;

    try {
        if (debug)
            console.log(json_str);
        var obj = JSON.parse(json_str);
    } catch(err) {
        if (typeof Sentry !== 'undefined') {
            Sentry.withScope(function(scope) {
                scope.setExtra('origin', 'bigpipe');
                scope.setExtra('data', json_str);
                Sentry.captureException(e);
            });
        }
        return;
    }

    for(var k in obj) {
        if ({}.hasOwnProperty.call(obj, k)) {
            if (debug)
                console.log(k, " = ", obj[k]);

            var id = k;
            var url = obj[k];

            // fetch html from this url and display in
            // the corresponding div
            $.ajax({
                url: url,
                id: id,
                success: function(html) {
                    var id = this.id;
                    $('#'+id).html(html);
                    latexifyAjaxDiv($('#'+id));

                    // now the elements have been inserted
                    // execute appropriate handlers
                    try {
                        domElementLive();
                    } catch(err) {
                        if (debug)
                            console.log(err.message);
                    }
                }
            });
        }
    }
}

$(document).ready(function() {
    // Fetch pagelets if there are existing bigpipe json
    fetch_pagelets();

    // load pagelet on click

    $('.load-pagelet').live('click', function(e) {
        var $this = $(this);
        var target = $('#' + $this.attr('target'));
        var url = $this.attr('ajax');
        var text = $this.html();
        var click_text = $this.attr('click-text');
        $this.html(click_text);

        var show_loader = $this.attr('show-loader');
        if (!show_loader || show_loader !== 'false') {
            target.html(LOADER_HTML);
        }

        // make the ajax call
        var xhr = $.ajax({
            url: url,
            type: 'POST',
            text: text,
            this_this: $this,
            target: target,
            success: function(response) {
                var text = this.text;
                this.this_this.html(text);
                this.target.html(response);
            },
            error: function(response) {
                var text = this.text;
                this.this_this.html(text);
                
                if(window.global.checkAndShowServerError) {
                    window.global.checkAndShowServerError(response.status);
                }
            },
        });
        e.preventDefault();
    });

    $('.section-form').live('submit', function(event) {
        var $this = $(this);

        var targets = parseInt($(this).attr('targets'));
        var url = $this.attr('ajax');
        var data = $this.serialize();
        var text = $this.html();

        // find the submit button for this form and move
        // it to a transient state
        var input = $this.find('input[type="submit"]:not(.cancel),button');
        var input_value = input.val();

        // if the input button has clicked class then
        // return false
        if (input.hasClass('clicked')) {
            event.preventDefault();
            return;
        }

        if (input.val() == 'Save' || input.val() == 'save') {
            input.val('Saving..');
        }

        if (input.is('[clicked]')) {
            var clicked_value = input.attr('clicked');
            input.val(clicked_value);
        }

        // add clicked class
        input.addClass('clicked');

        make_ajax = true;

        // shift between the split panel and the
        // full body panel
        for (var i = 0; i < targets; i++) {
            var index = i+1;
            var target_attr = 'target' + index;
            var target_id = $this.attr(target_attr);
            var target = $('#'+target_id);

            target.html(LOADER_HTML);

            // if we are making an ajax call then
            // abort all pending ajax requests for this
            // div id
            if (make_ajax) {
                if (target_id in LOAD_SECTION_MAP) {
                    var old_xhr = LOAD_SECTION_MAP[target_id];
                    old_xhr.abort();
                }
            }
        }

        // if the ajax call is to be made then
        // make the ajax call
        if (make_ajax) {
            var xhr = $.ajax({
                url: url,
                type: 'POST',
                data: data,
                dataType: 'json',
                text: text,
                this_this: $this,
                success: function(response) {
                    var text = this.text;
                    this.this_this.html(text);

                    if (response['status'] == AJAX_OK) {
                        if (response['url']) {
                            window.location.href = response['url'];
                        } else {
                            for (var i = 0; i < targets; i++) {
                                var index = i+1;
                                var target_attr = 'target' + index;
                                var target_id = $this.attr(target_attr);
                                var target = $('#'+target_id);
                                if (response['pagelet-'+index]) {
                                    target.html(response['pagelet-'+index]);
                                    // adjust the height of textarea
                                    $('textarea').each(function() {
                                        if (!$(this).hasClass('no-height-change')) {
                                            if($(this).length > 0) {
                                                var $this = $(this);
                                                var t_height =  $this.get(0).scrollHeight;
                                                if (t_height > MAX_HEIGHT) {
                                                    t_height = MAX_HEIGHT;
                                                }
                                                $this.height(t_height);
                                            }
                                        }
                                    });
                                } else {
                                    target.html('');
                                }
                            }
                            // execute the bindings
                            domElementLive();
                        }
                    }
                },
                statusCode: {
                    404: function() {
                        window.location.reload();
                        alert("There was some error in accessing the resource, re-loading the page.");
                    },
                    403: function() {
                        alert("There was some error in accessing the resource, re-loading the page.");
                        window.location.reload();
                    }
                }
            });

            // update the ajax request to the current
            for (var i = 0; i < targets; i++) {
                var index = i+1;
                var target_attr = 'target' + index;
                var target_id = $this.attr(target_attr);
                LOAD_SECTION_MAP[target_id] = xhr;
            }
        } // end if make_ajax

        return false;
    });
    // end form sections

    // load sections on click
    $('.load-section').live('click', function() {

        var $this = $(this);

        // find out how many targets are there
        var targets = parseInt($(this).attr('targets'));
        var url = $(this).attr('ajax');
        var cache = $this.attr('cache');
        var animation = $this.attr('animation');
        //url to replace ajax attribute value
        var ajax_url = $(this).attr('url');
        var execute = $this.attr('execute');

        // Can be GET or POST or undefined
        var request_method = $this.attr('ajax-request-method');

        if (typeof request_method === 'undefined') {
            request_method = 'POST';
        }

        /*
        If load-section element has an attribute 'url' then the ajax attribute
        value will be replaced by url value.
        use case: refer candidates reports
        */
        if (typeof ajax_url !== 'undefined' && ajax_url !== false) {
            $this.attr('ajax', ajax_url);
        }

        if (typeof cache !== 'undefined' && cache !== false) {
            cache = true;
        }

        // why this is here I don't know
        /*
        var event_url = $('#candidates-report').attr('url');
        $('#candidates-report').attr('ajax', event_url);
        */

        var text = $this.html();
        var click_text = $this.attr('click-text');
        $this.html(click_text);

        // variable that will determine if the ajax call needs to be made
        // or we just have to show the div, depends on the value of cache
        var make_ajax;
        if (cache) {
            make_ajax = false;
        } else {
            make_ajax = true;
        }

        // shift between the split panel and the
        // full body panel
        for (var i = 0; i < targets; i++) {
            var index = i+1;
            var target_attr = 'target' + index;
            var target_id = $this.attr(target_attr);
            var target = $('#'+target_id);
            if (target.hasClass('split-panel')) {
                $('.split-panel').removeClass('hidden');
                $('.full-panel').addClass('hidden');
            }
            if (target.hasClass('full-panel')) {
                $('.full-panel').removeClass('hidden');
                $('.split-panel').addClass('hidden');
            }

            // if the content is to be cached then hide all the siblings
            // and show this one
            if (cache) {
                var sibling_attr = 'sibling' + index;
                var sibling_class = $this.attr(sibling_attr);
                $('.'+sibling_class).hide();
                target.show();

                // determine if the ajax call needs to be made
                // or we can just unhide the div
                if (!$.trim(target.html())) {
                    target.html(LOADER_HTML);
                    make_ajax = make_ajax || true;
                }
            } else {
                target.html(LOADER_HTML);
            }

            // if we are making an ajax call then
            // abort all pending ajax requests for this
            // div id
            if (make_ajax) {
                if (target_id in LOAD_SECTION_MAP) {
                    var old_xhr = LOAD_SECTION_MAP[target_id];
                    old_xhr.abort();
                }
            }
        }

        // if the ajax call is to be made then
        // make the ajax call
        if (make_ajax) {
            var xhr = $.ajax({
                url: url,
                type: request_method,
                dataType: 'json',
                text: text,
                this_this: $this,
                success: function(response) {
                    var text = this.text;
                    this.this_this.html(text);

                    if (response['status'] == AJAX_OK) {
                        for (var i = 0; i < targets; i++) {
                            var index = i+1;
                            var target_attr = 'target' + index;
                            var target_id = $this.attr(target_attr);
                            var target = $('#'+target_id);
                            if (response['pagelet-'+index]) {
                                if (animation == 'slidedown') {
                                    target.hide().html(response['pagelet-'+index]).slideDown('slow');
                                } else {
                                    target.html(response['pagelet-'+index]);
                                }

                                latexifyAjaxDiv(target);
                                // adjust the height of textarea
                                $('textarea').each(function() {
                                    if (!$(this).hasClass('no-height-change')) {
                                        if($(this).length > 0) {
                                            var $this = $(this);
                                            var t_height =  $this.get(0).scrollHeight;
                                            if (t_height > MAX_HEIGHT) {
                                                t_height = MAX_HEIGHT;
                                            }
                                            $this.height(t_height);
                                        }
                                    }
                                });

                                // execute any function that needs to be executed
                                if (execute) {
                                    execute_list = execute.trim().split(" ");
                                    for(var i=0; i < execute_list.length; i++) {
                                        var command = execute_list[i];
                                        window[command]();
                                    }
                                }

                            } else {
                                target.html('');
                            }
                        }

                        // execute the bindings
                        domElementLive();
                    }
                    else {
                        if (targets) {
                            // Clear HTML for all targets (remove loaders)
                            for (var i = 1; i <= targets; i++) {
                                $('#' + $this.attr('target' + i)).html('');
                            }
                        }

                        if (response['messages']) {
                            messages = response['messages'];
                            for (var i = 0; i < messages.length; i++) {
                                addAlert(messages[i]);
                            };
                        }
                    }
                },
                statusCode: {
                    404: function() {
                        window.location.reload();
                        alert("There was some error in accessing the resource, re-loading the page.");
                    },
                    403: function() {
                        alert("There was some error in accessing the resource, re-loading the page.");
                        window.location.reload();
                    }
                }
            });

            // update the ajax request to the current
            for (var i = 0; i < targets; i++) {
                var index = i+1;
                var target_attr = 'target' + index;
                var target_id = $this.attr(target_attr);
                LOAD_SECTION_MAP[target_id] = xhr;
            }
        } // end if make_ajax

        return false;
    });
    // end load sections

    // add selected class on click
    $('.load-section').live('click', function() {
        var $this = $(this);
        var classes = $this.attr('class') + ' selected';
        $('.load-section').each(function() {
            var this_class = $(this).attr('class');
            if (this_class == classes) {
                $(this).removeClass('selected');
            }
        });
        $this.addClass('selected');
    });

    // reset a pagelet to empty html
    $('.reset-section').live('click', function() {
        var targets = parseInt($(this).attr('targets'));
        for (var i = 0; i < targets; i++) {
            var index = i+1;
            var target_attr = 'target' + index;
            var target_id = $(this).attr(target_attr);
            var target = $('#'+target_id);
            target.html('');
        }
        if (window.closeFlyout) {
            window.closeFlyout();
        }
        return false;
    });
    // end reset-section

    // Load a pagelet only when trigger element is in view
    $('.pagelet-inview').live('inview', function() {
        var $this = $(this);
        var target = $('#'+$this.attr('target'));
        var execute = $this.attr('execute');

        // Check whether target was already previously loaded
        var loaded = target.attr('loaded');
        if (typeof loaded !== 'undefined' && (loaded == "1" || loaded == "2")) {
            // 1: already loading, 2: loaded
            return;
        }

        var url = $this.attr('ajax');
        var loader = $this.attr('loader');
        if (loader !=='undefined')
        {
            if(loader!=="false")
                target.html(LOADER_HTML);
        }
        else
            target.html(LOADER_HTML);

        // set loading status
        target.attr('loaded', '1');


        var xhr = $.ajax({
            url: url,
            this_this: $this,
            target: target,
            success: function(response) {
                this.target.html(response);
                latexifyAjaxDiv(this);


                // set loaded status
                this.target.attr('loaded', '2');

                // now the elements have been inserted
                // execute appropriate handlers
                try {
                    domElementLive();
                } catch(err) {
                    if (debug)
                        console.log(err.message);
                }
                // execute any function that needs to be executed
                if (execute) {
                    var execute_args = response.execute_args;
                    execute_list = execute.split(" ");
                    for(var i=0; i < execute_list.length; i++) {
                        var command = execute_list[i];
                        if(execute_args) {
                            window[command](execute_args);
                        } else {
                            window[command]();
                        }
                    }
                }
            },
            error: function(response) {
                // clear loading status
                this.target.attr('loaded', '0');
                this.target.html('There was some error in loading this section! Please try again after sometime. Contact support@hackerearth.com if problem persists.');
            },
        });
    });

    /*
     * Loads pagelet on hover over specific dom element.
     */

    $('.pagelet-hover').live('hover', function() {
        var $this = $(this);
        var target = $('#'+$this.attr('target'));

        // Check whether target was already previously loaded
        var loaded = target.attr('loaded');
        if (typeof loaded !== 'undefined' && (loaded == "1" || loaded == "2")) {
            // 1: already loading, 2: loaded
            return;
        }

        var url = $this.attr('ajax');
        target.html(LOADER_HTML);

        // set loading status
        target.attr('loaded', '1');

        var xhr = $.ajax({
            url: url,
            this_this: $this,
            target: target,
            success: function(response) {
                this.target.html(response);
                // set loaded status
                this.target.attr('loaded', '2');

                // now the elements have been inserted
                // execute appropriate handlers
                try {
                    domElementLive();
                } catch(err) {
                    if (debug)
                        console.log(err.message);
                }
            },
            error: function(response) {
                // clear loading status
                this.target.attr('loaded', '0');
                this.target.html('There was some error in fetching data for you!');
            },
        });
    });

    show_view_option = function(){
        if (!(getParameterByName('scroll-id') || getParameterByName('scroll-trigger'))) {
            $('.view-comments .link-14').html("<i class='fa fa-comments result-icon'></i> View all comments");
            $('.view-comments-content, .sort-filter, .comment-sort-filter a.load-pagelet').css('display','none');
        }
    }
    $('.problem-page').on('click', '.view-comments, input[type=submit][name=submit-comment]', function(){
        $('.view-comments-content, .sort-filter, .comment-sort-filter a.load-pagelet').css('display','block');
        $('.view-comments').css('display','none');
    });

    $('.load-all-comments').on('click', function() {
        var $this = $(this);
        // Hide the button/link used to start loading comments
        $this.hide();
        var target = $('#'+$this.attr('target'));
        var execute = $this.attr('execute');

        target.css('display', 'block');

        // Check whether target was already previously loaded
        var loaded = target.attr('loaded');
        if (typeof loaded !== 'undefined' && (loaded === "1" || loaded === "2")) {
            // 1: already loading, 2: loaded
            return;
        }

        var url = $this.attr('ajax');
        var loader = $this.attr('loader');
        if (loader !== 'undefined')
        {
            if (loader !== "false")
                target.html(LOADER_HTML);
        }
        else
            target.html(LOADER_HTML);

        // set loading status
        target.attr('loaded', '1');


        var xhr = $.ajax({
            url: url,
            this_this: $this,
            target: target,
            success: function(response) {
                this.target.html(response);
                latexifyAjaxDiv(this);


                // set loaded status
                this.target.attr('loaded', '2');

                // now the elements have been inserted
                // execute appropriate handlers
                try {
                    domElementLive();
                } catch(err) {
                    if (debug)
                        console.log(err.message);
                }
                // execute any function that needs to be executed
                if (execute) {
                    var execute_args = response.execute_args;
                    execute_list = execute.split(" ");
                    for(var i=0; i < execute_list.length; i++) {
                        var command = execute_list[i];
                        if(execute_args) {
                            window[command](execute_args);
                        } else {
                            window[command]();
                        }
                    }
                }
            },
            error: function(response) {
                // clear loading status
                this.target.attr('loaded', '0');
                this.target.html('There was some error in loading this section! Please try again after sometime. Contact support@hackerearth.com if problem persists.');
                // Show the button/link used to load comments. This was hidden at the beginning of the function
                this.this_this.show();
            },
        });
    });
});
