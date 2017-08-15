function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function modify_qstring(token){
    if (history.pushState) {
        var url = window.location.href;
        var token_pos = window.location.href.indexOf('token');
        if(token_pos >= 0) {
            url = url.substr(0, token_pos -1);
        }
        var delim = url.indexOf('?') > -1 ? '&' : '?';
        var newurl =  url + delim + 'token=' + token;
        window.history.pushState({path:newurl},'',newurl);
    }
}

function clear_qstring(){
    if (history.pushState) {
        var url = window.location.href;
        var newurl = window.location.href;
        var token_pos = window.location.href.indexOf('token');
        if(token_pos >= 0) {
            newurl = url.substr(0, token_pos -1);
        }
        window.history.pushState({path:newurl},'',newurl);
    }
}

$(function () {
    /*-- Sign-in-dropdown --*/
    $('#sign-in-dropdown').click(function () {
        //console.log('$(window).width', $(window).width());
        if( $(window).width() > 752){
            $('.sign-in-dropdown').toggle();
        }
    });

     $('.lightbox-dropdown:not(.share-dropdown) > a, .boxclose').click(function (e) {
         $(".lightbox-dropdown-form").slideToggle();
    })

      $('.share-dropdown > a').click(function (e) {
         $(".share-list").slideToggle();
    })

    $('#refine-search').click(function(){
        $('.filters_dropdown').toggle();
    });

    setTimeout(function() { $('.alert-success').slideUp() }, 2000);

    /*-- Sign-in-dropdown --*/
});
