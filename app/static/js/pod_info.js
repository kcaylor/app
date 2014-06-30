/*global $, document */
$.fn.editable.defaults.mode = 'inline';
$('#notebook_name').editable({
    placement: "right",
    inputclass: "notebook_name",
    error: function (errors) {
    }
});

$(document).ready(function () {
    'use strict';
    var table = $('#data_table').DataTable();

    $("#data_table tfoot th").each(function (i) {
        var select = $('<select><option value=""></option></select>')
            .appendTo($(this).empty())
            .on('change', function () {
                table.column(i)
                    .search('^' + $(this).val() + '$', true, false)
                    .draw();
            });
        table.column(i).data().unique().sort().each(function (d, j) {
            select.append('<option value="' + d + '">' + d + '</option>');
        });
    });
});