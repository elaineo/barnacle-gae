function validate_username()
{
    var re = /^[A-Za-z0-9 ]{3,20}$/;
    var x = document.forms[0]["first_field"].value;
    change_validity(re.test(x))
}

function validate_zipcode()
{
    var re = /^[0-9]{5}$/;
    var x = document.forms[0]["zip"].value;
    change_validity(re.test(x))
}
function validate_rate()
{
    var re = /^(\d*\.\d{2}|\d+)$/;
    var x = document.forms[0]["rates"].value;
    change_validity(re.test(x))
}

function validate_age()
{
    var re = /^[0-9]{2,3}$/;
    var x = document.forms[0]["age"].value;
    change_validity(re.test(x))
}


function validate_clear(){
    document.forms[0].classList.remove('notvalid')
    document.forms[0].classList.remove('valid')
}

function change_validity (x){
    if (x){
        document.forms[0].classList.add('valid')
        document.forms[0].classList.remove('notvalid')
    }
    else{
        document.forms[0].classList.add('notvalid')
        document.forms[0].classList.remove('valid')
    }
}

/** click_ajax
  vtest: which fields do we need to check?
  clickver: Do they need to be logged in?
  steps: Do we need map dirs or just distance? What if we need neither?
**/
function click_ajax(btn_id, fields,inputs,vtest,form,clickver,steps) {
  var nchecks = fields.length;
  var valid = new Array(nchecks);
  $(btn_id).click(function(event) {
    //disable button until finished
    $(btn_id).attr('disabled', 'disabled');
    $(btn_id).addClass('wait');
    event.preventDefault();
    window.location.hash='';
    for (var i=0;i<nchecks;i++) {
      valid[i]=true;
    } 
    if (clickver) {
        loggedIn = checkLoginStatus();
        if (!loggedIn) {
          loginPlease();
          $(btn_id).removeAttr('disabled');
          $(btn_id).removeClass('wait');          
          return;
        }
    }
    var fajax = [];
    for (f in fields) {
      fieldLoc = $('#'+fields[f]+'Field').val();
      // do we need to test this field?
      var test = false;
      if (vtest[f].length<2) valid[f] = false; 
      else if (($(vtest[f][0]).val()!==vtest[f][1]) && 
      ( $('input#'+inputs[f]+'lat').val() == '' || $('input#'+inputs[f]+'lon').val() == '' )) 
        valid[f] = false;     
      if (!valid[f])
        fajax.push( geoFunc(fieldLoc, fields[f], inputs[f], f) );
    }
    // serialize, get path, submit
    $.when.apply($, fajax);
  });
  
  function getDirs(ff) {
    var directionsService = new google.maps.DirectionsService();
    var start = $('#'+ff[0]+'Field').val();
    /** TODO: add support for waypoints **/
    var end = $('#'+ff[ff.length-1]+'Field').val();
    var request = {
      origin:start,
      destination:end,
      travelMode: google.maps.TravelMode.DRIVING
    };
    directionsService.route(request, function(response, status) {
    if (status == google.maps.DirectionsStatus.OK) {
      // separate distance and route
      dirData = { distance: response.routes[0].legs[0].distance.value };
      if (steps) {        
        var polyline = response.routes[0].legs[0].steps; 
        var legs = [];
        for (p in polyline) {
          var segment = polyDecode(polyline[p].polyline.points, -1);
          legs.push.apply(legs,segment.filter(sparse100));
        }
        dirData.legs = legs;        
        var tempdist = dirData.distance/1609 * 100;
        dirData.precision = Math.round(5-2*Math.log(tempdist)/Math.log(100))
        /* this is a lot of data to upload */
        console.log(dirData.legs);
      }
      formData = $(form).serializeObject();
      $.extend(dirData, formData);      
    } else //else what? submit as is
      dirData = $(form).serializeObject();
    submitCallback(JSON.stringify(dirData), $(form).attr('action'));
    });
  }
  function geoFunc(locstr,o,i,f) {
    var geocoder = new google.maps.Geocoder();
    // is it blank? 
    if (locstr == '') {
        display_modal("#invalid-box");
        $(btn_id).removeAttr('disabled');
        $(btn_id).removeClass('wait');       
        return;
    }
    geocoder.geocode( { 'address': locstr, componentRestrictions: {country: 'us'}  }, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        // fill in form fields
        console.log(results);
        $('input#'+o+'Field').val(results[0].formatted_address);
        $('input#'+i+'str').val(results[0].formatted_address);
        $('input#'+i+'lat').val(results[0].geometry.location.lat());
        $('input#'+i+'lon').val(results[0].geometry.location.lng());   
        valid[f] = true;
        if (valid.every(Boolean))
          getDirs(fields);
      } else {
        console.log(status);
        $('input#'+i+'str').val('');
        $('input#'+i+'lat').val('');
        $('input#'+i+'lon').val('');
        display_modal("#invalid-box");
        $(btn_id).removeAttr('disabled');
        $(btn_id).removeClass('wait');   
        return;              
      }
    });     
  }
}

