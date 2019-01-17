// Document Dot Ready
$(document).ready(function() {

    $('#patch-rom-form').on('submit', function(event){
        event.preventDefault();
        if ($('#patch-rom-btn').hasClass('disabled')) { return; }
        var formData = new FormData($(this)[0]);
        console.log(window.location.pathname);
        $.ajax({
            url: window.location.pathname,
            type: 'POST',
            data: formData,
            beforeSend: function( jqXHR ){
                $('#patch-rom-btn').addClass('disabled');
                $('#search-icon').addClass('fa-spin');
                $('#rom-status').addClass('progress-bar-striped progress-bar-animated');
            },
            complete: function(){
                $('#search-icon').removeClass('fa-spin');
                $('#rom-status').removeClass('progress-bar-striped progress-bar-animated');
                $('#patch-rom-btn').removeClass('disabled');
            },
            success: function(data, textStatus, jqXHR){
                console.log('Status: '+jqXHR.status+', Data: '+JSON.stringify(data));
                $.fileDownload(data.location);
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
