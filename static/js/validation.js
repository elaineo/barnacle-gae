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

function validate_loc(locstr, i,o) {
    var gmapURL = 'http://maps.googleapis.com/maps/api/geocode/json';
    var data = 'address='+locstr+'&sensor=false';
    var output = $.ajax({
        type: "GET",
        url: gmapURL,
        data: data
    }).pipe(function(data) {
        if (data.status=='OK') {
            // fill in form fields
            $('input#'+o+'Field').val(data.results[0].formatted_address);
            $('input#'+i+'str').val(data.results[0].formatted_address);
            $('input#'+i+'lat').val(data.results[0].geometry.location.lat);
            $('input#'+i+'lon').val(data.results[0].geometry.location.lng);
            $('#'+o+'Err').html('');
            return true;
        } else {
            $('input#'+i+'str').val('');
            $('input#'+i+'lat').val('');
            $('input#'+i+'lon').val('');
            $('#'+o+'Err').html('Invalid Location');
            return false;
        }    
    });
    return output;
}

function click_validloc(btn_id,fields,inputs,vtest,form,clickver) {
    $(btn_id).click(function(event) {
      event.preventDefault();
      var oksubmit = true;
      var wait = false;
      var d = 0;
      for (f in fields) {
        var ff = fields[f];
        var test = false;
        if (vtest[f].length<2) test = true; 
        else if (($(vtest[f][0]).val()!==vtest[f][1]) && 
        ( $('input#'+inputs[f]+'lat').val() == '' || $('input#'+inputs[f]+'lon').val() == '' )) 
            test = true;
        if (test) {
            var locstr = $('#'+ff+'Field').val();
            console.log(locstr, inputs[f], ff);
            var g = validate_loc(locstr, inputs[f], ff);
            wait = true;
            g.done(function(ok) {
                if (ok==false) oksubmit = false;
                else if (d==fields.length-1 && oksubmit) { 
                    if (clickver) {
                        loggedIn = checkLoginStatus();
                        if (loggedIn) $(form).submit();
                        else loginPlease();
                    } else $(form).submit();
                }
                d++;
            });
            g.fail(function() { 
                $('#'+ff+'Err').html('GoogleMaps is thinking...'); 
                oksubmit = false;
            });
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
}