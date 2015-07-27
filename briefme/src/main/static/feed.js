
function _feed_show(show) {
	if (show && (show != 'feed')) {
		return;
	};
	$( "#canvas" ).empty();
	//TODO: Handle failures
	$.ajax({
    url: '/get-feed',
    dataType: 'json',
	success: function( response ) {//TODO: Feed response ought to contain all metadata
    	$( '#canvas' ).append('<table id="feeditems" class="table table-striped table-hover"></table>');
    	if (response.future.length == 0) {
    		_report_no_feed_items();
    		return;
    	}
		$.each( response.future, _show_item );//TODO: Display in order, independent of response time
	},
    timeout: 2500,
	});	
}

function _report_no_feed_items() {
	$( '#feeditems' ).append('<tr></tr>');
	$( '#feeditems tr:last' ).append('<td></td>');
	$( '#feeditems tr:last' ).append('You have no items in your feed. Search to add items.');
}

function _show_item(index, id) {
	var _url = '/get-meta-item/dbpedia-resource/' + encodeURIComponent(id);
	//TODO: Handle failures
	$.ajax({
    url: _url,
    dataType: 'json',
	success: function( response ) {
		$( '#feeditems' ).append('<tr></tr>');
		if (!response.thumbnail) {
			response.thumbnail = "https://upload.wikimedia.org/wikipedia/commons/0/02/Vraagteken.svg";
		};
		$ ( '#feeditems tr:last' ).append('<td></td>')
		$ ( '#feeditems tr:last td:last' ).append('<img class="feeditem" src="' + response.thumbnail + '"></img>')
		$ ( '#feeditems tr:last' ).append('<td></td>')
		$ ( '#feeditems tr:last td:last' ).append('<div class="feeditem"></div>');
		if (!response.title) {
			response.title = id;
		}
		$ ( "#feeditems tr:last td:last div" ).append( response.title );
	},
    timeout: 2500,
	});	
}

appstate_on_update(_feed_show, ['show']);
