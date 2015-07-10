
$(function() {
    $('.hidden-on-start').hide();

    $('#add-new').click(function(e){
        e.preventDefault();
        $('header').css('width', '35%');
        $('.hidden-on-start').show();
        $('#entries').hide();
    })
});