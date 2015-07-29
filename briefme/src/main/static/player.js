/**
 * Clear #canvas, lists content and narrates the named item.
 * @param show {string} If not == 'player', this function
 * returns without any effect.
 * @param item {string} The item to play, e.g. 'Mozart'.
 */
function _play_item(show, item) {
  //Check show, return if not == 'player'
  if (show != 'player') {
    return;
  }
  //Clear #canvas
  $( "#canvas" ).empty();
	$.ajax({//TODO: Handle failures
	url: '/get-item/dbpedia-resource/' + encodeURIComponent(item),//TODO provide url from server
	dataType: 'json',
	success: function (response) {
		$.each(response.data, function (index, label_or_abstract){
			//TODO: Allow pause/stop
      if (index % 2 == 0) {
        $( '#canvas' ).append( '<p></p>' );
        $( '#canvas p:last' ).html( label_or_abstract );        
      }
			_narrate_text(label_or_abstract);
		})
	},
	timeout: 2500,
	});
}

/**
 * Narrates the given text.
 * @param txt {string} A string of sentences, delimited by '.'s
 */
function _narrate_text(txt) {
  //See http://updates.html5rocks.com/2014/01/Web-apps-that-talk---Introduction-to-the-Speech-Synthesis-API
  //Dodge https://code.google.com/p/chromium/issues/detail?id=369472
  var txts = txt.split('.');
  $.each(txts, function( index, value ) {
  	if (value.length > 349) {//TODO: Handle this
        console.log(index + ': Too long, ' + value.length);
   		return;
  	}
    var msg = new SpeechSynthesisUtterance(value);
    msg.onend = function(event) {
      console.log(index + ': Finished');
    };
    window.speechSynthesis.speak(msg);    
  })  
}

/** Call _play_item() when appstate changes */
appstate_on_update(_play_item, ['show', 'item']);
