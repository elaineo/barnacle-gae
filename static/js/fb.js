  // This only happens if you click the Facebook button
  function fbLogin() {
    FB.login( function(response) {
        console.log(response);
       if (response.authResponse) {
        createFBAcct();
        return true;
      } else {
        console.log('User cancelled login or did not fully authorize.');
        return false;
      }
    },{scope: 'email,user_location'});
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
    console.log('Welcome!  Fetching your information.... ');
    FB.api('/me?fields=first_name,last_name,email,id,username', function(response) {
      console.log(response);
      //var data = "first_name="+response.first_name+"&last_name="+response.last_name+"&id="+response.id;
      $.ajax({
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        url: "/signup/fb",
        data: JSON.stringify(response),
        success: function(response) {
            // if (response.status == "new" || response.status == "existing") {
                // closeModal();
                // refresh_head();
                // return true;
            if (response.status == "new") {
                // window.location.replace("/splash");
                closeModal();
                var nextLoc = $( 'body' ).data( "nextLoc");
                if (typeof nextLoc != 'undefined')
                    window.location.replace(nextLoc);
                refresh_head();
                // window.location.replace("/profile");
            } else if (response.status == "existing") {
                // window.location.replace(window.location.href.split('#')[0]);
                closeModal();
                var nextLoc = $( 'body' ).data( "nextLoc");
                if (typeof nextLoc != 'undefined')
                    window.location.replace(nextLoc);
                refresh_head();
            }
            else {
                console.log('FB Account failed.');
                return false
            }
        }
    });
    });
  }

  function dumpFriends(fb_id, dumpsite, max) {
    if (fb_id=='')
        return;
    FB.api('/me/mutualfriends/'+fb_id, function(response) {
      console.log(response);
      var friends = response.data;
      var fdump='';
      var numfriends = response.data.length;
      if (numfriends == 0) {$(dumpsite).html('None');}
      else {
          if (numfriends > max) {
            friends = friends.slice(0,max);
            var plusStr = '<span class="friendsplus"> +'+(numfriends-max).toString() + '</span>'; }
          else {var plusStr = '';}
          var fajax = [];
          for (f in friends) {
            fajax.push( $.ajax({
              type: 'GET',
              url: 'http://graph.facebook.com/'+friends[f].id+'/picture?redirect=false',
              contName: friends[f].name,
              success:  function(data) {
                var imgurl = data.data.url;
                fdump += '<img src="'+imgurl+'" title="'+this.contName+'">&nbsp; '; }
              }) );
          }
          $.when.apply($, fajax).then(function() { $(dumpsite).html(fdump+plusStr);});
      }
    });
  }

  function dumpThumb(fb_id, dumpsite) {
    if (fb_id=='')
        return;
    FB.api('/'+fb_id, function(response) {
      console.log(response);
      var first_name = response.first_name;
      $(dumpsite).html(response.first_name);
      var fajax = [];
      var dumpcont = '';
      fajax.push( $.ajax({
        type: 'GET',
        url: 'http://graph.facebook.com/'+fb_id+'/picture?redirect=false',
        contName: first_name,
        success:  function(data) {
          var imgurl = data.data.url;
          dumpcont = '<img height="50px" src="'+imgurl+'"><br>'+first_name;
        }
      }) );
      $.when.apply($, fajax).then(function() { $(dumpsite).html(dumpcont);});
    });
  }

  function dumpResponse(fb_id) {
    if (fb_id=='')
        return;
    FB.api('/'+fb_id, function(response) {
      console.log(response);
      var first_name = response.first_name;
      var fajax = [];
      var dumpcont = '';
      fajax.push( $.ajax({
        type: 'GET',
        url: 'http://graph.facebook.com/'+fb_id+'/picture?redirect=false',
        contName: first_name,
        success:  function(data) {
          var imgurl = data.data.url;
          dumpcont = {img: imgurl, first_name: first_name};
          console.log(dumpcont);
          FBResponseHandler(dumpcont);
        }
      }) );
      $.when.apply($, fajax).then(function() { FBResponseHandler(dumpcont);});
    });
  }

$.ajaxSetup ({
    cache: false
});

$(document).ready(function(){
  $('.fblogin').click(function() {
    fbLogin();
  });
  $('#signoutFB').click(function() {
    // check if we have a fb cookie
    var acct = getCookie("account");
    if (acct == "fb") {
        FB.logout(function(response) {
            console.log('Logged out of FB');
        });
    }
  });

});

function click_facebook(btn_id,loc) {
    $(btn_id).click(function() {
        window.open(loc, '', 'width=800,height=500,scrollbars=no,location=no');
    });
}
