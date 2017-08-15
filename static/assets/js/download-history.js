$(function() {
    $('.filter_select').styler();

    $('.filter_select').on('change', function() {
        window.location = $(this).find('option:selected').data('href');
    })

})
