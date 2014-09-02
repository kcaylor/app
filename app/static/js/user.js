/*global $ */

var csrftoken = $('meta[name=csrf-token]').attr('content');


$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        'use strict';
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function reset_api_key(id) {
    'use strict';
    $.ajax({
        type: "GET",
        url: '../ajax/reset_api_key',
        data: "id=" + id,
        success: function (response) {
            // data is ur summary
            $('#api_key').html(response);
            $('.api_key').html(response);
        }
    });
}
