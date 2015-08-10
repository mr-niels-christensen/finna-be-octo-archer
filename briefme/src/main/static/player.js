/**
 * Narrates the named item.
 * @param item {string} The item to play, e.g. 'Mozart'.
 */
function attach_item(item, button, checkpoint) {
	$.ajax({
	url: '/item/' + encodeURIComponent(item),//TODO provide url from server
	dataType: 'json',
	success: function (response) {
    var utlist = response.SpeechSynthesisUtterances;
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

function _forward_to_checkpoint(utlist, checkpoint) {
  return $.map(utlist, function (ut, index) {
    return (index > checkpoint) ? ut : null;
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

