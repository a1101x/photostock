var token = '';

$(window).load(function () {
    $(document).ready(function () {

        collage();
        // $('.Collage').collageCaption();
        $('.Collage > div').on('click', function() {
            token = $(this).find('img').data('token');
            draw_info(this);
        });
    });
});

function bindings() {
    $('.description-close').on('click', function () {
        $(this).parent().slideUp();
        clear_qstring()
    });

    $('.boxclose').on('click', function () {
        $(this).parents('.lightbox-dropdown-form').hide();
    });

    $('.light-box').on('click', function () {
        $('.lightbox-dropdown-form').show();
    });

    $('.lightboxes-list > li > a').on('click', function () {
        var lightbox = $(this).data('lightbox_id');
        var $span = $('.lightbox-dropdown > .light-box > span');
        var $a = $('.lightbox-dropdown > .light-box');
        $span.text($(this).text());
        $a.unbind('click');
        add_item_to_lightbox(lightbox, token)
    });

    $('#lightbox_btn').on('click', function () {
        var title = $('#title').val();
        $('#title').removeClass('error');
        if(!title) {
            $('#title').addClass('error');
        } else {
            create_lightbox(title, token);
        }
    })
}


function draw_info(obj){
    token = getParameterByName('token');
    if (!obj && token) {
        var $obj = $('*[data-token="'+token+'"]').parents('div');
        obj = $obj.get(0);
    } else if (!obj && !token) {
        return;
    }
    var current_direction = obj.className.match(/effect-duration-(\d+)/)[0];
    var last_in_line = $('.'+current_direction).last();
    token = $(obj).find('img').data('token');

    var template = Handlebars.compile($("#details-template").html());

    var link = "/"+current_lang+"/search/image-info/"+token;

    var current_left = ($(obj).position().left + $(obj).width() / 2) - 30;

    $.get(link, function(data) {
        modify_qstring(token);
        var $result_info = $(".result-info");
        $result_info.remove();
        last_in_line.after(template(data));
        $('.info-arrow').css('left', current_left);

        bindings();

        $('html, body').animate({
            scrollTop: last_in_line.position().top + last_in_line.height() - ($('body').height() - $(".result-info").height()) + 10
        }, 200);
    });
}

function collage() {
    $('.Collage').removeWhitespace().collagePlus(
        {
            'allowPartialLastRow': true,
            'fadeSpeed': 2000,
            'effect': 'effect-1',
            'targetHeight': 170,
            'direction': 'vertical'
        }
    );
    setTimeout(function () {
        draw_info();
    }, 200)
}

// This is just for the case that the browser window is resized
var resizeTimer = null;
$(window).bind('resize', function () {
    // hide all the images until we resize them
    $('.Collage .Image_Wrapper').css("opacity", 0);
    // set a timer to re-apply the plugin
    if (resizeTimer) clearTimeout(resizeTimer);
    resizeTimer = setTimeout(collage, 200);
});
