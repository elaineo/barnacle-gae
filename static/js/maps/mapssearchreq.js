function initialize(mapURL,mapID) {
  var mapOptions = {
    center: new google.maps.LatLng(40, -99),
    zoom: 4,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  var autoOptions = { componentRestrictions: {country: 'us'}  };
  var map = new google.maps.Map(document.getElementById(mapID),
    mapOptions);

  var input0 = /** @type {HTMLInputElement} */(document.getElementById('map0Field'));
  var autocomplete0 = new google.maps.places.Autocomplete(input0,autoOptions);

  var input1 = /** @type {HTMLInputElement} */(document.getElementById('map1Field'));
  var autocomplete1 = new google.maps.places.Autocomplete(input1,autoOptions);
  
  autocomplete0.bindTo('bounds', map);
  autocomplete1.bindTo('bounds', map);
  
    $.ajax({
      type: "POST",
      url: mapURL,
      contentType: "json",  
      success: function(route){   
          var routePaths=[];
          var marker = new Array();
          var infowindow = new Array();
          for (k in route['markers']) {
            m = new google.maps.LatLng(route['markers'][k]['lat'],route['markers'][k]['lon']);        
            marker[k] = new google.maps.Marker({
                position:m,
                clickable: true,
                title: 'Get me to '+route['markers'][k]['loc'],
                animation: google.maps.Animation.DROP,
                icon: 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=O|B00000|ffffff',
                raiseOnDrag: false,
                visible: true
            });
            content = 'To '+route['markers'][k]['loc']+' by '+route['markers'][k]['delivby']+'<br>'+'\n$'+route['markers'][k]['rates']+'<br><a href="'+route['markers'][k]['url']+'">View Request</a>';
            infowindow[k] = new google.maps.InfoWindow({
               content: content
            });
            google.maps.event.addListener(marker[k], 'click', function(n) {
              return function() {
                infowindow[n].open(map,marker[n]);
              }
            }(k));
            routePaths.push(marker[k]);
          }
          var waypoints = [];
          console.log(route);
          if (route['waypts'] != null) {            
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
        }});    
  
  google.maps.event.addListener(autocomplete0, 'place_changed', function() {
    input0.className = '';
    var place0 = autocomplete0.getPlace();
    console.log(place0);
    if (!place0.geometry) {
      // Inform the user that the place was not found and return.
      input0.className = 'notfound';
      return;
    }
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
    $('input#destlat').val(place1.geometry.location.lat());
    $('input#destlon').val(place1.geometry.location.lng());
    $('#map1Err').html('');
    
  });

}
