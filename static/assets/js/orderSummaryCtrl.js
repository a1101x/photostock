$(window).load(function () {
    $('select').styler();
    var reneval = true;
    $('#switch-reneval').click(function (e) {
        if (reneval) {
            $('#switch').text('YES');
            $('#autorenew').val(true);
        } else {
            $('#switch').text('NO');
            $('#autorenew').val(false);
        }
        reneval = !reneval
    })
    $('#show_hide_vat, #show_hide_coupon').on('click', function() {
        var $td = $(this).parents('td');
        $td.addClass('align-left-forms');
        $td.find('.show-hide-el').hide();
        $td.find('.hidden-form').show();
    })

    $('#form_vat, #form_coupon').on('submit', function() {
        var inp_val = $(this).parent().find('input[type="text"]').val();
        var $td = $(this).parents('td');
        if(inp_val){
            $td.find('.show-hide-el span').text(inp_val);
            $td.find('.show-hide-el a').text('change');
        }
        $td.find('.hidden-form').hide()
        $td.find('.show-hide-el').show()
        return false;
    })
    $('#form_coupon input[type="text"]').on('keyup', function() {
        $('#coupon').val($(this).val());
    })
    $('#form_vat input[type="text"]').on('keyup', function() {
        $('#vat').val($(this).val());
    })

    //$(".btn-primary").on('click', function(e) {
        //var link = '/' + current_lang + '/order/get-link/?' + $(this).serialize();
        //$.post(link, function(data) {
            //if (data.status == true) {
                //var childWindow = window.open(data.value, 'buy')
                ////console.log(childWindow.location);
                //checkStatus(childWindow.location.href);
            //} else {
                //console.log(data);
            //}
        //})
        ////console.log($(this).serialize());
        //return false;

    //})
});
