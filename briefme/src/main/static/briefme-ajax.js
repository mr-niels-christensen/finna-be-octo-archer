//Request abstracts for a DBpedia resource,
//then wait for them to be ready (updating progress bar)
function show(id){
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
