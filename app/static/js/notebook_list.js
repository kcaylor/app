
var csrftoken = $('meta[name=csrf-token]').attr('content');

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        'use strict';
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


function delete_notebook(notebook_id) {
    'use strict';
    $.ajax({
        type: "POST",
        url: '../../ajax/notebook_delete',
        data: {'notebook_id': notebook_id},
        success: function (response) {
            // data is ur summary
            console.log('response')
            $('#' + notebook_id).remove();
        }
    });
}
