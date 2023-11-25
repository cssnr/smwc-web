// Document Dot Ready
$(document).ready(function () {
    $('#patch-rom-form').on('submit', function (event) {
        event.preventDefault()
        console.log('#patch-rom-form.on.submit event:', event)
        console.log('submitter:', event.originalEvent.submitter)
        const btn = $(`#${event.originalEvent.submitter.id}`)
        if (btn.hasClass('disabled')) {
            return console.log('disabled')
        }
        const searchIcon = $('#search-icon')
        const romStatus = $('#rom-status')
        const formData = new FormData($(this)[0])
        console.log('#patch-rom-form:', formData)
        $.ajax({
            url: window.location.pathname,
            type: 'POST',
            data: formData,
            beforeSend: function (jqXHR, settings) {
                console.log('jqXHR, settings :', jqXHR, settings)
                btn.addClass('disabled')
                searchIcon.addClass('fa-spin')
                romStatus.addClass('progress-bar-striped progress-bar-animated')
                $('#alerts-div').empty()
            },
            complete: function (jqXHR, textStatus) {
                console.log('jqXHR, textStatus:', jqXHR, textStatus)
                searchIcon.removeClass('fa-spin')
                romStatus.removeClass(
                    'progress-bar-striped progress-bar-animated'
                )
                btn.removeClass('disabled')
            },
            success: function (data, textStatus, jqXHR) {
                console.log('data, textStatus, jqXHR:', data, textStatus, jqXHR)
                if (event.originalEvent.submitter.id === 'play-rom-btn') {
                    window.location.href = `/play/${data.location}`
                } else {
                    $.fileDownload(data.location)
                    const alert = gen_alert('Success! Download Starting...')
                    $('#alerts-div').html(alert)
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log('jqXHR, textStatus:', jqXHR, textStatus)
                console.log('errorThrown:', errorThrown)
                try {
                    alert(data.responseText)
                } catch (error) {
                    alert(errorThrown)
                    console.log('Error: ' + error)
                }
            },
            cache: false,
            contentType: false,
            processData: false,
        })
    })
})

function gen_alert(message) {
    return (
        '<div class="alert alert-success alert-dismissible fade show" role="alert">\n' +
        '  ' +
        message +
        '\n' +
        '  <button type="button" class="close" data-dismiss="alert" aria-label="Close">\n' +
        '    <span aria-hidden="true">&times;</span>\n' +
        '  </button>\n' +
        '</div>'
    )
}
