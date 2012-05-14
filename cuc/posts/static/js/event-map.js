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

function populate(locations) {
	 var bounds = new google.maps.LatLngBounds();
	
	$.each(locations, function(i, location) {
		var post = posts[location[0]];
		
		var loc = new google.maps.LatLng(post.location.latitude, post.location.longitude);
		
		var marker = new google.maps.Marker({
			position: loc,
			icon: markerImage_post,
			shadow: markerImage_shadow,
			map: map,
			title: post.location.name,
		});
		
		bounds.extend(loc);
		
		// tie map events to the calendar
		google.maps.event.addListener(marker, 'mouseover', function() {
			$.each(location, function(j, event){
				$("#" + posts[event].id).addClass('highlight');
				console.log(posts[event].id);
			});
			marker.setIcon(markerImage_post_highlight);
		});
		
		google.maps.event.addListener(marker, 'dblclick', function() {
			window.location = post.location.permalink;
		});
		
		google.maps.event.addListener(marker, 'mouseout', function() {
			$.each(location, function(j, event){
				$("#" + posts[event].id).removeClass('highlight');
			});
			marker.setIcon(markerImage_post);
		});
		
		// tie calendar events to the map
		/*$("#" + post.id).on('click', function() {
			google.maps.event.trigger(marker, 'click');
		});*/
		
		$.each(location, function(j, event){
			$("#" + posts[event].id).hover(
				function () {
					marker.setIcon(markerImage_post_highlight);
				},
				function () {
					marker.setIcon(markerImage_post);
				}
			);
		});
		
    });
	
	if (bounds.isEmpty() || bounds.toSpan().lat() < 0.02 || bounds.toSpan().lng() < 0.02) {
		map.setCenter(bounds.getCenter());
		map.setZoom(14);
	}
}

$(function() {
	initialize();
	populate(locations);
});