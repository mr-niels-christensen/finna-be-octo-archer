
function _clean(id) {
	return id.replace(/\W/g, "_");
}
//Append HTML representing a progress bar with the given id
function progress_append(id, dest_selector, width, height) {
	id = _clean(id);
	dest_selector.append('<div id="' + id + '"></div>');
	var parent = $("#" + id);
	parent.width(width);
	parent.height(height);
	parent.append('<div class="progressbar"></div>');
	var bar = parent.find( '.progressbar' );
	bar.append('<div class="gradient"></div>');
	bar.append('<div class="mask"></div>');
	bar.append('<div class="progressIndicator">0%</div>');
	bar.append('<span class="glyphicon glyphicon-ok progresstick"></span>');
	bar.append('<span class="glyphicon glyphicon-hourglass progresshourglass"></span>');
}

//Put the progress bar back to 0%
function progress_reset(id) {
	id = _clean(id);
	var parent = $("#" + id);
	parent.removeClass("issue");
	parent.removeClass("working");
	parent.removeClass("complete");
	parent.find(".mask").css("left", "0%");
	parent.find(".mask").width("100%");
	//document.getElementById("progressIndicator").style.zIndex  = 10;
	parent.find(".progressIndicator").html("0%");
}

//Set the progress bar to the given fraction between 0 and 1
function progress_set(id, fraction) {
	id = _clean(id);
	var parent = $("#" + id);
	parent.removeClass("issue");
	parent.addClass("working");
	var pct = Math.floor(fraction*100);
	parent.find(".progressIndicator").html(pct + "%");
	if(fraction > 0.99) {
		parent.removeClass("issue");
		parent.removeClass("working");
		parent.addClass("complete");
		return;
	}
	parent.find(".mask").css("left", pct + "%");
	parent.find(".mask").width((100 - pct) + "%");
}

/*
 * Reports a (maybe temporary) issue with the progress.
 * @param id {string} The HTML/CSS id of the progress bar to update
 */
function progress_issue(id) {
	//TODO: Reuse code for clean parent, or make an object
	id = _clean(id);
	var parent = $("#" + id);
	parent.removeClass("working");
	parent.addClass("issue");
}