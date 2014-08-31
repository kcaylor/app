/*global $, document */

var csrftoken = $('meta[name=csrf-token]').attr('content');
var nbk_id = $('meta[name=nbk_id]').attr('content');
var nbk_tags = $('meta[name=nbk_tags]').attr('content');
var lat = $('meta[name=lat]').attr('content');
var lng = $('meta[name=lng]').attr('content');

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        'use strict';
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$.fn.editable.defaults.mode = 'inline';

$('#notebook_name').editable({
    placement: "right",
    inputclass: "notebook_name",
    error: function (errors) {
    },
    display: function (value, response) {
        'use strict';
        //render response into element
        $(this).html(response);
    }
});


$(".tm-input").tagsManager({
    prefilled: nbk_tags,
    AjaxPush: '/edit/nbk_tags',
    AjaxPushAllTags: true,
    AjaxPushParameters: { 'nbk_id': nbk_id }
});




// var nbkData = $('#notebook-data').data();

$(document).ready(function () {
    'use strict';

    $('#forecast').load("../ajax/forecast", {'lat': lat, 'lng': lng});

    var table = $('#data_table').DataTable({
        "order": [ 1, 'asc' ],
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