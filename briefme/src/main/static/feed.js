
function _feed_show(show) {
	if (show != 'feed') {
		return;
	};
	$( "#canvas" ).empty();
	//TODO: Handle failures
	$.ajax({
    url: '/get-feed',
    dataType: 'json',
	success: function( response ) {
    	$( '#canvas' ).append('<table id="feeditems" class="table table-striped table-hover"></table>');
		$.each( response.future, _show_item );		
	},
    timeout: 2500,
	});	
}

function _show_item(index, id) {
	var _url = '/get-item/dbpedia-resource/' + encodeURIComponent(id);
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
