/**
 * Narrates the named item.
 * @param item {string} The item to play, e.g. 'Mozart'.
 */
function attach_item(item, button, checkpoint) {
	$.ajax({
	url: '/get-item/dbpedia-resource/' + encodeURIComponent(item),//TODO provide url from server
	dataType: 'json',
	success: function (response) {
    var utlist = $.map(response.data, function (label_or_abstract, index){
      if (index == 0) {//Welcome line, opening the intro
        return _text_to_utlist(label_or_abstract, true);
      }
      if (index % 2 == 0) {//A label
        if (label_or_abstract.length > 0) {
          return _text_to_utlist('Next up: ' + label_or_abstract, true);
        }
      } else {//An abstract
        return _text_to_utlist(label_or_abstract, false);
      }
    });
    _annotate(utlist, '_name', item);
    _enumerate(utlist);
    utlist = _forward_to_checkpoint(utlist, checkpoint);
		_attach(utlist, button);
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
 * Annotates each element in utlist with its index in the list, as ._index
 * @param utlist a list of utterance objects.
 */
function _forward_to_checkpoint(utlist, checkpoint) {
  return $.map(utlist, function (ut, index) {
    return (index > checkpoint) ? ut : null;
  });
}

/**
 * Annotates each element in utlist with its index in the list, as ._index
 * @param utlist a list of utterance objects.
 */
function _enumerate(utlist) {
  $.each(utlist, function (index, ut) {
    ut._index = index;
  });
}

/**
 * Annotates each element in utlist with the given key and value
 * @param utlist a list of utterance objects.
 */
function _annotate(utlist, key, value) {
  $.each(utlist, function (index, ut) {
    ut[key] = value;
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
    if (value.length > 300) {//TODO: Actually handle this
      //Too long
      return null;
    }
    if (value.length < 2) {
      //Too short
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
function _attach(utlist, button) {
  var msg = new SpeechSynthesisUtterance();
  msg.onend = function(event) {
    if (!button.data("playing")) {//pause/cancel caused a call to msg.onend
      return;
    }
    ajax_set_checkpoint(msg._current._name, msg._current._index);
    _play_next(msg, utlist, button);
  };
  button.data("playing", false);
  button.on( "click", 
             {msg: msg, utlist: utlist},
              _on_play_pause);
}

/**
 * Event handler for the play/pause/resume button of a channel item.
 * @param event {Event} Must have the name of the relevant item
 * as event.data.name
 */
function _on_play_pause(event) {
  /* Chrome (especially on Android) does a lot of weird stuff with
     the speaking/paused state, so we need to be hard-handed (using cancel) 
     and keep the state ourselves. */
  if ($(this).data("playing")) {
    $(this).data("playing", false);
    event.data.utlist.unshift(event.data.msg._current);
    window.speechSynthesis.pause();
    window.speechSynthesis.cancel();
    $(this).html("Play");
  } else {
    $(this).data("playing", true)
    _play_next(event.data.msg, event.data.utlist, $(this));
    $(this).html('Pause');
  }
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
function _play_next(msg, utlist, button){
  if (0 == utlist.length) {
    return;
  };
  var ut = utlist.shift();
  msg._current = ut;
  //TODO link more info as msg._foo
  $.each(ut, function (key, val) {msg[key]=val});
  window.speechSynthesis.speak(msg);
}

