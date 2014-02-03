function initialize() {
  // Bounding box: give priority to Calif locs
  var swLL = new google.maps.LatLng(31.58,-125.82);
  var neLL = new google.maps.LatLng(41.90,-115.67);
  var boundsBox = new google.maps.LatLngBounds(swLL,neLL);
  var autoOptions = { 
    componentRestrictions: {country: 'us'},  
    bounds: boundsBox
    };
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
    getDirs();
    $('input#startstr').val(place0.formatted_address);
    $('input#startlat').val(place0.geometry.location.lat());
    $('input#startlon').val(place0.geometry.location.lng());
    $('#map0Err').html('');
  });
  
 }
google.maps.event.addDomListener(window, 'load', initialize);

  function getDirs() {
    var directionsService = new google.maps.DirectionsService();
    var start = $('#map0Field').val();
    /** TODO: add support for waypoints **/
    var end = '78701';
    var request = {
      origin:start,
      destination:end,
      travelMode: google.maps.TravelMode.DRIVING
    };
    directionsService.route(request, function(response, status) {
    if (status == google.maps.DirectionsStatus.OK) {
      console.log(response.routes[0]);
      var distance = response.routes[0].legs[0].distance.value;
      $('#distance').val(distance);
          calc_cost(0);
      }
    });
  }
  
function extract_zip(aString) {
    var el = $('<div></div>');
    el.html(aString);
    var zip = el.children('.postal-code').html();
    return zip;
}