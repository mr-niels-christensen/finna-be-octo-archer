//Updates the local state with the given mappings.
//Existing mappings remain if the key is not in the given map,
//otherwise they are overrideen
//map: e.g. {'foo' : 'bar','key':2}
function appstate_update(map) {
	var link_url = jQuery.param.fragment( '/index.html', map );
    document.location.href = link_url;
}

//Registers a callback when app state changes
//f: the callback, e.g. function(count){console.log(count);}
//arr_of_keys: the keys of the values needed as parameters to f, e.g. ['count']
function appstate_on_update(f, arr_of_keys) {
	$(window).bind( 'hashchange', function( event ) {
  		_appstate_apply(f, arr_of_keys, event);
	});
}

//Looks up the given keys and passes them as parameters to the callback f
//f: a callback
//arr_of_keys: The keys to look up
//event: A hashchange event provided by BBQ
function _appstate_apply(f, arr_of_keys, event) {
	f.apply(this, $.map(arr_of_keys, function ( key ) {
		return event.getState( key );
	}))
}

//Make this the very last JS to load, if you need appstate for initialization
//$(window).trigger( 'hashchange' );

