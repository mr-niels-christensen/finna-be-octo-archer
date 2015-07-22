//TODO: Give the progress bar variable size, it's fixed to 200px right now

//Put the progress bar back to 0%
function reset_progress_bar() {
	document.getElementById("mask").style.left = "0px";
	document.getElementById("mask").style.width = document.getElementById("progressbar").offsetWidth + "px";
	document.getElementById("progressIndicator").style.zIndex  = 10;
	document.getElementById("mask").style.display = "block";
	document.getElementById("progressIndicator").innerHTML = "0%";
}

//Set the progress bar to the given fraction between 0 and 1
function setProgress(fraction) {
	document.getElementById("progressIndicator").innerHTML = Math.floor(fraction*100) + "%";
	if(fraction > 0.99) {
		document.getElementById("mask").style.display = "none";
		return;
	}
	curLeft = Math.floor(fraction*200.0);
	curWidth = 200-curLeft;
	document.getElementById("mask").style.left = curLeft + "px";
	if(parseInt(document.getElementById("mask").offsetWidth)>10)document.getElementById("mask").style.width = curWidth + "px";

}
