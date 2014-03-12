function initialize() {
  // Try HTML5 geolocation
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
    });
  }

  var autoOptions = { componentRestrictions: {country: 'us'}  };
  
  var input0 = /** @type {HTMLInputElement} */(document.getElementById('map0Field'));
  var autocomplete0 = new google.maps.places.Autocomplete(input0,autoOptions);
  
  google.maps.event.addListener(autocomplete0, 'place_changed', function() {
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
  });
  
}
google.maps.event.addDomListener(window, 'load', initialize);
