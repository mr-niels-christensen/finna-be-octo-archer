//List found resources in the table in #options
function lookup(show, search_for) {
  if (show != 'hits') {
    return;
  }
	$( "#canvas" ).empty();
	//TODO: Handle failures
	$.ajax({
    url: "http://lookup.dbpedia.org/api/search/KeywordSearch",
    data: {
      "QueryString" : search_for,
      "MaxHits" : 10
    },
    dataType: 'json',
    success: function( response ) {
      $( '#canvas' ).append('<table id="options" class="table table-striped table-hover"></table>');
      $.each( response.results, _add_result );
    },
    timeout: 4000,
  });
}

//Add an individual DBpedia resource to the table in #options
function _add_result( index, result ) {
  var id = result.uri.split("/").pop();
	$( "#options" ).append( "<tr></tr>" );
	$( "#options tr:last" ).append( "<td><p><b></b></p></td>" );
	$( "#options tr:last b" ).append( result.label );
	$( "#options tr:last td" ).append( "<p><small></small></p>" );
	$( "#options tr:last small" ).append( _sentence(result.description) );
  $( "#options tr:last" ).append( '<td><button type="button" class="btn btn-success">Add</button></td>' );
  $( "#options tr:last button" ).on( "click", function() {
      $(this).prop('disabled', true);
      show(id, false);
  });
  $( "#options tr:last" ).append( '<td></td>' );
  var button = $( "#options tr:last button" );
  progress_append(id, $( "#options tr:last td:last" ), button.width()* 2, button.height() * 1.5);
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
  //Limit to max 150 chars
  if (result.length <= 150) {
    return result;
  } else {
    return result.substr(0,147) + "...";
  }
}

//Hook the lookup form up to the lookup() function
$( "#lookup" ).submit(function( event ) {
  event.preventDefault();
  appstate_update({show:'hits', query : $( '#query' ).val()});
});

appstate_on_update(lookup, ['show', 'query']);


