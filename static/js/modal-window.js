function add_confirmation_dialog(action, button){
    $('#'+button).click(function(event){
        event.preventDefault();
        delete_form = '<form method="post" action="' + action + '"><br><button type="submit" class="button small info">Yes</button>&nbsp;<button id="cancel" type="button" class="button small info">Cancel</button></form>';
        $('body').append('<div id="confirm" class="modal fade in" style="display: none; "><div class="modal-body"><h4>Are you sure?</h4><p>This action cannot be undone.</p>' + delete_form + '</div></div>');
        
        $('#confirm').modal();
        $('#cancel').on('click', function(){
          $('#confirm').modal('hide');
        });
    });
}

function display_modal(loginBox) {
  $(loginBox).modal();
}
function display_modal_msg(msg) {
  $('h4#modal-msg').html(msg);
  $('#modal-box').modal();
}


$(document).ready(function() {
	// When clicking on the button close or the mask layer the popup closed
	$('a.close, #mask').on('click', function() { 
        closeModal();
        return false;
	});
    
    /* Allow modal window to be accessed using # tags */
  $(window).load(function () {
	if(window.location.hash) {
	  var loginBox = window.location.hash;
      display_modal(loginBox);      
	}			 
  });
});

/* Modal functions. Might need to call from elsewhere. */
function closeModal() {
    $('#signin-box').modal('hide');
}