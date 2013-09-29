if (!window.console) console = {log: function() {}};   
  
  // This only happens if you click the Facebook button
  function fbLogin() {
    FB.login( function(response) {
        console.log(response);
       if (response.authResponse) {
        createFBAcct();
        return true;
      } else {
        console.log('User cancelled login or did not fully authorize.');
        $('#formErr').html('Submission Error');
        return false;
      }
    },{scope: 'email,user_education_history,user_work_history,user_location,user_birthday'});
   }
  
  window.fbAsyncInit = function() {
    FB.init({
      appId      : '540602052657989', // App ID
      channelUrl : '//www.gobarnacle.com/static/js/channel.html', // Channel File
      status     : true, // check login status
      cookie     : true, // enable cookies to allow the server to access the session
      xfbml      : true  // parse XFBML
    });
    $(document).trigger('fbload');
    
  // Here we subscribe to the auth.authResponseChange JavaScript event. This event is fired
  // for any authentication related change, such as login, logout or session refresh. This means that
  // whenever someone who was previously logged out tries to log in again, the correct case below 
  // will be handled. 
  FB.Event.subscribe('auth.authResponseChange', function(response) {
    // Here we specify what we do with the response anytime this event occurs. 
    if (response.status === 'connected') {
      // The response object is returned with a status field that lets the app know the current
      // login status of the person. In this case, we're handling the situation where they 
      // have logged in to the app.
      console.log('Connected');
    } else if (response.status === 'not_authorized') {
      // In this case, the person is logged into Facebook, but not into the app
      console.log('Not Authorized');
    } else {
      // In this case, the person is not logged into Facebook
      console.log('Not logged in to facebook ');
    }
  });
  };

  // Load the SDK asynchronously
  (function(d){
     var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0];
     if (d.getElementById(id)) {return;}
     js = d.createElement('script'); js.id = id; js.async = true;
     js.src = "//connect.facebook.net/en_US/all.js";
     ref.parentNode.insertBefore(js, ref);
   }(document));
 
  function createFBAcct() {
      data = {};
      data.first_name = $('input#firstname').val();
      data.last_name = $('input#lastname').val();
      data.email = $('input#email').val();
      data.tel = $('input#tel').val();
      data.details = $('textarea#details').val();
      data.descr = $('textarea#descr').val();
      data.freq = $("input[name=freq]:checked").val();
      data.dist = $("input[name=dist]:checked").map(function() {
            return $(this).val();
        }).get();
    FB.api('/me?fields=first_name,last_name,id,email,education,location,work,birthday,username', function(response) {
      data.fb = response;
      djson = JSON.stringify(data);
      $.ajax({
        type: "POST",
        dataType: "json",  
        contentType: "json", 
        url: "/apply/fb",
        data: djson,
        success: function(response) {
            console.log(response);
            $('#applform').addClass('hide');
            $('#applty').removeClass('hide');   
            window.location.hash="top";
        }
    });
    });
  }
      
$.ajaxSetup ({
    cache: false
});
