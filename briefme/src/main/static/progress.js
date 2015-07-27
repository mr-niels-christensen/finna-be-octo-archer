//TODO: Give the progress bar variable size, it's fixed to 200px right now

//Append HTML representing a progress bar with the given id
function progress_append(id, dest_selector) {
	dest_selector.append('<td id="' + id + '"><div class="progressbar"><div class="gradient"></div><div class="mask"></div><div class="progressIndicator">0%</div></div></td>');
}

//Put the progress bar back to 0%
function progress_reset(id) {
	var parent = $("#" + id);
	parent.removeClass("working");
	parent.removeClass("complete");
	parent.find(".mask").css("left", "0%");
	parent.find(".mask").width("100%");
	//document.getElementById("progressIndicator").style.zIndex  = 10;
	parent.find(".progressIndicator").html("0%");
}

//Set the progress bar to the given fraction between 0 and 1
function progress_set(id, fraction) {
	var parent = $('td[id="' + id + '"]');//ids may have '.'s in them, so don't try $('#'+id)
	parent.addClass("working");
	var pct = Math.floor(fraction*100);
	parent.find(".progressIndicator").html(pct + "%");
	if(fraction > 0.99) {
		parent.addClass("complete");
		return;
	}
	parent.find(".mask").css("left", pct + "%");
	parent.find(".mask").width((100 - pct) + "%");
}
