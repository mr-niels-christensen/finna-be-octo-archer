/**
 * Clears the #canvas and displays the current user's channel
 * @param show {string} This function returns without effect,
 * if show is a string != 'feed'.
 */
function _channel_show(show) {
	//Check whether to show channel (this is default, so ok if show is undefined)
	if (show && (show != 'channel')) {
		return;
	};
	//Clear #canvas
	$( "#canvas" ).empty();
	//Create a table to display channel items in
	$( '#canvas' ).append('<div class="table-responsive"></div>');
	$( '#canvas .table-responsive' ).append('<table id="channelitems" class="table table-striped table-hover"></table>');
	_channel_update();
}

function _channel_update() {
	//AJAX  request feed, then display using _show_item()
	$.ajax({//TODO: Handle failures
    url: '/get-channel',
    dataType: 'json',
	success: function( response ) {
    	//Provide instructions if the user's channel is empty
    	if (response.length == 0) {
    		_report_no_channel_items();
    		return;
    	}
    	//Append the row for each channel item
    	var missing = response.length - ($( '#channelitems tr' ).length);
    	for (i = 0; i < missing; i++) {
    		_append_item_row( $('#channelitems'), response[i].name );
    	};
    	//Call _show_item() on each channel item
		var poll = $.map( response, function (item, index) {
					var row_selector = $('#channelitems tr:nth-child(' + (index+1) + ')');
					return _show_item( row_selector, item );
		        });
		if (poll.some(function (x) {return x;})) {
			//TODO: Use comet long polling
			setTimeout(_channel_update , 1000 );
		}
	},
    timeout: 2500,
	});	
}

/**
 * Creates one row in table #channelitems, providing a bit of instruction
 */
function _report_no_channel_items() {
	$( '#channelitems' ).append('<tr></tr>');
	$( '#channelitems tr:last' ).append('<td></td>');
	$( '#channelitems tr:last' ).append('You have no items in your channel. Search to add items.');
}

function _append_item_row(table_selector, name) {
	table_selector.append('<tr></tr>');
	var row_selector = table_selector.find( 'tr:last' );	
	//Add Play column
	row_selector.append('<td></td>')
	row_selector.find( 'td:last' ).append('<button type="button" class="btn btn-success">Play</button>');
	row_selector.append('<td></td>')
	row_selector.find( 'td:last' ).append('<img class="feeditem"></img>')
	//Add title column
	row_selector.append('<td></td>')
	row_selector.find( 'td:last' ).append('<div class="feeditem itemtitle"></div>');
	//Add status/progress bar column
	row_selector.append('<td></td>')
	progress_append(
		name, 
		row_selector.find( 'td:last' ), 
		100,//TODO responsive design, please 
		40);
}

/**
 * Appends one row to table #channelitems, displaying the feed item.
 * Starts a polling loop (updating progress bar) if the feed item is not ready.
 * @param response {object} The channel item to display
 */
function _show_item( row_selector, item ) {
	if (item.ready) {
		row_selector.find( 'button' ).on( "click", function() {
	      appstate_update({show: 'player', item:item.name});
    	});
		row_selector.find( 'button' ).prop('disabled', false);
	} else {
		row_selector.find( 'button' ).prop('disabled', true);
	}
	//Add thumbnail
	if (!item.thumbnail_url) {
		item.thumbnail_url = "https://upload.wikimedia.org/wikipedia/commons/0/02/Vraagteken.svg";
	};
	if (item.thumbnail_url != row_selector.find( 'img' ).attr( 'src' )){
		row_selector.find( 'img' ).attr( 'src', item.thumbnail_url );
	}
	if (!item.title) {
		item.title = item.name;
	}
	row_selector.find ( ".itemtitle" ).html( item.title || item.name );
	//Update progress bar and poll if necessary
	if (item.ready) {
		progress_set(item.name, 1.0);
	} else {
		progress_set(item.name, item.progress);
	};
	return !item.ready;
}

/** Call _channel_show() when appstate changes */
appstate_on_update(_channel_show, ['show']);
