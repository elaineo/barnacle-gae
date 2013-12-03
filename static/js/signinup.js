if (!window.console) console = {log: function() {}}; 

$(document).ready(function(){
    $('#signupSub').click(function() {
      email = $('#su_email').val();
      okemail = validate_email($('#su_email'));
      if (!okemail) {
        $('#erroremail').html('That\'s not a valid email address');
      } else {
        $('#erroremail').html();
      }
      password = $('#su_password').val();
      verify = $('#su_verify').val();
      okpass = false;
      console.log(password.length);
      if (password.length < 4) {
        $('#errorpw').html('Password must be at least 4 characters');
      } else if (password !== verify) {
        $('#errorverify').html('Passwords must match');
      } else {
        okpass = true;
        $('#errorpw').html('');
        $('#errorverify').html('');
      }
      if (okemail && okpass) {
          data = "email="+email+"&password="+password+"&verify="+verify;
          $.ajax({
            type: "POST",
            url: "/signup",
            data: data,
            success: function(response) {
                console.log(response);
                if (response.has_error == "email") {
                    $('#erroremail').html(response.erroremail);
                } else if (response.has_error == "password") {
                    $('#errorpw').html(response.errorpw0);
                } else if (response.has_error == "verify") {
                    $('#errorverify').html(response.errorpw1);
                } else if (response.has_error == "0") {
                    closeModal();
                    refresh_head();
                    window.location.replace("/profile");
                }
                else {
                    console.log('Signup Account failed.');
                }
            }
          });
      }
    });
    $('#signinSub').click(function() {
      console.log('attempt signin')
      email = $('#si_email').val();
      okemail = validate_email($('#si_email'));
      if (!okemail) {
        $('#erroremailsi').html('That\'s not a valid email address');
      } else {
        $('#erroremailsi').html();
      }
      password = $('#si_password').val();
      if (password.length < 4) {
        $('#errorpwsi').html('That\'s not a real password');
      } else {
        okpass = true;
        $('#errorpwsi').html('');
      }
      if (okemail && okpass) {
          data = "email="+email+"&password="+password;
          $.ajax({
            type: "POST",
            url: "/signup",
            data: data,
            success: function(response) {
                console.log(response);
                if (response.has_error == "email") {
                    $('#erroremailsi').html(response.erroremail);
                } else if (response.has_error == "0") {
                    // window.location.replace(window.location.href.split('#')[0]);
                    closeModal();
                    refresh_head();
                }
                else {
                    console.log('Signin Account failed.');
                }
            }
          });
      }
    });
    
    $('form').keypress(function(e) {
        if (e.which == 13) 
            return false;
    });
});

function validate_email(input)
{
    var re = /^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$/;
    var x = input.val();
    if(re.test(x)) {
        input.addClass('valid');
        input.removeClass('notvalid');
        return true;
    } else {
        input.addClass('notvalid');
        input.removeClass('valid');
        return false;
    }
}

function refresh_head() {
  $.ajax({
    type: "GET",
    url: "/navhead",
    success: function(response) {      
        console.log(response);
        var head = '<table class="table-condensed user_head"><tr><td rowspan="2" class="th"><img src="';
        head += response.prof_thumb
        head += '" class="img-rounded" id="prof_thumb"></td><td style="text-align:left">';
        head += response.nickname + '<br>';
        head += response.account_links + '</td></tr></table>';
        $('#user_head').html(head);        
        }
  });
}
function click_redirect(btn_id,loc) {
    $(btn_id).click(function(event) {
      event.preventDefault();
      loggedIn = checkLoginStatus();
      if (loggedIn) {
        window.location.assign(loc);
      } else {
        $( 'body' ).data( "nextLoc", loc );      
        loginPlease();
      }
    });    
}
function click_submit(btn_id,form) {
    $(btn_id).click(function(event) {
      event.preventDefault();
      loggedIn = checkLoginStatus();
      if (loggedIn) {
        $(form).validate();
        $(form).submit();
      } else {
        loginPlease();
      }
    });    
}

function click_landing(btn_id,loc) {
$(btn_id).click(function(event) {
  console.log('click');
  event.preventDefault();
  loggedIn = checkLoginStatus();
  if (loggedIn) {
    window.location.assign(loc);
  } else {
    $( 'body' ).data( "nextLoc", loc );      
    loginLand();
  }
});    
}