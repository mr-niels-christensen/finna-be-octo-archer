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
					$body.removeClass("working");
					reset_progress_bar();
	      			$( "#show" ).empty();
	      			if (response.thumbnail) {
	      				$ ( '#show' ).append('<p><img src="' + response.thumbnail + '"/></p>')
	      			};
	      			$.each( response.data, _show_abstract );
				} else {
					setProgress(response.progress);
					setTimeout(function(){show(uri);} , 500 );
				};
			},
    timeout: 1500,
  });	
}

//Add an individual abstract to #show
function _show_abstract( index, abstract ) {
	$( "#show" ).append( "<p>" + abstract + "</p>" )
}
