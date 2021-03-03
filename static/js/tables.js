$(document).ready(function() {
    $('#protab').DataTable({
        "order": [[ 0, "asc" ]],
        "dom": '<"top"fl>rt<"bottom"=ip><"clear">',
        stateSave: true
    });
    $('#protab').show()
});

$(document).ready(function() {
    $('#famtab').DataTable({
        "order": [[ 1, "desc" ]],
        "dom": '<"top"fl>rt<"bottom"=ip><"clear">',
        stateSave: true
    });
    $('#famtab').show()
});



$(document).ready(function() {
    $('#drugtab').DataTable({
        "order": [[ 0, "asc" ]],
        "dom": '<"top"fl>rt<"bottom"=ip><"clear">',
        stateSave: true
    });
    $('#drugtab').show()
});


$(document).ready(function() {
    $('#faminditab').DataTable({
        "order": [[ 1, "desc" ]],
        "dom": '<"top"fl>rt<"bottom"=ip><"clear">',
        stateSave: true
    });
});

$(document).ready(function() {
    $('#protinditab').DataTable({
        "order": [[ 1, "desc" ]],
        "dom": '<"top"fl>rt<"bottom"=ip><"clear">',
        stateSave: true
    });
});

$(document).ready(function() {
    $('#druginditab').DataTable({
        "order": [[ 1, "desc" ]],
        "dom": '<"top"fl>rt<"bottom"=ip><"clear">',
        stateSave: true
    });
});

$(document).ready(function() {
    $('#prodrugtab').DataTable({
        "order": [[ 1, "desc" ]],
        "dom": '<"top"fl>rt<"bottom"=ip><"clear">',
        stateSave: true
    });
});