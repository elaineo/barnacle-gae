var zip0 = '91775';

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
    zip0 = extract_zip(place0.adr_address);
    $('input#startstr').val(place0.formatted_address);
    $('input#startlat').val(place0.geometry.location.lat());
    $('input#startlon').val(place0.geometry.location.lng());
    $('input#startzip').val(zip0);
    update_cost();
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
    zip1 = extract_zip(place1.adr_address);
    $('input#deststr').val(place1.formatted_address);
    $('input#destlat').val(place1.geometry.location.lat());
    $('input#destlon').val(place1.geometry.location.lng());
    $('input#destzip').val(zip1);    
    update_cost();
    $('#map1Err').html('');
  });

}
google.maps.event.addDomListener(window, 'load', initialize);

function extract_zip(aString) {
    var el = $('<div></div>');
    el.html(aString);
    var zip = el.children('.postal-code').html();
    return zip;
}

function update_cost() {
    x = zone_lookup(parseInt($('input#startzip').val()));
    y = zone_lookup(parseInt($('input#destzip').val()));
    if (x==-1 || y==-1) {
        $('#serviceErr').html('We currently do not have drivers in that location. Please <a href="/post/request">submit a delivery request</a>.');
        $('#submit_btn').attr('disabled','disabled');
        $('input#estcost').val(0);
    } else {
        size = $("input[name=vcap]:checked").val();        
        var estcost = rates[x][y];
        if (size == '1') estcost = 1.25*estcost;
        else if (size == '2') estcost = 2*estcost;
        $('input#estcost').val(estcost);
        $('#serviceErr').html('');
        $('#submit_btn').removeAttr('disabled');
        $('input#estcostdup').val(estcost);
    }
    
}

function zone_lookup(zip) {
  if (zip == 94043) return 0;
  else if (zip == 91775) return 4;
  else if (zone1MV.indexOf(zip) != -1) return 1;
  else if (zone2MV.indexOf(zip) != -1) return 2;
  else if (zone3MV.indexOf(zip) != -1) return 3;
  else if (zone1SG.indexOf(zip) != -1) return 5;  
  else if (zone2SG.indexOf(zip) != -1) return 6;    
  else if (zone3SG.indexOf(zip) != -1) return 7;    
  else return -1;
}