/* Modal functions. Might need to call from elsewhere. */
function closeModal() {
    $('#signin-box').trigger('reveal:close');
}
function display_modal(loginBox) {
  $( loginBox ).reveal( $( loginBox ).data() );
}
