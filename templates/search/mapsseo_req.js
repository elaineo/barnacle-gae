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

  {% if center is defined %}
    center = new google.maps.LatLng({{center[0]}}, {{center[1]}});
  {% else %}
    center =  new google.maps.LatLng(40, -99);
  {% endif %}
  
  var mapOptions = {
    center: center,
    zoom: 4,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  var autoOptions = { componentRestrictions: {country: 'us'}  };
  var map = new google.maps.Map(document.getElementById('map-canvas'),
    mapOptions);

  var routePaths=[];
  var marker = new Array();
  var infowindow = new Array();    
  {% for mark in markers %}
    m = new google.maps.LatLng({{mark.lat}},{{mark.lon}});        
    marker[{{ loop.index0 }}] = new google.maps.Marker({
        position:m,
        clickable: true,
        title: 'Get me to {{mark.loc}}',
        animation: google.maps.Animation.DROP,
        icon: '/static/img/icons/map/marker-barnacle.png',
        raiseOnDrag: false,
        visible: true
    });
    content = 'To {{mark.loc}} by {{mark.delivby}} <br> \n${{mark.rates}}<br><a href="{{mark.url}}">View Request</a>';
    infowindow[{{loop.index0}}] = new google.maps.InfoWindow({
       content: content
    });
    google.maps.event.addListener(marker[{{loop.index0}}], 'click', function(n) {
      return function() {
        infowindow[n].open(map,marker[n]);
      }
    }({{loop.index0}}));
    routePaths.push(marker[{{loop.index0}}]);
  {% endfor %}
  {% for path in paths %}
       waypoints = [];
       {% for p in path %}
        waypoints.push(new google.maps.LatLng({{p[0]}},{{p[1]}}));
       {% endfor %}
      routePaths.push(new google.maps.Polyline({
        path: waypoints,
        strokeColor: "#FF0000",
        strokeOpacity: 1.0,
        strokeWeight: 2
      }));
  {% endfor %}      

            
  for (q in routePaths) {
    routePaths[q].setMap(map);
  }
}
