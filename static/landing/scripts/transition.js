

// DEFAULTS FORM FOUNDATION FRAMEWORK, GENERALY YOU DON'T NEED TO EDIT THIS

;(function ($, window, undefined) {
  'use strict';

  var $doc = $(document),
      Modernizr = window.Modernizr;

  $(document).ready(function() {
    $.fn.foundationAlerts           ? $doc.foundationAlerts() : null;
    $.fn.foundationButtons          ? $doc.foundationButtons() : null;
    $.fn.foundationAccordion        ? $doc.foundationAccordion() : null;
    $.fn.foundationNavigation       ? $doc.foundationNavigation() : null;
    $.fn.foundationTopBar           ? $doc.foundationTopBar() : null;
    $.fn.foundationCustomForms      ? $doc.foundationCustomForms() : null;
    $.fn.foundationMediaQueryViewer ? $doc.foundationMediaQueryViewer() : null;
    $.fn.foundationTabs             ? $doc.foundationTabs({callback : $.foundation.customForms.appendCustomMarkup}) : null;
    $.fn.foundationTooltips         ? $doc.foundationTooltips() : null;
    //$.fn.foundationMagellan         ? $doc.foundationMagellan() : null;
    $.fn.foundationClearing         ? $doc.foundationClearing() : null;

    $.fn.placeholder                ? $('input, textarea').placeholder() : null;
  });

  // UNCOMMENT THE LINE YOU WANT BELOW IF YOU WANT IE8 SUPPORT AND ARE USING .block-grids
  // $('.block-grid.two-up>li:nth-child(2n+1)').css({clear: 'both'});
  // $('.block-grid.three-up>li:nth-child(3n+1)').css({clear: 'both'});
  // $('.block-grid.four-up>li:nth-child(4n+1)').css({clear: 'both'});
  // $('.block-grid.five-up>li:nth-child(5n+1)').css({clear: 'both'});

  // Hide address bar on mobile devices (except if #hash present, so we don't mess up deep linking).
  if (Modernizr.touch && !window.location.hash) {
    $(window).load(function () {
      setTimeout(function () {
        window.scrollTo(0, 1);
      }, 0);
    });
  }

})(jQuery, this);





// EDIT BELOW THIS LINE FOR CUSTOM EFFECTS, TWEACKS AND INITS

/*--------------------------------------------------

Custom overwiev:

1.  Mobile specific			
2.  CarouFredSel - Responsive Carousel
3.  Titles - Loading slow effect
4.  Fit text - Resize big titles on small device platform
5.  Video - Show/hide promo video
6.  PrettyPhoto
7.  Mailchimp integration
8.  Button - Go Up
9.  Circular Match Bar
10. Accordion
11. Toggle Message Form
12. Foundation Orbit - Profile Sliders
13.	Foundation Orbit - Blog Sliders
14.	Cross-browser tweacks ;)
	
---------------------------------------------------*/


//You should bind all actions in document.ready, because you should wait till the document is fully loaded.
$(document).ready(function(){
	ifisMobile();
	hyperlinkPhone();
	goupPage();
		
});





/***************************************************
1. Mobile specific
***************************************************/
function ifisMobile(){
	if (
		(navigator.userAgent.indexOf('iPhone') != -1) || (navigator.userAgent.indexOf('iPod') != -1) ||
		((navigator.userAgent.indexOf('Android') != -1) && (navigator.userAgent.indexOf('Mobile') != -1))
	)
		{
			//Hide quote you don't need
			$('.hide-on-mobile').hide();
		}
}

//Hyperlink your phone numbers
function hyperlinkPhone(){
	 $("a[href^='tel:']").click(function(){
	 	if( !$("body").hasClass("mobile") )  return false;
  });
}





/***************************************************
3. Titles - Loading slow effect
***************************************************/
function loadingSlow(){
	jQuery('#call-to-actions .section-title').animate({opacity:1},1200,function(){ jQuery('#call-to-actions .lead').animate({opacity:1},1500);});
}







/***************************************************
8. Button - Go Up
***************************************************/
function goupPage(){
	// hide #btnGoUp first
	$("#btnGoUp").hide();
	
	// fade in #btnGoUp
	$(function () {
		$(window).scroll(function () {
			if ($(this).scrollTop() > 100) {
				$('#btnGoUp').fadeIn();
			} else {
				$('#btnGoUp').fadeOut();
			}
		});
	
		// scroll body to 0px on click
		$('#btnGoUp').click(function () {
			$('body,html').animate({
				scrollTop: 0
			}, 800);
			return false;
		});
	});
}
