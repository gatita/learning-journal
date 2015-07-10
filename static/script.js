
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
            console.log('did this work?')
        })
    })
});