// Document Dot Ready
$(document).ready(function() {

    $( "#patch-rom-btn" ).click(function() {
        $('#patch-rom-form').find('[type="submit"]').trigger('click');
    });

    $('#patch-rom-form').on('submit', function(event){
        event.preventDefault();
        if ($('#patch-rom-btn').hasClass('disabled')) { return; }
        var formData = new FormData($(this)[0]);
        $.ajax({
            url: window.location.pathname,
            type: 'POST',
            data: formData,
            beforeSend: function( jqXHR ){
                $('#patch-rom-btn').addClass('disabled');
                $('#search-icon').addClass('fa-spin');
                $('#rom-status').addClass('progress-bar-striped progress-bar-animated');
                $('#alerts-div').empty();
            },
            complete: function(){
                $('#search-icon').removeClass('fa-spin');
                $('#rom-status').removeClass('progress-bar-striped progress-bar-animated');
                $('#patch-rom-btn').removeClass('disabled');
            },
            success: function(data, textStatus, jqXHR){
                console.log('Status: '+jqXHR.status+', Data: '+JSON.stringify(data));
                $.fileDownload(data.location);
                $('#alerts-div').html(gen_alert('Success! Your download should start now...'));
            },
            error: function(data, textStatus) {
                console.log('Status: '+data.status+', Response: '+data.responseText);
                try {
                    alert(data.responseText)
                }
                catch(error){
                    console.log('Error: ' + error);
                }
            },
            cache: false,
            contentType: false,
            processData: false
        });
        return false;
    });

} );

function gen_alert(message) {
    return ('<div class="alert alert-success alert-dismissible fade show" role="alert">\n' +
        '  ' + message + '\n' +
        '  <button type="button" class="close" data-dismiss="alert" aria-label="Close">\n' +
        '    <span aria-hidden="true">&times;</span>\n' +
        '  </button>\n' +
        '</div>');
}