function click_validloc(btn_id,fields,inputs,vtest,form,clickver) {
    var oksubmit = true;
    var d = 0;          
    $(btn_id).click(function(event) {
      oksubmit = true; 
      event.preventDefault();
      var wait = false;
      for (f in fields) {
        var ff = fields[f];
        var test = false;
        if (vtest[f].length<2) test = true; 
        else if (($(vtest[f][0]).val()!==vtest[f][1]) && 
        ( $('input#'+inputs[f]+'lat').val() == '' || $('input#'+inputs[f]+'lon').val() == '' )) 
            test = true;
        if (test) {
            var locstr = $('#'+ff+'Field').val();
            console.log(locstr, inputs[f], ff, d);
            validate_loc(locstr, inputs[f], ff, fields, clickver);
            wait = true;
        } else { $('#'+ff+'Err').html(''); d++; }
      }
      
      if (wait==false) {
        if (clickver) {
            loggedIn = checkLoginStatus();
            if (loggedIn) $(form).submit();
            else loginPlease();
        } else $(form).submit();   
      }
    });
    
  function validate_loc(locstr, i,o,fields,clickver) {
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode( { 'address': locstr}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        // fill in form fields
        console.log(results);
        $('input#'+o+'Field').val(results[0].formatted_address);
        $('input#'+i+'str').val(results[0].formatted_address);
        $('input#'+i+'lat').val(results[0].geometry.location.lat());
        $('input#'+i+'lon').val(results[0].geometry.location.lng());   
        if (d==fields.length-1 && oksubmit) { 
            if (clickver) {
                loggedIn = checkLoginStatus();
                if (loggedIn) $(form).submit();
                else { loginPlease(); d=0; }
            } else $(form).submit();
        }
        d++;
      } else {
        $('input#'+i+'str').val('');
        $('input#'+i+'lat').val('');
        $('input#'+i+'lon').val('');
        display_modal("#invalid-box");
        oksubmit = false;                
      }
    });    
  }       
}

$.fn.serializeObject = function() {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

function polyDecode(encoded, prec) {
  // array that holds the points

  var points=[ ]
  var index = 0, len = encoded.length;
  var lat = 0, lng = 0;
  while (index < len) {
    var b, shift = 0, result = 0;
    do {
      b = encoded.charAt(index++).charCodeAt(0) - 63;  //finds ascii 
                                                    //and substract it by 63
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);
    
    var dlat = ((result & 1) != 0 ? ~(result >> 1) : (result >> 1));
    lat += dlat;
    shift = 0;
    result = 0;
    do {
      b = encoded.charAt(index++).charCodeAt(0) - 63;
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);
    var dlng = ((result & 1) != 0 ? ~(result >> 1) : (result >> 1));
    lng += dlng;
 
    /* round to 6 digits ensures that floats are same as when encoded */
    latrnd = lat / 1E5;
    lngrnd = lng / 1E5;
    if (prec >= 0) {
      latrnd = latrnd.toFixed(prec);
      lngrnd = lngrnd.toFixed(prec);
    } 
    
    points.push([latrnd,lngrnd])  
  }
  if (prec >= 0)
    return points.filter( onlyUnique );
  else
    return points;
}

function onlyUnique(value, index, self) { 
  return self.indexOf(value) === index;
}
function sparse100(value, index, self) { 
  return index % 100 === 0;
}