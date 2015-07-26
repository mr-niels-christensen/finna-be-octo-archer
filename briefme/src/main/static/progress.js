//TODO: Give the progress bar variable size, it's fixed to 200px right now

//Put the progress bar back to 0%
function reset_progress_bar(id) {
	var parent = $("#" + id);
	parent.removeClass("working");
	parent.removeClass("complete");
	parent.find(".mask").css("left", "0%");
	parent.find(".mask").width("100%");
	//document.getElementById("progressIndicator").style.zIndex  = 10;
	parent.find(".progressIndicator").html("0%");
}

//Set the progress bar to the given fraction between 0 and 1
function setProgress(id, fraction) {
	//TODO Does not work with e.g. id="George_H._W._Bush" because the "." annoys jquery selectors
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
	//var width = parent.width();
	//var newLeft = Math.floor(fraction*width);
	//var newWidth = width - newLeft;
	//document.getElementById("mask").style.left = curLeft + "px";
	//if(parseInt(document.getElementById("mask").offsetWidth)>10)document.getElementById("mask").style.width = curWidth + "px";

}
