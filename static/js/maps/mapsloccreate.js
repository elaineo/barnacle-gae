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
    visible: false
   });       
   
    marker0.setIcon(/** @type {google.maps.Icon} */({
      url: 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=A|990099|ffffff',
      size: new google.maps.Size(71, 71),
      origin: new google.maps.Point(0, 0),
      anchor: new google.maps.Point(17, 34),
      scaledSize: new google.maps.Size(25, 35)
    }));
    
  var marker1 = new google.maps.Marker({
    map: map,
    draggable: true,
    visible: false
  });
    marker1.setIcon(/** @type {google.maps.Icon} */({
      url: 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=B|990099|ffffff',
      size: new google.maps.Size(71, 71),
      origin: new google.maps.Point(0, 0),
      anchor: new google.maps.Point(17, 34),
      scaledSize: new google.maps.Size(25, 35)
    }));  
       
    
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
