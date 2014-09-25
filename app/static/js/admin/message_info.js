/*global $, document, d3, Rickshaw */

var csrftoken = $('meta[name=csrf-token]').attr('content');
var message_status = $('meta[name=message_status]').attr('content');

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        'use strict';
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


function initialize(message_id) {
    'use strict';
    $('#message').load("../../ajax/message_initialize", {'message_id': message_id});
    $('#initButton').attr('disabled', true);
    $('#parseButton').attr('disabled', false);
    $('#parseButton').addClass('btn-info');
    $('#postButton').attr('disabled', true);
    $('#deleteButton').attr('disabled', false);
    $('#status').addClass('label-info');
    $('#status').attr('content', 'initialized');
}

function parse(message_id) {
    'use strict';
    $('#message').load("../../ajax/message_parse", {'message_id': message_id});
    $('#initButton').attr('disabled', true);
    $('meta[name=message_status]').attr('content', 'parsed');
    $('#parseButton').attr('disabled', true);
    $('#postButton').attr('disabled', false);
    $('#postButton').addClass('btn-info');
    $('#status').attr('content', 'parsed');
    $('#status').addClass('label-primary');
}

function post(message_id) {
    'use strict';
    $('#message').load("../../ajax/message_post", {'message_id': message_id});
    $('#initButton').attr('disabled', true);
    $('meta[name=message_status]').attr('content', 'posted');
    $('#parseButton').attr('disabled', true);
    $('#postButton').attr('disabled', true);
    $('#status').attr('content', 'posted');
    $('#status').addClass('label-success');
}

function delete_msg(message_id) {
    'use strict';
    $('#message').load("../../ajax/message_delete", {'message_id': message_id});
    $('#initButton').attr('disabled', true);
    $('meta[name=message_status]').attr('content', 'deleted');
    $('#parseButton').attr('disabled', true);
    $('#postButton').attr('disabled', true);
    $('#status').attr('content', 'deleted');
    $('#status').addClass('label-danger');
}

