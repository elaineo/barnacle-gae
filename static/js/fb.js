  // Load the SDK asynchronously
  (function(d){
     var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0];
     if (d.getElementById(id)) {return;}
     js = d.createElement('script'); js.id = id; js.async = true;
     js.src = "//connect.facebook.net/en_US/all.js";
     ref.parentNode.insertBefore(js, ref);
   }(document));

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
