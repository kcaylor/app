/*global $, document, d3, Rickshaw */

var csrftoken = $('meta[name=csrf-token]').attr('content');

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        'use strict';
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function test_gateway(gateways) {
    'use strict';
    var obj = JSON.parse(gateways);
    var arrayLength = obj.length;
    for (var i = 0; i < arrayLength; i++) {
        console.log("gateway: "+obj[i].number);
        if ($(".bootstrap-switch-id-"+obj[i]._id+"Toggle").hasClass(
        "bootstrap-switch-on")) {
            console.log("testing the "+obj[i]._id+" gateway");
            $.ajax({
                type: "POST",
                url: '../ajax/gateway_test',
                data: "country=" + obj[i].country + "&number=" + obj[i].number,
                success: function (response) {
                     // data is ur summary
                     console.log(JSON.stringify(response));
                },
                error: function(e) {
                     console.log(e.message);
                }
            });
        }
    }
}

$(document).ready(function () {
    'use strict';
     $(".my-toggle-checkbox").bootstrapSwitch();
 });