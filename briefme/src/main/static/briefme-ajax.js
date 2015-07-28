//Request abstracts for a DBpedia resource,
//then wait for them to be ready (updating progress bar)
/**
 * Adds the given id to the current user's feed,
 * then directs to the feed page.
 * @param id {string} The id to add, e.g. 'Mozart'
 */
function _add_to_feed(id){
	//TODO: Handle failures
	$.ajax({
    url: '/add-to-feed/' + encodeURIComponent(id),
    method: 'POST',
    dataType: 'json',
	success: function( response ) {
				appstate_update({show: 'feed'});
			},
    timeout: 2500,
  });
}
