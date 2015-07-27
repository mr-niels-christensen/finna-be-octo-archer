//Common abbrieviation and optimization
$body = $("body");

//Request abstracts for a DBpedia resource,
//then wait for them to be ready (updating progress bar),
//then display them on #show
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
					var _url = '/get-item/dbpedia-resource/' + encodeURIComponent(response.id);
	      			appstate_update({show:'item',url:_url});
				} else {
					progress_set(id, response.progress);
					//TODO: Use comet long polling
					setTimeout(function(){show(id, true);} , 1000 );
				};
			},
    timeout: 2500,
  });	
}

function _show_item(show, url) {
	if (show != 'item') {
		return;
	};
	$( "#canvas" ).empty();
	//TODO: Handle failures
	$.ajax({
    url: url,
    dataType: 'json',
	success: function( response ) {
		if (response.thumbnail) {
			$ ( '#canvas' ).append('<p><img src="' + response.thumbnail + '"/></p>')
		};
		$.each( response.data, _show_abstract );
				
	},
    timeout: 2500,
	});	
}

//Add an individual abstract to #show
function _show_abstract( index, abstract ) {
	$( "#canvas" ).append( "<p>" + abstract + "</p>" )
}

appstate_on_update(_show_item, ['show', 'url']);
