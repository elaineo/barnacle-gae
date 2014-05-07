function initialize_home(mapURL) {
    var mapOptions = {
        center: new google.maps.LatLng(40, -99),
        zoom: 4,
        mapTypeId: google.maps.MapTypeId.TERRAIN,
        disableDefaultUI: true,
        draggable: false,
        scrollwheel: false
    };
    var map = new google.maps.Map(document.getElementById("map-canvas"),mapOptions);
    map.mapTypes.set('map_style', styledMap);
    map.setMapTypeId('map_style');
    
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
}