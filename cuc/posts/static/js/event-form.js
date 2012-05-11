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
	// generates map
	geocoder = new google.maps.Geocoder();

	var myOptions = {
		zoom : 2,
		center : new google.maps.LatLng(0, 0),
		disableDefaultUI : true,
		mapTypeId : google.maps.MapTypeId.ROADMAP,
		panControl : true,
		zoomControl : true,
		mapTypeControl : false,
		scaleControl : false,
		streetViewControl : true,
		overviewMapControl : false,
	};

	map = new google.maps.Map(document.getElementById("event-form-map"),
			myOptions);
}

function findAddress() {
	var address = $('#id_address').val();

	geocoder.geocode({
		'address' : address
	}, function(results, status) {
		if (status == google.maps.GeocoderStatus.OK) {
			$('#event-form-map').show();
			google.maps.event.trigger(map, 'resize');
			
			map.setCenter(results[0].geometry.location);
			marker.setPosition(results[0].geometry.location);
			marker.setMap(map);
			map.setZoom(12);
			
			$('#id_address').removeClass('errorlist');
		} else {
			$('#id_address').addClass('errorlist');
		}
	});
}

function checkAddress() {
	if ($('#id_address').val() != addr
			&& $('#id_address').val().length > 2) {
		// make sure that the search field has changed
		addr = $('#id_address').val();

		// make sure the user has finished typing
		setTimeout(
				"if (addr == $('#id_address').val()){ findAddress();}",
				500);
	}
}

$(function() {
	initialize();

	marker = new google.maps.Marker({
		map : map,
		icon: markerImage_post,
		shadow: markerImage_shadow,
	});
	
	google.maps.event.addListener(marker, 'position_changed', function() {
		$('#id_latitude').val(marker.getPosition().lat());
		$('#id_longitude').val(marker.getPosition().lng());
	});
	
	$('#id_location').keyup(checkAddress);
	$('#id_address').keyup(checkAddress);
});