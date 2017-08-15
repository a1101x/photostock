$(function () {
    new autoComplete({
        selector: '#keyword',
        minChars: 2,
        source: function(term, response){
            $.getJSON("/"+ current_lang +"/autocomplete/"+term, function(data){
                response(data); });
        },
        onSelect: function(e, term){
            var author = getParameterByName('author');
            var link = "/"+ current_lang +"/search/?keyword="+ term + (author != null ? '&author=' + author : '');
            window.location = link;
        }
    });
});
