var map;

var markerImage_post = new google.maps.MarkerImage("/static/images/post.png");
var markerImage_post_highlight = new google.maps.MarkerImage("/static/images/post-highlight.png");
var markerImage_shadow = new google.maps.MarkerImage("/static/images/shadow.png",
		new google.maps.Size(45, 40),
		new google.maps.Point(0, 0),
		new google.maps.Point(0, 40),		
		new google.maps.Size(45, 40)
		);

//the posts that are currently selected
var selected = [];

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
		
		// TODO: value of select is not altered when other markers alter it!
		marker.select = false;
		
		bounds.extend(loc);
		
		$.each(location, function(j, event){
			posts[event].marker = marker;
		});
		
		// tie map events to the calendar
		google.maps.event.addListener(marker, 'mouseover', function() {
			$.each(location, function(j, event){
				$("#" + posts[event].id).addClass('highlight');
				$('#postid-' + event).addClass('highlight');
			});
			marker.setIcon(markerImage_post_highlight);
		});
		
		google.maps.event.addListener(marker, 'click', function() {			
			marker.select = !marker.select;
			
			if (!marker.select) { // not selected
				selected = [];
				
				$.each(location, function(j, event){
					$("#" + posts[event].id).removeClass('select');
				});
				marker.setIcon(markerImage_post);
			} else { // selected
				
				// deselect previous selection
				$.each(selected, function(j, event){
					$("#" + posts[event].id).removeClass('select');
					posts[event].marker.setIcon(markerImage_post);
					posts[event].marker.select = false;
				});
				selected = location;
				
				// select current location
				$.each(location, function(j, event){
					$("#" + posts[event].id).addClass('select');
				});
				marker.setIcon(markerImage_post_highlight);
			}
			
			updateSelected();			
		});
		
		google.maps.event.addListener(marker, 'dblclick', function() {
			window.location = post.location.permalink;
		});
		
		google.maps.event.addListener(marker, 'mouseout', function() {
			$.each(location, function(j, event){
				$("#" + posts[event].id).removeClass('highlight');
				$('#postid-' + event).removeClass('highlight');
			});
			if (!marker.select) {
				marker.setIcon(markerImage_post);
			}
		});
		
		/* This is a little complicated, so here's an explanation: 
		 * Basically, we will iterate through every event in this particular location.
		 * The end result is that every event will be iterated through once (if it has a location!).
		 * 
		 * This means that there needs to be some trickery, because one date may map to more than one
		 * location, and vice versa.
		 */
		$.each(location, function(j, event){
			
			/* Hover: this is simple */
			$("#" + posts[event].id).hover(
				function () {
					marker.setIcon(markerImage_post_highlight);
					$(this).addClass('highlight');
					$('#postid-' + event).addClass('highlight');
				},
				function () {
					// don't reset the icon unless we're allowed to
					if (!marker.select) {
						marker.setIcon(markerImage_post);
					}
					$(this).removeClass('highlight');
					$('#postid-' + event).removeClass('highlight');
				}
			);
			
			function isDeselectable(s) {
				/*
				 * This function tells us whether or not any of the currently selected dates
				 * corresponds to the date the user just clicked on.
				 * The user obviously didn't deselect if they clicked on a date that only has
				 * different events.
				 */
				var deselect = false;
				
				$.each(s, function(k, e){
					if (e == event) {
						deselect = true;
					}
				});
				
				return deselect;
			}
			
			// Click: this is complicated
			$("#" + posts[event].id).click(				
				function () {		
					
					if (isDeselectable(selected)) { // deselect
						/* If the user did deselect, do the usual.
						 * Remember that every event for this date will be deselected since
						 * we have multiple click events bound to the same date.
						 */
						
						marker.setIcon(markerImage_post);
						marker.select = false;
						$(this).removeClass('select');
						selected.splice(selected.indexOf(event), 1);
						
					} else { // select
						
						// create a separate list to mark down the previous selection
						var remove_selected = [];
						
						// deselect previous selection
						$.each(selected, function(k, e){
							// If a previously selected element doesn't have the date of the 
							// currently selected element, remove it (no longer selected)
							if (posts[e].id != posts[event].id) {
								$("#" + posts[e].id).removeClass('select');
								posts[e].marker.setIcon(markerImage_post);
								posts[e].marker.select = false;
								
								remove_selected.push(e);
							}
						});
						
						// Remove the events marked for selection
						if (remove_selected.length > 0) {
							for (var k = 0; k < remove_selected.length; k++) {
								selected.splice(selected.indexOf(remove_selected[k]), 1);
							}
						}
						
						// Make the current location is selected.
						// Other events during this date will activate when the click is propogated.
						marker.setIcon(markerImage_post_highlight);			
						marker.select = true;
						
						// Make the current date selected.
						$(this).addClass('select');
						
						// Only add this event if it hasn't already been added.
						if (selected.indexOf(event) < 0) {
							selected.push(event);
						}
					}
					
					updateSelected();
					
					/* Note that we can't return false, we need the click to propogate to other events
					 * for this date */
				}
			);
		});
		
    });
	
	if (bounds.isEmpty() || bounds.toSpan().lat() < 0.02 || bounds.toSpan().lng() < 0.02) {
		map.setCenter(bounds.getCenter());
		map.setZoom(14);
	}
}

function updateSelected() {
	
	
	if (selected.length <= 0) {
		$('li.post').show();
	} else {
		$('li.post').hide();
		
		$.each(selected, function(i, s) {
			$('#postid-' + s).show();
		});
	}
}

$(function() {
	initialize();
	populate(locations);
});