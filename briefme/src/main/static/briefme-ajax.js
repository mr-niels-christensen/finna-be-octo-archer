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

/**
 * Marks the named item in the current user's channel as done,
 * then calls the provided callback
 * @param name {string} The name to add, e.g. 'Mozart'
 * @param cb {callback} Zero-parameter callback called on success
 */
function ajax_mark_done(name, cb){
	$.ajax({
    url: '/mark-done/' + encodeURIComponent(name),
    method: 'POST',
    dataType: 'json',
	success: cb,
	error: function () {
		console.log('ajax_mark_done failed');
	},
    timeout: 5000,
  });
}
