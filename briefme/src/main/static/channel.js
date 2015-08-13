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
		//Clear #canvas
		$( "#canvas" ).empty();
		//Create a table to display channel items in
		$( '#canvas' ).append('<div class="table-responsive"></div>');
		$( '#canvas .table-responsive' ).append('<table id="channelitems" class="table table-striped table-hover"><tbody></tbody></table>');
    	//Provide instructions if the user's channel is empty
    	if (response.length == 0) {
    		_report_no_channel_items();
    		return;
    	}
    	//Call _show_item() on each channel item
		var content = $.map( response, function (item, index) {
				   	return _show_item( item );
		        });
		$('#channelitems tbody')
			.append(content.join(''))
			.on('click', '.btn-done', function (event) {
				event.preventDefault();
				ajax_mark_done(event.target.name, _channel_update);
			})
			.on('click', '.btn-play', player_on_play_pause)
			;
		if (response.some(function (x) {return !(x.ready);})) {
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
 * Creates a single item row.
 * @param item {object} The channel item to display in the row
 * @return HTML for a table row
 */
function _show_item( item ) {
	var template = $("#itemrowtemplate").html();//TODO: Cache
	var id = item.name.replace(/\W/g, "_");
	var pct = Math.floor(item.progress*100);
	var klass = (item.ready) ? 'complete' :
					(item.failed) ? 'issue' : 'working';
	return template.format(
		id, 
		klass, 
		(item.ready) ? '' : 'disabled="disabled"',
		item.thumbnail_url || "https://upload.wikimedia.org/wikipedia/commons/0/02/Vraagteken.svg",
		item.title || item.name,
		pct, 
		100 - pct,
		item.name,
		item.checkpoint);
		//attach_item(item.name, row_selector.find( '.btn-play' ), item.checkpoint);
}

/** Call _channel_show() when appstate changes */
appstate_on_update(_channel_show, ['show']);
