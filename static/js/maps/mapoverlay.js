function initialize_map(mapURL) {
    $.getJSON(mapURL, function(route){   
      console.log(route)
      var ctrLatLng = new google.maps.LatLng(route['center'][0],route['center'][1]);
      var mapOptions = {
        zoom: route['zoom'],  
        center: ctrLatLng,
        mapTypeId: google.maps.MapTypeId.TERRAIN
      };

      var map = new google.maps.Map(document.getElementById("map-canvas"),
          mapOptions);


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
      /* check for markers */
      for (k in route['markers']) {
        m = new google.maps.LatLng(route['markers'][k][0],route['markers'][k][1]);
        if (k==0) 
          bimg = '/static/img/icons/map/marker-barnacle.png';            
        else if (k==(route['markers'].length-1))
          bimg = '/static/img/icons/map/marker-dest.png';        
        routePaths.push(new google.maps.Marker({
            position:m,
            clickable: false,
            animation: google.maps.Animation.DROP,
            icon: bimg,
            raiseOnDrag: false,
            visible: true
        }));
      }

        for (q in routePaths) {
          routePaths[q].setMap(map);
        }
    });
}