/*global $, document, d3, Rickshaw */

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


function clear_chart() {
    'use strict';
    $('#legend').empty();
    $('#chart_container').html('<div id="y_axis"></div><div id="chart"></div><div id="legend_container"><div id="smoother" title="Smoothing"></div><div id="legend"></div></div><div id="slider"></div>');
}

function plot_data_ajax(nbk_id, sensor_id) {
    'use strict';
    clear_chart();
    var url = '../ajax/get_data/' + nbk_id + '/' + sensor_id;
    var graph = new Rickshaw.Graph.Ajax({
        element: document.getElementById("chart"),
        width: 400,
        height: 250,
        renderer: 'line',
        dataURL: url,
        onData: function (d) {
            return [{name: d.name, color: 'steelblue', data: d.data}];
            //return [data];
        },
        onComplete: function () {
            var yaxis = new Rickshaw.Graph.Axis.Y({
                graph: this.graph,
                orientation: 'left',
                tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
                element: document.getElementById('y_axis'),
            });
            var hoverDetail = new Rickshaw.Graph.HoverDetail({
                graph: this.graph
            });
            var xaxis = new Rickshaw.Graph.Axis.Time({
                graph: this.graph
            });
            this.graph.render();
        }
    });
}


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