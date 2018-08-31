(function($) {
    
    "use strict";

     
    function preloader() {
        var preloader = $('.preloader');
        preloader.delay(100).fadeOut(500);
    }

    // Navbar
    var nav = $('.main-navbar');
    
    $(window).scroll(function () {
        if ($(this).scrollTop() > 80) {
            nav.addClass("fixed-header");
        } else {
            nav.removeClass("fixed-header");
        }
    });
    
    //Search Popup
    if($('#search-item').length){
        
        //Show Popup
        $('.search-btn').on('click', function() {
            $('#search-item').addClass('search-visible');
        });
        
        //Hide Popup
        $('.search-close').on('click', function() {
            $('#search-item').removeClass('search-visible');
        });
    }


    // Slider JS Code Start

    //Function to animate slider captions 
    function doAnimations( elems ) {
        //Cache the animationend event in a variable
        var animEndEv = 'webkitAnimationEnd animationend';
        
        elems.each(function () {
            var $this = $(this),
                $animationType = $this.data('animation');
            $this.addClass($animationType).one(animEndEv, function () {
                $this.removeClass($animationType);
            });
        });
    }
    
    //Variables on page load 
    var $myCarousel = $('#carousel-example-generic'),
        $firstAnimatingElems = $myCarousel.find('.item:first').find("[data-animation ^= 'animated']");
        
    //Initialize carousel 
    $myCarousel.carousel();
    
    //Animate captions in first slide on page load 
    doAnimations($firstAnimatingElems);
    
    //Pause carousel  
    $myCarousel.carousel({
      interval: 4000
    });

    
    
    //Other slides to be animated on carousel slide event 
    $myCarousel.on('slide.bs.carousel', function (e) {
        var $animatingElems = $(e.relatedTarget).find("[data-animation ^= 'animated']");
        doAnimations($animatingElems);
    });

    // Slider JS Code End


    // Progress Ber  
    startAnimation();

    function startAnimation(){
        jQuery('.skills').each(function(){

            jQuery(this).find('.skillbar-1').animate({
              width:jQuery(this).attr('data-percent')
            },3000);

            jQuery(this).find('.skillbar-2').animate({
              width:jQuery(this).attr('data-percent')
            },3000);

            jQuery(this).find('.skillbar-3').animate({
              width:jQuery(this).attr('data-percent')
            },3000);

            jQuery(this).find('.skillbar-4').animate({
              width:jQuery(this).attr('data-percent')
            },3000); 
            
        });
    } 

     // Gallery filter 

    if($('.gallery-filter li').length){
        $('.gallery-filter li').on("click",function (event) {
            $(this).siblings('.active').removeClass('active');
            $(this).addClass('active');
            event.preventDefault();
        });
    }

    if($('.gallery-filter').length){
        $('.gallery-filter').on('click', 'a', function () {
            $('#filters button').removeClass('current');
            $(this).addClass('current');
            var filterValue = $(this).attr('data-filter');
            $(this).parents(".gallery-filter-item").next().isotope({filter: filterValue});
        });
    }

    
    // isotope | init Isotope
    if ($.fn.imagesLoaded && $(".gallery:not(.gallery-masonry)").length > 0) {
        var $container = $(".gallery:not(.gallery-masonry)");
        imagesLoaded($container, function () {
            setTimeout(function(){
                $container.isotope({
                    itemSelector: '.gallery-item',
                    layoutMode: 'fitRows',
                    filter: '*'
                });

                $(window).trigger("resize");
                // filter items on button click
            },500);

        });
    }

    
     //LightBox / Fancybox
    if($('.lightbox-image').length) {
        var lightbox_image = $('.lightbox-image');
        lightbox_image.fancybox();
    }
    
    $(window).scroll(function () {
        if ($(this).scrollTop() > 150) {
            $('.scrollup').fadeIn();
        } else {
            $('.scrollup').fadeOut();
        }
    });
    $('.scrollup').click(function () {
        $("html, body").animate({
            scrollTop: 0
        }, 1500);
        return false;
    });

    if($('.player').length) {
        $('.player').mb_YTPlayer();
    }

 

    // For Testimonal Slider
    if($('.testimonials-slider').length){
        $('.testimonials-slider').owlCarousel({
            loop:true,
            margin:0,
            dots: true,
            nav: false,
            autoplayHoverPause:false,
            autoplay: true,
            smartSpeed: 1500,
            navText: [
              '<i class="fa fa-angle-left" aria-hidden="true"></i>',
              '<i class="fa fa-angle-right" aria-hidden="true"></i>'
            ],
            responsive: {
                0: {
                    items: 1,
                    center: false
                },
                480:{
                    items:1,
                    center: false
                },
                600: {
                    items: 1,
                    center: false
                },
                768: {
                    items: 3
                },
                992: {
                    items: 3
                },
                1200: {
                    items: 3
                }
            }
        })
    }

    // For Testimonal Slider
    if($('.about-carousel-one').length){
        $('.about-carousel-one').owlCarousel({
            loop:true,
            margin:0,
            dots: false,
            nav: false,
            autoplayHoverPause:false,
            autoplay: true,
            smartSpeed: 1500,
            navText: [
              '<i class="fa fa-angle-left" aria-hidden="true"></i>',
              '<i class="fa fa-angle-right" aria-hidden="true"></i>'
            ],
            responsive: {
                0: {
                    items: 1,
                    center: false
                },
                480:{
                    items:1,
                    center: false
                },
                600: {
                    items: 1,
                    center: false
                },
                768: {
                    items: 1
                },
                992: {
                    items: 1
                },
                1200: {
                    items: 1
                }
            }
        })
    }

    // Counter jQuery
    if($('.count01').length){
        var count01 = $(".count01");
        count01.jQuerySimpleCounter({
            end: 8766,
            duration: 15000,
        });
    }

    if($('.count02').length){
        var count02 = $(".count02");
        count02.jQuerySimpleCounter({
            end: 2751,
            duration: 16000
        });
    }

    if($('.count03').length){
        var count03 = $(".count03");
        count03.jQuerySimpleCounter({
            end: 6581,
            duration: 17000,
        });
    }

    if($('.count04').length){
        var count04 = $(".count04");
        count04.jQuerySimpleCounter({
            end: 4690,
            duration: 17000,
        });
    }


/* ==========================================================================
   When document is loading, do
   ========================================================================== */

    $(window).on('load', function() {
        // add your functions
        preloader();
    });

})(window.jQuery);
