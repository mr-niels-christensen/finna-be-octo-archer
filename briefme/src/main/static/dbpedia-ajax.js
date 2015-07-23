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
	$( "#options tr:last" ).append( "<td><p><b></b></p></td>" );
	$( "#options tr:last b" ).append( result.label );
	$( "#options tr:last td" ).append( "<p><small></small></p>" );
	$( "#options tr:last small" ).append( _sentence(result.description) );
}

//Return the first sentence of the textual descrition,
//without stuff in parentheses
function _sentence(text) {
  if (!text) { //Avoid processing a null text
    return "Sorry, no description.";
  }
  //Select everything before first "." and add a "." to form a sentence.
  var first = text.split(".")[0] + ".";
  //Split "foo (bar) qwerty" into "foo ", "(", "bar", ")", " qwerty"
  var fsplit = first.split(/(\(|\))/g);
  var elems = [];
  for (var i = 0; i < fsplit.length; i += 4) {  // take every 4th element, e.g. "foo " and " qwerty"
    elems.push(fsplit[i]);
  }
  //Join up the strings and replace any dangling commas that used to have () in front of them
  var result = elems.join('').replace(/ ,/g, ', ');
  //Limimt to max 150 chars
  if (result.length <= 150) {
    return result;
  } else {
    return result.substr(0,147) + "...";
  }
}
