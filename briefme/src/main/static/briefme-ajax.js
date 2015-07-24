//Common abbrieviation and optimization
$body = $("body");

//Request abstracts for a DBpedia resource,
//then wait for them to be ready (updating progress bar),
//then display them on #show
function show(uri){
	$body.addClass("working");
	//TODO: Handle failures, consider setInterval() and clearInterval() or similar from jquery
	$.ajax({
    url: uri,
    dataType: 'json',
	success: function( response ) {
				if (response.ready) {
					//TODO: Use HTML local state or load from separate URL, do not store all data in URL
	      			appstate_update({show:'item',item:response});
				} else {
					setProgress(response.progress);
					//TODO: Use comet long polling
					setTimeout(function(){show(uri);} , 500 );
				};
			},
    timeout: 1500,
  });	
}

function _show_item(show, item) {
	if (show != 'item') {
		return;
	};
	$body.removeClass("working");
	reset_progress_bar();
	$( "#canvas" ).empty();
	if (item.thumbnail) {
		$ ( '#canvas' ).append('<p><img src="' + response.thumbnail + '"/></p>')
	};
	$.each( item.data, _show_abstract );
}

//Add an individual abstract to #show
function _show_abstract( index, abstract ) {
	$( "#canvas" ).append( "<p>" + abstract + "</p>" )
}

appstate_on_update(_show_item, ['show', 'item']);
