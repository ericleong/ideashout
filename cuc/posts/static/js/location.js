var map;
var geocoder;
var addr;
var marker;

var markerImage_post = new google.maps.MarkerImage("/static/images/post.png");
var markerImage_post_highlight = new google.maps.MarkerImage(
		"/static/images/post-highlight.png");
var markerImage_shadow = new google.maps.MarkerImage(
		"/static/images/shadow.png", new google.maps.Size(45, 40),
		new google.maps.Point(0, 0), new google.maps.Point(0, 40),
		new google.maps.Size(45, 40));

function initialize() {
	
	var myOptions = {
		zoom : 16,
		center : loc,
		disableDefaultUI : true,
		mapTypeId : google.maps.MapTypeId.ROADMAP,
		panControl : true,
		zoomControl : true,
		mapTypeControl : false,
		scaleControl : false,
		streetViewControl : true,
		overviewMapControl : false,
	};

	map = new google.maps.Map(document.getElementById("event-map-single"),
			myOptions);
}

$(function() {
	initialize();

	marker = new google.maps.Marker({
		map : map,
		icon: markerImage_post,
		shadow: markerImage_shadow,
		position: loc,
	});
});