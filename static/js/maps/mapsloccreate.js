function initialize() {
  var mapOptions = {
    zoom: 4,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  var autoOptions = { componentRestrictions: {country: 'us'}  };
  var map = new google.maps.Map(document.getElementById('map-canvas'),
    mapOptions);

   var marker0 = new google.maps.Marker({
    map: map,
    draggable: true,
    visible: false,
    icon: '/static/img/icons/map/marker-car.png'
   });       
    
  var marker1 = new google.maps.Marker({
    map: map,
    draggable: true,
    visible: false,
    icon: '/static/img/icons/map/marker-star.png'
  });
       
    
  // Try HTML5 geolocation
  if(navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
    var pos = new google.maps.LatLng(position.coords.latitude,
                                       position.coords.longitude);
    var geocoder = new google.maps.Geocoder();                                       
    console.log(position);
    map.setCenter(pos);
    marker0.setPosition(pos);
    marker0.setVisible(true);      
    geocoder.geocode({ "latLng":pos }, function (results, status) {
                        console.log(results, status);
                    if (status == google.maps.GeocoderStatus.OK) {
                        formAddr = results[0].formatted_address;
                        console.log(formAddr);
                        $('input#map0Field').val(formAddr);
                        $('input#startstr').val(formAddr);                            
                    } });       
    $('input#startlat').val(position.coords.latitude);
    $('input#startlon').val(position.coords.longitude);              
    }, function() {
      handleNoGeolocation(true);
    });

  } else {
    // Browser doesn't support Geolocation
    handleNoGeolocation(false);
  }
  

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
  
}

function handleNoGeolocation(errorFlag) {
  if (errorFlag) {
    var content = 'Error: The Geolocation service failed.';
  } else {
    var content = 'Error: Your browser doesn\'t support geolocation.';
  }

  var options = {
    map: map,
    position: new google.maps.LatLng(60, 105),
    content: content
  };

  map.setCenter(options.position);
}    
    
 
google.maps.event.addDomListener(window, 'load', initialize);
