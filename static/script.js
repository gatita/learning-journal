
$(function() {
    $('.hidden-on-start').hide();

    $('#add-new').click(function(e){
        e.preventDefault();
        $('header').css('width', '35%');
        $('.hidden-on-start').show();
        $('#entries').hide();
    })

    $('.add_entry').submit(function(e) {
        e.preventDefault();

        var data = $('.add_entry').serialize();

        $.ajax({
            type: "POST",
            url: "/create",
            data: data
        }).done(function(response) {
            $('.hidden-on-start').hide();
            $('header').css('width', '45%');
            $('#entries').prepend(
                '<article class="post-listing" id=' + 
                response['id'] + '><p>' + response['created'] + 
                '</p><h2>' + response['title'] + '</h2>' +
                '<a href="entry/' + response['id'] + '">Read</a>').show();
        })
    })
});