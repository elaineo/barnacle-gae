function initialize() {
  var autoOptions = { componentRestrictions: {country: 'us'}  };
  
  var input0 = /** @type {HTMLInputElement} */(document.getElementById('map0Field'));
  var autocomplete0 = new google.maps.places.Autocomplete(input0,autoOptions);

  var input1 = /** @type {HTMLInputElement} */(document.getElementById('map1Field'));
  var autocomplete1 = new google.maps.places.Autocomplete(input1,autoOptions);
 
  
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
  
  
  google.maps.event.addListener(autocomplete1, 'place_changed', function() {
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
  });

}
google.maps.event.addDomListener(window, 'load', initialize);


function mapsAutoDynamic(mapName, inputName) {
  var autoOptions = { componentRestrictions: {country: 'us'}  };
  
  var input0 = /** @type {HTMLInputElement} */(document.getElementById(mapName+'Field'));
  var autocomplete0 = new google.maps.places.Autocomplete(input0,autoOptions);
  
  google.maps.event.addListener(autocomplete0, 'place_changed', function() {
    input0.className = '';
    var place0 = autocomplete0.getPlace();
    if (!place0.geometry) {
      // Inform the user that the place was not found and return.
      input0.className = 'notfound';
      return;
    }
    $('input#'+inputName+'str').val(place0.formatted_address);
    $('input#'+inputName+'lat').val(place0.geometry.location.lat());
    $('input#'+inputName+'lon').val(place0.geometry.location.lng());
    $('#'+mapName+'Err').html('');
  });
}