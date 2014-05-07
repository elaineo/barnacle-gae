$(document).ready(function(){
	$(".card-number").keyup(function()
	{
		var cc = $(this).val();
		if (cc.length >= 1) {
			var which;

			if ((/^(34|37)/).test(cc)) {
				which = '.cc_amex';
			} else if ((/^(51|52|53|54|55)/).test(cc)) {
				which = '.cc_mastercard';
			} else if ((/^(4)/).test(cc)) {
				which = '.cc_visa';
			} else if ((/^(300|301|302|303|304|305|36|38)/).test(cc)) {
				which = '.cc_diners';
			} else if ((/^(6011)/).test(cc)) {
				which = '.cc_discover';
			} else if ((/^(3)/).test(cc) && cc.length >= 2) {
				which = '.cc_jcb';
			} else if ((/^(2131|1800)/).test(cc)) {
				which = '.cc_jcb';
			}

			$('.cc').removeClass('cc_initial');
			$('.cc').removeClass('cc_selected');
			$('.cc').addClass('cc_deselected');
			if (which) {
				$(which).removeClass('cc_deselected');
				$(which).addClass('cc_selected');

				if (which == '.cc_amex') {
					$('#cvc_card').addClass('amex_front');
					$('#cvc_card').removeClass('visa_back');                    
				} else {
					$('#cvc_card').removeClass('amex_front');
                    $('#cvc_card').addClass('visa_back');
				}
			}
		} else {
			$('.cc').removeClass('cc_deselected');
			$('.cc').removeClass('cc_selected');
			$('.cc').addClass('cc_initial');
			$('#cvc_card').removeClass('amex_front');
            $('#cvc_card').addClass('visa_back');
		}
	});
    });
    
    
   var tokenizeInstrument = function(e) {
       e.preventDefault();     
        $('#cc_form').validate();             
       $('#cc-err').html('');
       $('#check-err').html('');
        $('#request_btn').attr('disabled', 'disabled');  
        $('#request_btn').addClass('wait');  
        $('#check-err').html('Please wait...');      
       var $form = $('#cc_form');
       var creditCardData = {
            card_number: $form.find('.card-number').val(),
            expiration_month: $form.find('.cc-em').val(),
            expiration_year: '20'+$form.find('.cc-ey').val(),
            security_code: $form.find('.cc-csc').val()
        };
        if($('#cc_form').valid() == true)
          balanced.card.create(creditCardData, callbackHandler);
        else {
          $('#request_btn').removeAttr('disabled');
          $('#request_btn').removeClass('wait');
          $('#check-err').html('');
        }
    };
   $('#request_btn').click(tokenizeInstrument);    
function callbackHandler(response) {
   switch (response.status) {
     case 201:
         // response.data.uri == URI of the bank account resource you
         // can store this card URI in your database
         console.log(response.data);
         var $form = $("#cc_form");
         var cardTokenURI = response.data['uri'];
         var last4 = response.data['last_four'];
         // append the token as a hidden field to submit to the server
         $('<input>').attr({
            type: 'hidden',
            value: cardTokenURI,
            name: 'balancedCreditCardURI'
         }).appendTo($form);
         $('<input>').attr({
            type: 'hidden',
            value: last4,
            name: 'last4'
         }).appendTo($form);
         
        $('#cc_form').submit();                 
         break;
     case 400:
         // missing field - check response.error for details
         console.log(response.error);
         $('#cc-err').html('Invalid card information.');
         break;
     case 402:
         // we couldn't authorize the buyer's credit card
         // check response.error for details
         $('#cc-err').html('Card Declined.');
         console.log(response.error);
         break
     case 404:
         // your marketplace URI is incorrect
         console.log(response.error);
         $('#check-err').html('Barnacle died. Please contact <a href="mailto:help@gobarnacle.com">Life Support</a>.');
         break;
     case 500:
         $('#check-err').html('Our card reader burped, please hit checkout again.');
         break;
   }
   $('#request_btn').removeAttr('disabled');
   $('#request_btn').removeClass('wait');
   $('#check-err').html('');
}   