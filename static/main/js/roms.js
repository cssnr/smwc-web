// Document Dot Ready
$(document).ready(function() {
    $('#roms-table').DataTable( {
        "lengthMenu": [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
        "order": [[ 6, "desc" ]],
        "pageLength": 50
    } );
} );
