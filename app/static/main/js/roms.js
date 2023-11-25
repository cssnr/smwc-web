// Document Dot Ready
$(document).ready(function () {
    $.fn.dataTable.moment('DD MMM YYYY')

    $('#roms-table').DataTable({
        lengthMenu: [
            [10, 25, 50, 100, -1],
            [10, 25, 50, 100, 'All'],
        ],
        order: [[5, 'desc']],
        pageLength: 50,
        // "columnDefs": [
        //     { "type": "html-num-fmt", "targets": [ 3 ] }
        // ]
    })
})
