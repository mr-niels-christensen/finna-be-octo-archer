/**
 * Event handler for the play/pause button of a channel item.
 * @param event {Event} Click event of the button
 */
function player_on_play_pause(event) {
  event.preventDefault();
  var btn = $(event.target);
  if (btn.data('initialized')) {
    /* Chrome (especially on Android) does a lot of weird stuff with
     the speaking/paused state, so we need to be hard-handed (using cancel) 
     and keep the state ourselves. */
    if (btn.data('playing')) {
      _player_on_pause(btn);
    } else {
      _player_on_play(btn);
    }
  } else { //Load item from server, initialize and start playing
    var item_name = event.target.name;
    var checkpoint = event.target.value;
    $.ajax({
      url: '/item/' + encodeURIComponent(item_name),//TODO provide url from server
      dataType: 'json',
      timeout: 2500,
    }).done(function (response) {
      _player_init(btn, response, checkpoint);
      _player_on_play(btn);
    });
  };
}

/**
 * Initializes Play button with item from server.
 * @param btn {Selector} the Play button to init
 * @param response {object} the item delivered by the server
 * @param checkpoint {int} Last index that has already been played
 */
function _player_init(btn, response, checkpoint) {
  btn.data('initialized', true);
  btn.data('playing', false);
  var utlist = response.SpeechSynthesisUtterances;
  utlist = _forward_to_checkpoint(utlist, checkpoint);
  btn.data('utterances', utlist);
}

/*
 * Starts playing the utterances already
 * associated with the Play button
 * @param btn {Selector} the Play button
 */
function _player_on_play(btn) {
  var utlist = btn.data('utterances');
  if (0 == utlist.length) {
    return;
  };
  btn.data('playing', true);
  var ut = utlist.shift();
  btn.data('current_utterance', ut);
  var msg = new SpeechSynthesisUtterance();
  $.each(ut, function (key, val) {msg[key]=val});
  msg.onend = function(event) {
    if (!btn.data("playing")) {//pause/cancel caused a call to msg.onend
      return;
    };
    ajax_set_checkpoint(ut._name, ut._index);
    _player_on_play(btn);
  };
  window.speechSynthesis.speak(msg);
  btn.html('Pause');
}

/**
 * Stops playing the item associated with the given button.
 * @param btn {Selecor} The Play (Pause) button pressed.
 */
function _player_on_pause(btn) {
  btn.data('playing', false);
  btn.data('utterances').unshift(btn.data('current_utterance'));
  window.speechSynthesis.pause();
  window.speechSynthesis.cancel();
  btn.html('Play');
}

/**
 * Filters the given list, removing an initial part.
 * @param utlist {array} The list to filter, e.g. ['a','b','c']
 * @param checkpoint {int} Indexes below this number will be
 * filtered.
 * @return The filtered list, e.g. with parameters ['a','b','c']
 * and 0 returns ['b', 'c'].
 */
function _forward_to_checkpoint(utlist, checkpoint) {
  return $.map(utlist, function (ut, index) {
    return (index > checkpoint) ? ut : null;
  });
}


