//Common abbrieviation and optimization
$body = $("body");

//Hook the lookup form up to the lookup() function
$( "#lookup" ).submit(function( event ) {
  event.preventDefault();
  lookup();
});

//Use string from #search to search DBpedia for resources
//List found resources in the table in #options
function lookup() {
	$( "#options" ).empty();
	$( "#show" ).empty();
	var search_for = $( '#search' ).val();
	//TODO: Handle failures
	$.ajax({
    url: "http://lookup.dbpedia.org/api/search/KeywordSearch",
    data: {
      "QueryString" : search_for,
      "MaxHits" : 10
    },
    dataType: 'json',
    success: function( response ) {
      $.each( response.results, _add_result );
    },
    timeout: 4000,
  });
}

//Add an individual DBpedia resource to the table in #options
function _add_result( index, result ) {
	var content_uri = '/get-item/dbpedia-resource/' + encodeURIComponent(result.uri.split("/").pop());
	$( "#options" ).append( "<tr></tr>" );
	$( "#options tr:last" ).on( "click", function() {
  	  show(content_uri);
	});
	$( "#options tr:last" ).append( "<th></th>" );
	$( "#options tr:last th" ).append( result.label );
	$( "#options tr:last" ).append( "<td><small></small></td>" );
	$( "#options tr:last small" ).append( result.description );
}

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
