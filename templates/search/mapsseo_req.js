function initialize() {
  var mapOptions = {
    center: new google.maps.LatLng({{center[0]}}, {{center[1]}}),
    zoom: 4,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  var autoOptions = { componentRestrictions: {country: 'us'}  };
  var map = new google.maps.Map(document.getElementById('map-canvas'),
    mapOptions);

  var marker0 = new google.maps.Marker({
    map: map,
    draggable: true,
    visible: false
  });
    marker0.setIcon(/** @type {google.maps.Icon} */({
      url: 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=A|990099|ffffff',
      size: new google.maps.Size(71, 71),
      origin: new google.maps.Point(0, 0),
      anchor: new google.maps.Point(17, 34),
      scaledSize: new google.maps.Size(25, 35)
    }));
    
  var marker1 = new google.maps.Marker({
    map: map,
    draggable: true,
    visible: false
  });
    marker1.setIcon(/** @type {google.maps.Icon} */({
      url: 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=B|990099|ffffff',
      size: new google.maps.Size(71, 71),
      origin: new google.maps.Point(0, 0),
      anchor: new google.maps.Point(17, 34),
      scaledSize: new google.maps.Size(25, 35)
    }));  
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
        icon: 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=O|B00000|ffffff',
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
