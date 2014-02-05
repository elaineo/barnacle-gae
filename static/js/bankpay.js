var tokenizeInstrument = function(e) {
   e.preventDefault();     
   $('#acct-err').html('');
   $('#check-err').html('');
   var $form = $('#bank_form');
   var bankData = {
        name: $form.find('.acct_name').val(),
        account_number: $form.find('.acct_num').val(),
        bank_code: $form.find('.route_num').val(),
        type: $form.find("input[name=acct_type]:checked").val() 
    };
    balanced.bankAccount.create(bankData, callbackHandler);
};
$('#request_btn').click(tokenizeInstrument);   
 $('#bank_form').submit(false);
 
function callbackHandler(response) {
   switch (response.status) {
     case 201:
         // response.data.uri == URI of the bank account resource you
         // can store this card URI in your database
         console.log(response.data);
         var $form = $("#bank_form");
         var bankTokenURI = response.data['uri'];
         // append the token as a hidden field to submit to the server
         $('<input>').attr({
            type: 'hidden',
            value: bankTokenURI,
            name: 'balancedBankURI'
         }).appendTo($form);

        $('#request_btn').attr('disabled', 'disabled');  
        $('#check-err').html('Please wait...');
        $('#bank_form').css('cursor', 'wait');
        //$('#bank_form').submit();                 
        data = 'bankTokenURI='+bankTokenURI+'&bankAccountNum=' + response.data['account_number'] + '&bankName=' + response.data['bank_name'];
          $.ajax({
            type: "POST",
            url: "/settings/bank",
            data: data,
            success: function(response) {
                if (response.status == "ok") {
                    $('#bank_stuff').html('<br><h4>Account Saved.</h4>');
                } else {
                    $('#bank_stuff').html('<br><h4>Permission Denied.</h4>');
                }
            }
          });
         break;
     case 400:
         // missing field - check response.error for details
         console.log(response.error);
         $('#acct-err').html('Invalid account information.');
         break;
     case 404:
         // your marketplace URI is incorrect
         console.log(response.error);
         $('#check-err').html('Barnacle died. Please contact <a href="mailto:help@gobarnacle.com">Life Support</a>.');
         break;
     case 500:
         $('#check-err').html('Our account processor burped, please hit submit again.');
         break;
   }
}   