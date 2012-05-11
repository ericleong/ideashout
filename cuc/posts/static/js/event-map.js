var map;

var markerImage_post = new google.maps.MarkerImage("/static/images/post.png");
var markerImage_post_highlight = new google.maps.MarkerImage("/static/images/post-highlight.png");
var markerImage_shadow = new google.maps.MarkerImage("/static/images/shadow.png",
		new google.maps.Size(45, 40),
		new google.maps.Point(0, 0),
		new google.maps.Point(0, 40),		
		new google.maps.Size(45, 40)
		);

function initialize() {
	// generates map
	
	var myOptions = {
		zoom : 2,
		center : new google.maps.LatLng(0, 0),
		disableDefaultUI : true,
		mapTypeId : google.maps.MapTypeId.ROADMAP,
		panControl: true,
		zoomControl: true,
		mapTypeControl: false,
		scaleControl: false,
		streetViewControl: true,
		overviewMapControl: false,
	};
	
	map = new google.maps.Map(document.getElementById("event-map"), myOptions);	
}

function populate(posts) {
	 var bounds = new google.maps.LatLngBounds();
	
	$.each(posts, function(i, post) {
		var loc = new google.maps.LatLng(post.location.latitude, post.location.longitude);
		
		post.marker = new google.maps.Marker({
			position: loc,
			icon: markerImage_post,
			shadow: markerImage_shadow,
			map: map,
			title: post.location.name,
		});
		
		bounds.extend(loc);
		
		// tie map events to the calendar
		google.maps.event.addListener(post.marker, 'mouseover', function() {
			$("#" + post.date).addClass('highlight');
			post.marker.setIcon(markerImage_post_highlight);
		});
		
		google.maps.event.addListener(post.marker, 'click', function() {
			$("#" + post.date).addClass('highlight');
		});
		
		google.maps.event.addListener(post.marker, 'mouseout', function() {
			$("#" + post.date).removeClass('highlight');
			post.marker.setIcon(markerImage_post);
		});
		
		// tie calendar events to the map
		$("#" + post.date).on('click', function() {
			google.maps.event.trigger(post.marker,'click');
		});
		
		$("#" + post.date).hover(
			function () {
				google.maps.event.trigger(post.marker, 'mouseover');
			},
			function () {
				google.maps.event.trigger(post.marker, 'mouseout');
			}
		);
    });
	
	if (bounds.isEmpty() || bounds.toSpan().lat() < 0.02 || bounds.toSpan().lng() < 0.02) {
		map.setCenter(bounds.getCenter());
		map.setZoom(14);
	}
}

$(function() {
	$(window).resize(function() {
		google.maps.event.trigger(map, 'resize');
	});

	initialize();
	populate(posts);
});