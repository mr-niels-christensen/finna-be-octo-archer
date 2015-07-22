$body = $("body");

$( "#lookup" ).submit(function( event ) {
  event.preventDefault();
  lookup();
});

function lookup() {
	$( "#options" ).empty();
	$( "#show" ).empty();
	var search_for = $( '#search' ).val();
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
function _add_result( index, result ) {
	var content_uri = '/get-item/dbpedia-resource/'+encodeURIComponent(result.uri.split("/").pop());
	$( "#options" ).append( "<tr></tr>" );
	$( "#options tr:last" ).on( "click", function() {
  	  show(content_uri);
	});
	$( "#options tr:last" ).append( "<th></th>" );
	$( "#options tr:last th" ).append( result.label );
	$( "#options tr:last" ).append( "<td><small></small></td>" );
	$( "#options tr:last small" ).append( result.description );
}
function show(uri){
	$body.addClass("working");
	$.ajax({
    url: uri,
    dataType: 'json',
	success: function( response ) {
				if (response.ready) {
					$body.removeClass("working");
	      			$( "#show" ).empty();
	      			$.each( response.data, _show_abstract );
				} else {
					setProgress(response.progress);
					setTimeout(function(){show(uri);} , 500 );
				};
			},
    timeout: 1500,
  });	
}
function _show_abstract( index, abstract ) {
	$( "#show" ).append( "<p>" + abstract + "</p>" )
}
