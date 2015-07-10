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

function set_nbk_event_sensor(nbk_id, event_var, sid) {
    'use strict';
    $('#event-alert').html(
        "Okay, setting this notebook's event sensor to measure " + event_var)
    $('#event-alert').addClass('alert-info')
    $('#event-alert').removeClass('alert-warning')
    $.ajax({
        type: "GET",
        url: '../ajax/set_nbk_event_sensor',
        data: "id=" + nbk_id + "&event_sensor=" + event_var + "&sid=" + sid,
        success: function (response) {
            // data is ur summary
            $('#event-alert').addClass('alert-success')
            $('#event-alert').removeClass('alert-info')
            $('#event-alert').html(
                'Success! Your notebook is now measuring ' + event_var
            )
            $('#event-alert').fadeOut(2000, function () {
                $(this).remove();
            });
            $("#label_" + sid).html(response.variable);
            $("#data_" + sid).html(response.unit);
        },
        error: function() {
            $('#event-alert').addClass('alert-danger')
            $('#event-alert').removeClass('alert-info')
            $('#event-alert').html('Oops. We failed to set the event sensor.')
            $('#event-alert').fadeOut(500, function () {
                $(this).remove();
            });
        }
    });
}

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

$('.data-btn .btn').click( function() {
    $(this).addClass('active').siblings().removeClass('active');
  });


function clear_chart() {
    'use strict';
    $('#legend').empty();
    $('#chart_container').html('<div id="y_axis"></div><div id="chart"></div><br><div id="slider"></div>');
}

function plot_data_ajax(nbk_id, sensor_id, nbk_name, variable_name) {
    'use strict';
    $('#chart-title').html(nbk_name + ', ' + variable_name);
    clear_chart();
    var url = '../ajax/get_data/' + nbk_id + '/' + sensor_id;
    var graph = new Rickshaw.Graph.Ajax({
        element: document.getElementById("chart"),
        width: 500,
        height: 300,
        renderer: 'line',
        dataURL: url,
        onData: function (d) {
            return [{name: d.name, color: 'steelblue', data: d.data}];
            //return [data];
        },
        onComplete: function () {

            var yAxis = new Rickshaw.Graph.Axis.Y({
                graph: this.graph,
                orientation: 'left',
                tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
                element: document.getElementById('y_axis'),
            });

            var hoverDetail = new Rickshaw.Graph.HoverDetail({
                graph: this.graph,
            });

            var xAxis = new Rickshaw.Graph.Axis.Time({
                graph: this.graph,
                timeFixture: new Rickshaw.Fixtures.Time.Local()
            });

            this.graph.render();

            var slider = new Rickshaw.Graph.RangeSlider({
                graph: this.graph,
                element: document.getElementById('slider')
            });

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