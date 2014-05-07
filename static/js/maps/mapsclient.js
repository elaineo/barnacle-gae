function initialize() {
  var mapOptions = {
    center: new google.maps.LatLng(40, -99),
    zoom: 4,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  var autoOptions = { componentRestrictions: {country: 'us'}  };
  var map = new google.maps.Map(document.getElementById('map-canvas'),
    mapOptions);

  var input0 = /** @type {HTMLInputElement} */(document.getElementById('map0Field'));
  var autocomplete0 = new google.maps.places.Autocomplete(input0,autoOptions);

  var input1 = /** @type {HTMLInputElement} */(document.getElementById('map1Field'));
  var autocomplete1 = new google.maps.places.Autocomplete(input1,autoOptions);
  
  autocomplete0.bindTo('bounds', map);
  autocomplete1.bindTo('bounds', map);
  
  var marker0 = new google.maps.Marker({
    map: map,
    draggable: true,
    visible: false,
    icon: '/static/img/icons/map/marker-barnacle.png'
  });
    
  var marker1 = new google.maps.Marker({
    map: map,
    draggable: true,
    visible: false,
    icon: '/static/img/icons/map/marker-star.png'
  });
  
  google.maps.event.addListener(autocomplete0, 'place_changed', function() {
    marker0.setVisible(false);
    input0.className = '';
    var place0 = autocomplete0.getPlace();
    console.log(place0);
    if (!place0.geometry) {
      // Inform the user that the place was not found and return.
      input0.className = 'notfound';
      return;
    }
    $('input#startstr').val(place0.formatted_address);
    $('input#startlat').val(place0.geometry.location.lat());
    $('input#startlon').val(place0.geometry.location.lng());
    $('#map0Err').html('');
    
    var bounds = new google.maps.LatLngBounds ();
    bounds.extend (place0.geometry.location);
    var place1 = autocomplete1.getPlace();
    console.log(place1);
    if (typeof place1 !== 'undefined') 
        bounds.extend (place1.geometry.location);
    // If the place has a geometry, then present it on a map.
    if (place0.geometry.viewport) {
      map.fitBounds(bounds);
    } else {
      map.setCenter(place0.geometry.location);
      map.setZoom(10);  
    }
    
    marker0.setPosition(place0.geometry.location);
    marker0.setVisible(true);
  });
  
  
  google.maps.event.addListener(autocomplete1, 'place_changed', function() {
    marker1.setVisible(false);
    input1.className = '';
    var place1 = autocomplete1.getPlace();
    if (!place1.geometry) {
      // Inform the user that the place was not found and return.
      input1.className = 'notfound';
      return;
    }
    $('input#deststr').val(place1.formatted_address);
    $('input#destlat').val(place1.geometry.location.lat());
    $('input#destlon').val(place1.geometry.location.lng());
    $('#map1Err').html('');
    
    var bounds = new google.maps.LatLngBounds ();
    bounds.extend (place1.geometry.location);
    var place0 = autocomplete0.getPlace();
    console.log(place0);    
    if (typeof place0 !== 'undefined') 
        bounds.extend (place0.geometry.location);
    // If the place has a geometry, then present it on a map.
    if (place1.geometry.viewport) {
      map.fitBounds(bounds);
    } else {
      map.setCenter(place1.geometry.location);
      map.setZoom(10);  
    }    
    marker1.setPosition(place1.geometry.location);
    marker1.setVisible(true);

  });

  google.maps.event.addListener(marker0, 'mouseup', function() {
    var geocoder = new google.maps.Geocoder();
    var formAddr;
    var mpoint = marker0.getPosition();
    console.log(mpoint);
    $('input#startlat').val(mpoint.lat());
    $('input#startlon').val(mpoint.lng());      
    geocoder.geocode({ "latLng":marker0.getPosition() }, function (results, status) {
                        console.log(results, status);
                        if (status == google.maps.GeocoderStatus.OK) {
                            formAddr = results[0].formatted_address;
                            console.log(formAddr);
                            $('input#map0Field').val(formAddr);
                            $('input#startstr').val(formAddr);                            
                        } }); 
  });
  google.maps.event.addListener(marker1, 'mouseup', function() {
    var geocoder = new google.maps.Geocoder();
    var formAddr;
    var mpoint = marker1.getPosition();
    $('input#destlat').val(mpoint.lat());
    $('input#destlon').val(mpoint.lng());      
    geocoder.geocode({ "latLng":marker1.getPosition() }, function (results, status) {
                        console.log(results, status);
                        if (status == google.maps.GeocoderStatus.OK) {
                            formAddr = results[0].formatted_address;
                            console.log(formAddr);
                            $('input#map1Field').val(formAddr);                            
                            $('input#deststr').val(formAddr);
                        } });
  });         
  google.maps.event.addListener(map, 'click', function(event) {
    var geocoder = new google.maps.Geocoder();
    var formAddr;
    geocoder.geocode({ "latLng":event.latLng }, function (results, status) {
                        console.log(results, status);
                        if (status == google.maps.GeocoderStatus.OK) {
                            formAddr = results[0].formatted_address;
                            if (marker0.getVisible() != true) {
                                marker0.setPosition(event.latLng);
                                marker0.setVisible(true);
                                $('input#map0Field').val(formAddr); 
                                $('input#startstr').val(formAddr);
                                $('input#startlat').val(event.latLng.lat());
                                $('input#startlon').val(event.latLng.lng());        
                            } else {
                                marker1.setPosition(event.latLng);
                                marker1.setVisible(true);
                                $('input#map1Field').val(formAddr); 
                                $('input#deststr').val(formAddr);
                                $('input#destlat').val(event.latLng.lat());
                                $('input#destlon').val(event.latLng.lng());        
                            }
                        } });
});  
}
google.maps.event.addDomListener(window, 'load', initialize);
