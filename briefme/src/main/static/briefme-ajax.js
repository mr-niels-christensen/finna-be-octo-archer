//Common abbrieviation and optimization
$body = $("body");

//Request abstracts for a DBpedia resource,
//then wait for them to be ready (updating progress bar),
//then display them on #show
function show(uri){
	$body.addClass("working");
	//TODO: Handle failures
	$.ajax({
    url: uri,
    dataType: 'json',
	success: function( response ) {
				if (response.ready) {
					//TODO: Use HTML local state or load from separate URL, do not store all data in URL
					var _url = '/get-item/dbpedia-resource/' + encodeURIComponent(response.id);
	      			appstate_update({show:'item',url:_url});
				} else {
					setProgress(response.progress);
					//TODO: Use comet long polling
					setTimeout(function(){show(uri);} , 500 );
				};
			},
    timeout: 1500,
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
    timeout: 1500,
	});	
	$body.removeClass("working");
	reset_progress_bar();
}

//Add an individual abstract to #show
function _show_abstract( index, abstract ) {
	$( "#canvas" ).append( "<p>" + abstract + "</p>" )
}

appstate_on_update(_show_item, ['show', 'url']);
