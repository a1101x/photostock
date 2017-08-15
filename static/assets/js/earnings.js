var token = '';
var total_earn = 0;

$(function() {
    $('.profile-earning .same-block').on('click', function() {
        token = $(this).find('img').data('token');
        draw_info(this);
    });
    draw_info();

    $('#input-earn').on('input', function (){
        var value = $('#input-earn').val();
        var total = 0
        if (value > 0) {
            total = value;
        }
        if (total > 0) {
            total_earn = total;
            $("#total-earn").html(total);
        } else {
            $("#total-earn").html('0.0');
        }
    });

    $('#input-earn-bank').on('input', function (){
        var value = $('#input-earn-bank').val();
        var total = 0
        if (value > 0) {
            total = value;
        }
        if (total > 0) {
            total_earn = total;
            $("#total-earn-bank").html(total);
        } else {
            $("#total-earn-bank").html('0.0');
        }
    });

    $('#submit_btn').on('click', function () {
        $.ajax({
            type: "POST",
            url: '/' + current_lang + '/profile/withdraw/',
            data: JSON.stringify({'total_earn': total_earn}),
            contentType: 'application/json; charset=UTF-8',
            success: function(res){
                console.log(res)
            }
        })
        $('#paymentPopUp').modal('hide');
    })

    $('#submit_bank_btn').on('click', function () {
        $.ajax({
            type: "POST",
            url: '/' + current_lang + '/profile/withdraw_bank/',
            data: JSON.stringify({'total_earn': total_earn}),
            contentType: 'application/json; charset=UTF-8',
            success: function(res){
                console.log(res)
            }
        })
        $('#paymentBankPopUp').modal('hide');
    })
})

function bindings() {
    $('.description-close').on('click', function () {
        $(this).parent().slideUp();
        $(".result-info-wrapper").slideUp();
        clear_qstring()
    });
}

function draw_info(obj){
    token = getParameterByName('token');
    if (!obj && token) {
        var $obj = $('*[data-token="'+token+'"]').parents('.same-block');
        obj = $obj.get(0);
    } else if (!obj && !token) {
        return;
    }

    token = $(obj).find('img').data('token');

    var template = Handlebars.compile($("#details-template").html());

    /*
     * detect last item in current row
    * */
    var $current_item = $(obj);
    var line_index = Math.round($('.profile-earning .row').width() / $(".same-block").innerWidth());
    var current_index = $('.profile-earning .row .same-block').index($current_item) + 1;
    var rows_number = Math.round($('.profile-earning .row .same-block').length / line_index);
    var current_row = Math.ceil(current_index / line_index);
    var total_count = $('.profile-earning .row .same-block').length;
    var last_elem_index = (line_index * current_row) <= total_count  ? (line_index * current_row) : total_count;
    var current_left = ($(obj).position().left + $(obj).outerWidth()/2) + ($('.nav-tabs').is(":visible") ? ($(".container .row").position().left + $(".nav-tabs").parent().width()) : 0);
    var $last_item = $($current_item.parent().find('.same-block')[last_elem_index - 1]);


    var link = "/"+current_lang+"/search/image-info/"+token;

    $.get(link, function(data) {
        modify_qstring(token);
        var $result_info = $(".result-info");
        $(".result-info-wrapper").remove();
        $(".result-info").remove();
        var $result_info_wrapper = $("<div/>", {class: 'result-info-wrapper col-md-12 col-sm-12 col-xs-12'});
        $last_item.after($result_info_wrapper);
        data.price = $('img[data-token="'+token+'"]').data('price')
        $(".profile-earning").after(template(data));
        $('.info-arrow').css('left', current_left);

        bindings();

        $result_info.hide().slideDown();
        $('.result-info').css('top', $result_info_wrapper.position().top + 110)

        $('html, body').animate({
            scrollTop: $current_item.position().top + $current_item.height() - ($('body').height() - $(".result-info").outerHeight()) + 140
        }, 200);
    });
}
