/**
 * Narrates the named item.
 * @param item {string} The item to play, e.g. 'Mozart'.
 */
function play_item(item) {
  //Always cancel any ongoing utterances on update
  window.speechSynthesis.cancel();
	$.ajax({
	url: '/get-item/dbpedia-resource/' + encodeURIComponent(item),//TODO provide url from server
	dataType: 'json',
	success: function (response) {
		_play_all($.map(response.data, function (label_or_abstract, index){
      if (index % 2 == 0) {//A label
        //$( '#canvas' ).append( '<p></p>' );
        //$( '#canvas p:last' ).html( label_or_abstract );
        if (label_or_abstract.length > 0) {
          return _text_to_utlist('Next up: ' + label_or_abstract, true);
        }
      } else {//An abstract
        return _text_to_utlist(label_or_abstract, false);
      }
		}));
	},
  error: function () {
      //$( '#canvas' ).append( '<p>Waiting for server...</p>' );
      setTimeout(function () {
        play_item(item);
      } , 5000 );
  },
	timeout: 2500,
	});
}

/**
 * Converts the given text to an object with settings
 * for a SpeechSynthesisUtterance object.
 * @param txt {string} A string of sentences, delimited by '.'s
 * @param high_pitch {boolean} If true, the pitch of the voice will
 * have above-average pitch.
 * @return {object} e.g. {text: 'Hello', pitch: 1.0}
 */
function _text_to_utlist(txt, high_pitch) {
  //See http://updates.html5rocks.com/2014/01/Web-apps-that-talk---Introduction-to-the-Speech-Synthesis-API
  //Dodge https://code.google.com/p/chromium/issues/detail?id=369472
  return $.map(txt.split('.'), function( value ) {
    if (value.length > 349) {//TODO: Handle this
        console.log('Too long, ' + value.length);
      return null;
    }
    if (value.length < 2) {
        console.log('Too short, ' + value);
      return null;
    }
    return {text: value, pitch: (high_pitch) ? 1.15 : 1.0};
  });
}

/**
 * Plays a sequence of SpeechSynthesisUtterances.
 * @param utlist {array} An array of objects each with
 * settings for a SpeechSynthesisUtterance, e.g.
 * {text: 'Hello', pitch: 1.0}
 * The array will be modified.
 */
function _play_all(utlist) {
  var msg = new SpeechSynthesisUtterance();
  msg.onend = function(event) {
    _play_next(msg, utlist);
  };
  _play_next(msg, utlist);
}

/**
 * Removes and plays the first utterance in the
 * given list, by modifying and using the given
 * SpeechSynthesisUtterance.
 * @param msg {SpeechSynthesisUtterance} The object to
 * modify and pass to window.speechSynthesis.speak
 * @param utlist {array} a sequqence of utterances,
 * each one like {text: 'Hello', pitch: 1.0}
 */
function _play_next(msg, utlist){
  if (0 == utlist.length) {
    return;
  };
  var ut = utlist.shift();
  $.each(ut, function (key, val) {msg[key]=val});
  window.speechSynthesis.speak(msg);
}

