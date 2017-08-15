$(function () {
    $('.categories-tabs li a').click(function () {
        createGalleryByCategory($(this).data('tag'));
    });


    if ($(window).width() > 768) {
        $('.categories-tabs li:first-child').addClass('active');

    }else{
        $('.categories-tabs li:nth-child(2)').addClass('active');
    }
    createGalleryByCategory($('.categories-tabs:visible .active a').data('tag'));

});

function createGalleryByCategory(category) {
    var $freewall = $("#freewall");
    var $freewall_tag = $("#freewall_tag");
    var collageImageSize = $(window).width() > 992 ? 150 : 100;

    if (category != 'all') {
        var gallery = tags[category];
        $freewall_tag.html('');
        $.each(gallery.images, function (key, val) {
            var h = (1 + 3 * Math.random() << 0) * collageImageSize;
            var w = (1 + 3 * Math.random() << 0) * collageImageSize;
            $freewall_tag.append($("<a/>",{'class': 'brick', href: '/'+current_lang+'/image-details/'+val.token,
                'style':'background-image: url('+val['thumb_url']+'); width: '+w+'px; height: '+h+'px'}));
        });

        $freewall.hide();
        $freewall_tag.show();

        freewallInit('freewall_tag');
    } else {
        $freewall_tag.hide();
        $freewall.show();

        freewallInit('freewall');
    }
}

function freewallInit(id) {
    var collageImageSize = $(window).width() > 992 ? 150 : 100;

    var wall = new Freewall('#'+id);
    wall.reset({
        selector: '.brick',
        animate: false,
        cellW: collageImageSize - 10,
        cellH: collageImageSize - 10,
        delay: 30,
        gutterX: 2.5,
        gutterY: 2.5,
    });
    wall.fillHoles();
    wall.fitZone($('.layout').width(), 435);
}
