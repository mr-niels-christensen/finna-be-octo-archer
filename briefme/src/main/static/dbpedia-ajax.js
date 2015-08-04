/**
 * If show=='hits', search DBpedia for search_for and
 * display the results on #canvas
 * @param show {string} If show!='hits', return without action
 * @param search_for {string} The search query to send to DBpedia
 */
function lookup(show, search_for) {
  //Check show, return if not == 'hits'
  if (show != 'hits') {
    return;
  }
  //Clear #canvas
	$( "#canvas" ).empty();
	//AJAX search DBpedia
	$.ajax({
    url: "http://lookup.dbpedia.org/api/search/KeywordSearch",
    data: {
      "QueryString" : search_for,
      "MaxHits" : 10
    },
    dataType: 'json',
    success: function( response ) {
      //Add table #options to contain hits from DBpedia
      $( '#canvas' ).append('<div class="table-responsive"></div>');
      $( '#canvas .table-responsive' ).append('<table id="options" class="table table-striped table-hover"></table>');
      if (response.results.length == 0) {
        _report_no_hits(search_for);
        return;
      }
      //Add each hit as a row in table #options
      $.each( response.results, _add_result );
    },
    error: function( ) {
      $( '#canvas' ).append('<p>Sorry, the search failed</p>');
      $( '#canvas' ).append('<p><button type="button" class="btn btn-success">Retry</button></p>');
      $( "#canvas button" ).on( "click", function() {
        lookup('hits', $( '#query' ).val());
      });
    },
    timeout: 4000,
  });
}

/**
 * Creates one row in table #options, providing a bit of information
 * @param search_for {string} The string the DBpedia was searched for
 */
function _report_no_hits(search_for) {
  $( "#options" ).append( "<tr></tr>" );
  $( "#options tr:last" ).append( "<td></td>" ); 
  $( "#options tr:last td" ).html('Sorry, 0 hits for "' + search_for + '"');
}

/*
 * Add an individual DBpedia hit as a row in table #options
 * @param index {number} The index of this hit, e.g. 5
 * @param result {object} Parsed JSON object from DBpedia
 */
function _add_result( index, result ) {
  //Extract id without namespace, e.g. 'Mozart'
  var id = result.uri.split("/").pop();
  //Append a row displaying this DBpedia hit
	$( "#options" ).append( "<tr></tr>" );
  $( "#options tr:last" ).append( '<td><button type="button" class="btn btn-success">Add</button></td>' );
  $( "#options tr:last button" ).on( "click", function() {
      $(this).prop('disabled', true);
      _add_to_feed(id);
  });
	$( "#options tr:last" ).append( "<td><p><b></b></p></td>" );
	$( "#options tr:last b" ).append( result.label );
	$( "#options tr:last td:last" ).append( "<p><small></small></p>" );
	$( "#options tr:last small" ).append( _sentence(result.description) );
}

//Return the first sentence of the textual descrition,
//without stuff in parentheses
/*
 * Summarizes a DBpedia description to a form that is at most
 * 150 characters and at most one sentence. Removes anything
 * in parentheses.
 * @param text {string} The description to summarize.
 * @return {string} The summary.
 */
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

/** Hook the lookup form up to appstate */
$( "#lookup" ).submit(function( event ) {
  event.preventDefault();
  appstate_update({show:'hits', query : $( '#query' ).val()});
});

/** Call the lookup() function on appstate update */
appstate_on_update(lookup, ['show', 'query']);


