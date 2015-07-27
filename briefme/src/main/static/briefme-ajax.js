//Request abstracts for a DBpedia resource,
//then wait for them to be ready (updating progress bar)
function show(id, is_recursive_call){
	if (!is_recursive_call){
		progress_set(id, 0);	
	} 
	//TODO: Handle failures
	$.ajax({
    url: ((is_recursive_call) ? '/get-meta-item/dbpedia-resource/' :'/add-to-feed/') + encodeURIComponent(id),
    method: (is_recursive_call) ? 'GET' : 'POST',
    dataType: 'json',
	success: function( response ) {
				if (response.ready) {
					progress_set(id, 1.0);
				} else {
					progress_set(id, response.progress);
					//TODO: Use comet long polling
					setTimeout(function(){show(id, true);} , 1000 );
				};
			},
    timeout: 2500,
  });	
}
