var defaultPt = new google.maps.LatLng(32.72,-117.16);
function initializeSub() {

  var mapSubOptions = {
    center: new google.maps.LatLng(40, -122),
    panControl: false,
    zoomControl: false,
    scaleControl: false,    
    draggable: false,
    scrollwheel: false,
    navigationControl: false,
    mapTypeControl: false,
    zoom: 4,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };

  var map = new google.maps.Map(document.getElementById('map-canvas'),
    mapSubOptions);

  var waypoints = [];
  var routePaths=[];
  for (i in routei5) {
    p = routei5[i];
    waypoints.push(new google.maps.LatLng(i,p));
  }  
  routePaths = new google.maps.Polyline({
    path: waypoints,
    strokeColor: "#FF0000",
    strokeOpacity: 1.0,
    strokeWeight: 2
  });
  routePaths.setMap(map);
    
  var marker0 = new google.maps.Marker({
    position: new google.maps.LatLng(47.60,-122.33),
    map: map,
    draggable: true,
    visible: true,
    icon: '/static/img/icons/map/marker-car.png'
  });
  mpoint = marker0.getPosition();
  checkinput = $('input#substartlat').val();
  if (checkinput=='') {
    $('input#substartlat').val(mpoint.lat());
    $('input#substartlon').val(mpoint.lng());  
  }
  var marker1 = new google.maps.Marker({
    position: defaultPt,
    map: map,
    draggable: true,
    visible: true,
    icon: '/static/img/icons/map/marker-car.png'
  });
  mpoint = marker1.getPosition();
  checkinput = $('input#subdestlat').val();
  if (checkinput=='') {
    $('input#subdestlat').val(mpoint.lat());
    $('input#subdestlon').val(mpoint.lng());  
  }  

  google.maps.event.addListener(marker0, 'dragend', function() {
    var geocoder = new google.maps.Geocoder();
    var formAddr;
    var temppoint = marker0.getPosition();
    var mpoint = mapToRoute(temppoint);
    $('input#substartlat').val(mpoint.lat());
    $('input#substartlon').val(mpoint.lng());  
    marker0.setPosition(mpoint);
    geocoder.geocode({ "latLng":mpoint }, function (results, status) {
                        console.log(results, status);
                        if (status == google.maps.GeocoderStatus.OK) {
                            formAddr = results[1].formatted_address;
                            console.log(formAddr);
                            $('input#sub0Field').val(formAddr);
                            $('input#substartstr').val(formAddr);
                        } }); 
  });
  google.maps.event.addListener(marker1, 'dragend', function() {
    var geocoder = new google.maps.Geocoder();
    var formAddr;
    var temppoint = marker1.getPosition();
    var mpoint = mapToRoute(temppoint);
    $('input#subdestlat').val(mpoint.lat());
    $('input#subdestlon').val(mpoint.lng());   
    marker1.setPosition(mpoint);
    geocoder.geocode({ "latLng":marker1.getPosition() }, function (results, status) {
                        console.log(results, status);
                        if (status == google.maps.GeocoderStatus.OK) {
                            formAddr = results[1].formatted_address;
                            console.log(formAddr);
                            $('input#sub1Field').val(formAddr);
                            $('input#subdeststr').val(formAddr);
                        } });
  });         
}
google.maps.event.addDomListener(window, 'load', initializeSub);

function mapToRoute(mpoint) {
  var lat = mpoint.lat().toFixed(2);
  if (lat > 48.95)
    lat = 48.95;
  else if (lat < 32.56)
    lat = 32.56;  
  maplon = routei5[lat];
  if (maplon == 'undefined')
    mappoint = defaultPt;
  else
    mappoint = new google.maps.LatLng(lat,maplon);
  return mappoint;
}
