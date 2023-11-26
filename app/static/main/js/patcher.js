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
        const icon = $('#search-icon')
        const status = $('#rom-status')
        const formData = new FormData($(this)[0])
        console.log('#patch-rom-form:', formData)
        $.ajax({
            url: window.location.pathname,
            type: 'POST',
            data: formData,
            beforeSend: function (jqXHR, settings) {
                console.log('jqXHR, settings :', jqXHR, settings)
                btn.addClass('disabled')
                icon.addClass('fa-spin')
                status.addClass('progress-bar-striped progress-bar-animated')
                $('#alerts-div').empty()
            },
            complete: function (jqXHR, textStatus) {
                console.log('jqXHR, textStatus:', jqXHR, textStatus)
                icon.removeClass('fa-spin')
                status.removeClass('progress-bar-striped progress-bar-animated')
                btn.removeClass('disabled')
            },
            success: function (data, textStatus, jqXHR) {
                console.log('data, textStatus, jqXHR:', data, textStatus, jqXHR)
                if (event.originalEvent.submitter.id === 'play-rom-btn') {
                    window.location.href = `/play/${data.location}`
                } else {
                    $.fileDownload(data.location)
                    addAlert('Success! Download Starting...')
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log('jqXHR, textStatus:', jqXHR, textStatus)
                try {
                    addAlert(jqXHR.responseJSON.error.__all__[0], 'warning')
                } catch (error) {
                    console.log('error:', error)
                    addAlert(errorThrown, 'danger')
                }
            },
            cache: false,
            contentType: false,
            processData: false,
        })
    })
})

/**
 * Generate Bootstrap Alert HTML
 * @param message
 * @param {String} type
 * @return {String}
 */
function addAlert(message, type = 'success') {
    $(`#alerts-div`).html(
        `<div id="patch-alert" class="alert alert-${type} alert-dismissible fade show" role="alert">${message}` +
            '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
            '<span aria-hidden="true">&times;</span></button></div>'
    )
    $('#patch-alert')
        .fadeTo(15000, 500)
        .slideUp(500, function () {
            $('#success-alert').slideUp(500)
        })
}
