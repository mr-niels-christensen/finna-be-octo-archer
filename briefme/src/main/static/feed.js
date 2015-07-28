/**
 * Clears the #canvas and displays the current user's feed
 * @param show {string} This function returns without effect,
 * if show is a string != 'feed'.
 */
function _feed_show(show) {
	//Check whether to show feed (this is default, so ok if show is undefined)
	if (show && (show != 'feed')) {
		return;
	};
	//Clear #canvas
	$( "#canvas" ).empty();
	//AJAX  request feed, then display using _show_item()
	$.ajax({//TODO: Handle failures
    url: '/get-feed',
    dataType: 'json',
	success: function( response ) {//TODO: Feed response ought to contain all metadata
		//Success: Create a table to display feed items in
    	$( '#canvas' ).append('<table id="feeditems" class="table table-striped table-hover"></table>');
    	//Provide instructions if the user's feed is empty
    	if (response.future.length == 0) {
    		_report_no_feed_items();
    		return;
    	}
    	//Call _show_item() on each feed item
		$.each( response.future, 
		        function (index, id) {_load(id, _show_item)});//TODO: Display in order, independent of response time
	},
    timeout: 2500,
	});	
}

/**
 * Creates one row in table #feeditems, providing a bit of instruction
 */
function _report_no_feed_items() {
	$( '#feeditems' ).append('<tr></tr>');
	$( '#feeditems tr:last' ).append('<td></td>');
	$( '#feeditems tr:last' ).append('You have no items in your feed. Search to add items.');
}

/**
 * AJAX loads and displays one feed item as a row in table #feeditems
 * @param index {number} The index of the feed item in the list of
 * of feed items, e.g. 0, 1, or 45.
 * @param id {string} The id of the feed item to show, e.g. 'Mozart'
 */
function _load(id, success_cb) {
	//Request metadata from server, then append as a row in table #feeditems
	$.ajax({//TODO: Handle failures
    url: '/get-meta-item/dbpedia-resource/' + encodeURIComponent(id),//TODO provide url from server
    dataType: 'json',
	success: success_cb,
    timeout: 2500,
	});	
}

function _show_item( response ) {//Append row showing item
	$( '#feeditems' ).append('<tr></tr>');
	if (!response.thumbnail) {
		response.thumbnail = "https://upload.wikimedia.org/wikipedia/commons/0/02/Vraagteken.svg";
	};
	$ ( '#feeditems tr:last' ).append('<td></td>')
	$ ( '#feeditems tr:last td:last' ).append('<img class="feeditem" src="' + response.thumbnail + '"></img>')
	$ ( '#feeditems tr:last' ).append('<td></td>')
	$ ( '#feeditems tr:last td:last' ).append('<div class="feeditem"></div>');
	if (!response.title) {
		response.title = response.id;
	}
	$ ( "#feeditems tr:last td:last div" ).append( response.title );
	$ ( '#feeditems tr:last' ).append('<td></td>')
	progress_append(
		response.id, 
		$ ( '#feeditems tr:last td:last' ), 
		100,//TODO responsive design, please 
		40);
	//Update progress bar and poll if necessary
	_poll(response);
}

function _poll(response) {
	if (response.ready) {
		progress_set(response.id, 1.0);
	} else {
		progress_set(response.id, response.progress);
		//TODO: Use comet long polling
		setTimeout(function(){_load(response.id, _poll);} , 1000 );
	};
}

/** Call _feed_show() when appstate changes */
appstate_on_update(_feed_show, ['show']);
