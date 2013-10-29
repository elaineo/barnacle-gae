var map;
var marker0;
var watchID;
function initialize() {
  var mapOptions = {
    zoom: 8,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  var autoOptions = { componentRestrictions: {country: 'us'}  };
  map = new google.maps.Map(document.getElementById('map-canvas'),
    mapOptions);

  marker0 = new google.maps.Marker({
    map: map,
    draggable: false,
    visible: true,
    clickable: false,
    icon: 'http://www.gobarnacle.com:8080/static/img/icons/dot.png',
    raiseOnDrag: false
   });       
    
  // Try HTML5 geolocation
  if(navigator.geolocation) {
    // timeout at 60000 milliseconds (60 seconds)
    var options = {timeout:60000};
    geoLoc = navigator.geolocation;
    watchID = geoLoc.watchPosition(function(position) {
        var pos = new google.maps.LatLng(position.coords.latitude,
                                       position.coords.longitude);
        var geocoder = new google.maps.Geocoder();
        console.log(position);
        map.setCenter(pos);
        marker0.setPosition(pos);                   
        $('input#startlat').val(position.coords.latitude);
        $('input#startlon').val(position.coords.longitude);
        }, handleNoGeolocation, options);   
  } else {
    // Browser doesn't support Geolocation
    handleNoGeolocation(false);
  }  
}  
function handleNoGeolocation(errorFlag) {
  if (errorFlag) {
    var content = 'Error: The Geolocation service failed.';
  } else {
    var content = 'Error: Your browser doesn\'t support geolocation.';
  }
}
  
    
 
google.maps.event.addDomListener(window, 'load', initialize);


function updatePos() {
    var poslat = $('input#startlat').val();
    var poslon = $('input#startlon').val();
    var pos = new google.maps.LatLng(poslat,poslon);
    var geocoder = new google.maps.Geocoder(); 
    console.log(pos);
    map.setCenter(pos);
    marker0.setPosition(pos);       
    geocoder.geocode({ "latLng":pos }, function (results, status) {
        console.log(results, status);
        if (status == google.maps.GeocoderStatus.OK) {
            formAddr = results[0].formatted_address;
            console.log(formAddr);
            data = {};
            data.startlat = poslat;
            data.startlon = poslon;
            data.startstr = formAddr;
            $.ajax({
            type: "POST",
            dataType: "json",  
            contentType: "json",
            data: JSON.stringify(data),
            url: '/track/update',
            success: function(response) {
              console.log(response);
                if (response.status == "ok") {
                    $('#addrText').html(formAddr);
                }
              }
            });
        }
    });              
}