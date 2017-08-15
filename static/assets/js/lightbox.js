$(function () {
    $('.lightboxes-list > li > a').unbind('click').on('click', function () {
        var lightbox = $(this).data('lightbox_id');
        var $span = $('.lightbox-dropdown > .light-box span');
        var $a = $('.lightbox-dropdown > .light-box');
        $span.text($(this).text());
        $a.unbind('click');
        add_item_to_lightbox(lightbox, token)
    });

    $('#lightbox_btn').unbind('click').on('click', function () {
        var title = $('#title').val();
        $('#title').removeClass('error');
        if(!title) {
            $('#title').addClass('error');
        } else {
            create_lightbox(title, token);
        }
    })
});

function add_item_to_lightbox(lightbox, token) {
    $.post("/"+current_lang+"/search/add-to-lightbox/",
        {'lightbox': lightbox, 'token': token},
        function (data) {
            if(data.status) {
                $('.lightbox-dropdown-form').hide();
            }
        }
    )
}

function create_lightbox(lightbox, token) {
    $.post("/"+current_lang+"/search/create-lightbox/", {'title': lightbox},
        function (data) {
            add_item_to_lightbox(data.lightBoxId, token)
            var $span = $('.lightbox-dropdown > .light-box > span');
            var $a = $('.lightbox-dropdown > .light-box');
            $span.text(data.title);
            $a.unbind('click');
        }
    )
}
