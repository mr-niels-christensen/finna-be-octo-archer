function reset() {
	document.getElementById("mask").style.left = "0px";
	document.getElementById("mask").style.width = document.getElementById("progressbar").offsetWidth + "px";
	document.getElementById("progressIndicator").style.zIndex  = 10;
	document.getElementById("mask").style.display = "block";
	document.getElementById("progressIndicator").innerHTML = "0%";
}

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
