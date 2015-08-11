function _forward_to_checkpoint(utlist, checkpoint) {
  return $.map(utlist, function (ut, index) {
    return (index > checkpoint) ? ut : null;
  });
}

/**
 * Event handler for the play/pause/resume button of a channel item.
 * @param event {Event} Must have the name of the relevant item
 * as event.data.name
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
  } else {
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

function _player_init(btn, response, checkpoint) {
  btn.data('initialized', true);
  btn.data('playing', false);
  var utlist = response.SpeechSynthesisUtterances;
  utlist = _forward_to_checkpoint(utlist, checkpoint);
  btn.data('utterances', utlist);
}
function _player_on_play(btn) {
  var utlist = btn.data('utterances');
  console.log(utlist.length);
  if (0 == utlist.length) {
    return;
  };
  btn.data('playing', true);
  var ut = utlist.shift();
  console.dir(ut);
  btn.data('current_utterance', ut);
  var msg = new SpeechSynthesisUtterance();
  $.each(ut, function (key, val) {msg[key]=val});
  msg.onend = function(event) {
    console.log('onend');
    if (!btn.data("playing")) {//pause/cancel caused a call to msg.onend
      return;
    };
    ajax_set_checkpoint(ut._name, ut._index);
    _player_on_play(btn);
  };
  console.log('SPEAK');
  window.speechSynthesis.speak(msg);
  btn.html('Pause');
}

function _player_on_pause(btn) {
  btn.data('playing', false);
  btn.data('utterances').unshift(btn.data('current_utterance'));
  window.speechSynthesis.pause();
  window.speechSynthesis.cancel();
  btn.html('Play');
}
