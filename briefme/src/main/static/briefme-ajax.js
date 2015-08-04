/**
 * Adds the given id to the current user's feed,
 * then directs to the feed page.
 * @param id {string} The id to add, e.g. 'Mozart'
 */
function _add_to_feed(id){
	$.ajax({
    url: '/add-to-feed/' + encodeURIComponent(id),
    method: 'POST',
    dataType: 'json',
	success: function( response ) {
				appstate_update({show: 'channel'});
			},
	error: function () {
		console.log('add-to-feed failed');
	},
    timeout: 2500,
  });
}
