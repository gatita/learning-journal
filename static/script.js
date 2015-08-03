
$(function() {

    $('#add-new').click(function(e){
        e.preventDefault();
        $('header').css('width', '35%');
        $('.hidden-on-start').css('display', 'block');
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
            // $('.hidden-on-start').hide();
            $('header').css('width', '45%');
            $('.hidden-on-start').css('display', 'none');
            $('#entries').prepend(
                '<article class="post-listing" id=' + 
                response['id'] + '><p>' + response['created'] + 
                '</p><h2>' + response['title'] + '</h2>' +
                '<a href="entry/' + response['id'] + '">Read</a>').show();
        })
    })

    $('.save_entry').submit(function(e) {
        e.preventDefault();

        var url = $('.save_entry').attr('action')
        var data = $('.save_entry').serialize();

        $.ajax({
            type: 'POST',
            url: url,
            data: data
        }).done(function(response) {
            $('.hidden-on-start').css('display', 'none');
            $('header').css('width', '45%');
            $('#entry-title').html(response.title)
            $('#entry-body').html(response.text.markdown)
            // $('#title-label').val(response['title']);
            // $('#text').val(response['text']);
            $('#entries').show()
        })
    })
});