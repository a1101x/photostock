$(window).load(function () {
    // $('select').styler();
    $('.profile-section h4').click(function(){
        console.log('click');
        $('.left-menu').toggle();
        $('.arrow-down').toggle();
        $('.arrow-up').toggle();
    })
});