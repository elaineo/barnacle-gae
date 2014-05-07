var map;
var trafficLayer;

function initialize_map(mapURL) {
    $.getJSON(mapURL, function(route){   
      console.log(route)
      var ctrLatLng = new google.maps.LatLng(route['center'][0],route['center'][1]);
      var mapOptions = {
        zoom: route['zoom'],  
        center: ctrLatLng,
        mapTypeId: google.maps.MapTypeId.TERRAIN
      };
    var markerDot = new google.maps.MarkerImage('/static/img/icons/map/dot.png',
                new google.maps.Size(10, 10),
                new google.maps.Point(0,0),
                new google.maps.Point(5, 5));    
               

    map = new google.maps.Map(document.getElementById("map-canvas"),
          mapOptions);
    map.mapTypes.set('map_style', styledMap);
    map.setMapTypeId('map_style');          
      trafficLayer = new google.maps.TrafficLayer();

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
            m = new google.maps.LatLng(p[0],p[1]);
            routePaths.push(new google.maps.Marker({
                position:m,
                clickable: false,
                icon: markerDot,
                raiseOnDrag: false,
                visible: true
            }));
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
        else 
          bimg = '/static/img/icons/map/marker-dest.png';
        routePaths.push(new google.maps.Marker({
            position:m,
            clickable: false,
            animation: google.maps.Animation.DROP,
            icon: bimg,
            raiseOnDrag: false,
            visible: true}));
      }

        for (q in routePaths) {
          routePaths[q].setMap(map);
        }
    });
}
function addTraffic() {
  trafficLayer.setMap(map);
  map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
}
function hideTraffic() {  
  trafficLayer.setMap(null);
  map.setMapTypeId(google.maps.MapTypeId.TERRAIN);
}