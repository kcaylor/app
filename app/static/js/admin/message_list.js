/*global $, document, d3, Rickshaw */

var csrftoken = $('meta[name=csrf-token]').attr('content');
var count = $('meta[name=message=count]').attr('content');

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        'use strict';
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

var table = $('#data_table').DataTable({
        "order": [ 1, 'asc' ],
        "processing": true,
        "serverSide": true,
        "ajax": "ajax/get_messages",
        "post": true,
        "deferLoading": count
        // "data": nbkData.json,
        // "columns": [
        //     { "title" : "Date"},
        //     { "title" : "Sensor", "class": "center"},
        //     { "title" : "Value", "class": "center"}
        // ]
    });

$(document).ready(function () {
    'use strict';
    var table = $('#data_table').DataTable({
        "order": [ 1, 'asc' ],
        "processing": true,
        "serverSide": true,
        "ajax": "ajax/get_messages",
        "post": true,
        "deferLoading": count,
        "columns": [
            { "items": "Date"},
            { "items": "Time"}
        ]
        // "data": nbkData.json,
        // "columns": [
        //     { "title" : "Date"},
        //     { "title" : "Sensor", "class": "center"},
        //     { "title" : "Value", "class": "center"}
        // ]
    });
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
