function initialize_home(mapURL) {
  // Try HTML5 geolocation

    var mapOptions = {
        center: new google.maps.LatLng(40, -99),
        zoom: 4,
        mapTypeId: google.maps.MapTypeId.TERRAIN,
        disableDefaultUI: true
    };
    var map = new google.maps.Map(document.getElementById("map-canvas"),mapOptions);
    map.mapTypes.set('map_style', styledMap);
    map.setMapTypeId('map_style');
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
  $('#swaploc').click(function() {
    var temp = marker0.getPosition();
    marker0.setPosition(marker1.getPosition());
    marker1.setPosition(temp);  
    marker1.setVisible(true);    
  });
    
    $.getJSON(mapURL, function(route){   
      var ctrLatLng = new google.maps.LatLng(route['center'][0],route['center'][1]);
      map.setCenter(ctrLatLng);
      map.setZoom(route['zoom']);

      var waypoints = [];
      var routePaths=[];
      if (route['waypts'] == null) {
        for (i in route['paths']) {
           waypoints = [];
           for (w in route['paths'][i]) {
            p = route['paths'][i][w]
            waypoints.push(new google.maps.LatLng(p[0],p[1]));
          }
          routePaths.push(new google.maps.Polyline({
            path: waypoints,
            strokeColor: "#FF0000",
            strokeOpacity: 1.0,
            strokeWeight: 2
          }));
        }
      } else {
          for (w in route['waypts']) {
            p = route['waypts'][w]
            waypoints.push(new google.maps.LatLng(p[0],p[1]));
          }
          routePaths.push(new google.maps.Polyline({
            path: waypoints,
            strokeColor: "#FF0000",
            strokeOpacity: 1.0,
            strokeWeight: 2
          }));
      }
        for (q in routePaths) {
          routePaths[q].setMap(map);
        }
    });
  var autoOptions = { componentRestrictions: {country: 'us'}  };    
  var input0 = /** @type {HTMLInputElement} */(document.getElementById('map0Field'));
  var autocomplete0 = new google.maps.places.Autocomplete(input0,autoOptions);

  var input1 = /** @type {HTMLInputElement} */(document.getElementById('map1Field'));
  var autocomplete1 = new google.maps.places.Autocomplete(input1,autoOptions);
  
  autocomplete0.bindTo('bounds', map);
  autocomplete1.bindTo('bounds', map);
  

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
    geocoder.geocode({ "latLng":mpoint }, function (results, status) {
                        console.log(results, status);
                        if (status == google.maps.GeocoderStatus.OK) {
                            formAddr = results[0].formatted_address;
                            $('input#map0Field').val(formAddr);
                        } }); 
  });
  google.maps.event.addListener(marker1, 'mouseup', function() {
    var geocoder = new google.maps.Geocoder();
    var formAddr;
    var mpoint = marker1.getPosition();    
    $('input#destlat').val(mpoint.lat());
    $('input#destlon').val(mpoint.lng());     
    geocoder.geocode({ "latLng":mpoint }, function (results, status) {
                        console.log(results, status);
                        if (status == google.maps.GeocoderStatus.OK) {
                            formAddr = results[0].formatted_address;
                            $('input#map1Field').val(formAddr);
                        } });
  });      
  if(navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
    console.log(position);    
    var geocoder = new google.maps.Geocoder();
    var ll = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
    geocoder.geocode({ "latLng": ll}, function (results, status) {
                        console.log(results, status);
                        if (status == google.maps.GeocoderStatus.OK) {
                            formAddr = results[0].formatted_address;
                            $('input#map0Field').val(formAddr);
                            $('input#startstr').val(formAddr);
                        } });    
    $('input#startlat').val(position.coords.latitude);
    $('input#startlon').val(position.coords.longitude);

    marker0.setPosition(ll);
    marker0.setVisible(true);    
    });
  }   
}