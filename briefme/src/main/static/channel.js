/**
 * Clears the #canvas and displays the current user's channel
 * @param show {string} This function returns without effect,
 * if show is a string != 'channel'.
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

/**
 * AJAX request channel, then displays using _show_item()
 */
function _channel_update() {
	//TODO: An update may prevent pausing a running narrative
	$.ajax({
    url: '/get-channel',
    dataType: 'json',
	success: function( response ) {
    	//Provide instructions if the user's channel is empty
    	if (response.length == 0) {
    		_report_no_channel_items();
    		return;
    	}
    	//Append the row for each channel item, TODO assumes no reordering or removal
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
	error: function () {
		_report_server_problem();
		setTimeout(_channel_update , 5000 );
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

/**
 * Creates one row in table #channelitems, providing a bit of information
 */
function _report_server_problem() {
	$( '#channelitems' ).append('<tr></tr>');
	$( '#channelitems tr:last' ).append('<td></td>');
	$( '#channelitems tr:last' ).append('Waiting for server...');
}


/**
 * Adds one row to the given table, representing a channel item
 * with the given name.
 * @param table_selector {jquery selector} The table to append a row to
 * @param name {string} name of the item, e.g. 'Mozart'
 */
function _append_item_row(table_selector, name) {
	table_selector.append('<tr></tr>');
	var row_selector = table_selector.find( 'tr:last' );	
	//Add Play/Done column
	row_selector.append('<td></td>')
	row_selector.find( 'td:last' ).append('<div></div>');
	row_selector.find( 'td:last div:last' ).append('<button type="button" class="btn btn-success btn-play btn-block">Play</button>');
	row_selector.find( 'td:last' ).append('<div></div>');
	row_selector.find( 'td:last div:last' ).append('<button type="button" class="btn btn-default btn-done btn-block">Done</button>');
	row_selector.find( '.btn-done' ).on( "click", function (event) {
		row_selector.empty();
		ajax_mark_done(name, _channel_update);
	});
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
 * Updates a single item row.
 * @param row_selector {jquery selector} The row to update
 * @param item {object} The channel item to display in the row
 */
function _show_item( row_selector, item ) {
	if (item.ready) {
		attach_item(item.name, row_selector.find( '.btn-play' ), item.checkpoint);
		row_selector.find( '.btn-play' ).prop('disabled', false);
	} else {
		row_selector.find( '.btn-play' ).prop('disabled', true);
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
		if (item.failed) {
			progress_issue(item.name);
		} else {
			progress_set(item.name, item.progress);
		}
	};
	return !item.ready;
}

/** Call _channel_show() when appstate changes */
appstate_on_update(_channel_show, ['show']);
