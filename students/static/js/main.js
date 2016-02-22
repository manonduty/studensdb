function initJournal() {
    var indicator = $('#ajax-progress-indicator');

    $('.day-box input[type="checkbox"]').click(function(event){
        var box = $(this);
        $.ajax(box.data('url'), {
            'type': 'POST',
            'async': true,
            'dataType': 'json',
            'data': {
                'pk': box.data('student-id'),
                'date': box.data('date'),
                'present': box.is(':checked') ? '1': '',
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            'beforeSend': function(xhr, settings){
                indicator.show();
            },
            'error': function(xhr, status, error){
                $('#ajax-error').show();
                $('#ajax-error-text').text("ERROR: Data not saved. " + error);
                indicator.hide();
            },
            'success': function(data, status, xhr){
                indicator.hide();
            }
        });
    });
}

function initGroupSelector(){
    // look up select element with groups and attach our even handler
    // on field "change" event
    $('#group-selector select').change(function(event){
        var group = $(this).val();

        if (group) {
            // set cookie with expiration date 1 year since now;
            // cookie creation function takes period in days
            $.cookie('current_group', group, {'path': '/', 'expires': 365});
        } else {
            // otherwise we delete the cookie
            $.removeCookie('current_group', {'path': '/'});
        }

        // and reload a page
        // location.reload(true);
        location = '/' + location.pathname.split('/')[1];

        return true;
    });
}

function initDateFields() {
    $('input.dateinput').datetimepicker({
        format: 'YYYY-MM-DD',
        locale: 'uk'
    }).on('dp.hide', function(event){
        $(this).blur();
    });
    var datefield = $('#div_id_birthday div');
    datefield.find('input').attr('aria-describedby', 'calendar-icon');
    datefield.append('<span class="input-group-addon">'
            + '<i class="glyphicon glyphicon-calendar"'
            + 'id="calendar-addon" aria-hidden="true"></i></span>');
    datefield.wrapInner('<div class="input-group"> </div>');
}

function renewStudentsList(data, student_id) {
    $('table #'+student_id).html($(data).find('table #'+student_id).html());
}

function initEditStudentForm(form, modal) {
    // attache datepicker
    initDateFields();

    // close modal window on Cancel button click
    form.find('input[name="cancel_button"]').click(function(event){
        modal.modal('hide');
        return false;
    });

    // make form work in AJAX mode
    form.ajaxForm({
        'dataType': 'html',
        'error': function(){
            //alert('Помилка на сервері. Спробуйте будь-ласка пізніше. form.ajaxForm()');
            $('#modal-message-block').show();
            $('#modal-message').html('<b>Error:</b> Помилка на сервері. Спробуйте будь-ласка пізніше.');
            return false;
        },
        'success': function(data, status, xhr) {
            var html = $(data), newform = html.find('#content-column form.form-horizontal');

            // copy alert to modal window
            modal.find('.modal-body').html(html.find('.alert'));

            // copy form to modal if we found it in server response
            if (newform.length > 0) {
                modal.find('.modal-body').append(newform);

                // initialize form fields and buttons
                initEditStudentForm(newform, modal);
            } else {
                // if no form, it means success and we need to reload page
                // to get updated student list;
                // reload after 2 seconds, so that user can read
                // success message
                //setTimeout(function(){location.reload(true);}, 500);
                student_id = $(form).attr('action').split('/')[2];
                $('table #'+student_id).html(
                    $(data).find('table #'+student_id).html()
                );
            }
        },
        'beforeSend': function() {
            $('.ajax-loader-modal img').show();
            $('input, select, textarea, a, button').attr('disabled', 'disabled');
        },
        'complete': function() {
            $('.ajax-loader-modal img').hide();
            $('input, select, textarea, a, button').removeAttr('disabled', 'disabled');
        }
    });
}

function initEditStudentPage() {
    $('a.student-edit-form-link').click(function(event){
        // dvk: find all anchors with a class .student-edit-form-link
        var studentEditAnchors = $('a.student-edit-form-link');
        $('a').click(function (event) {
            event.preventDefault();
        });
        
        var link = $(this);
        $.ajax({
            'url': link.attr('href'),
            'dataType': 'html',
            'type': 'get',
            'success': function(data, status, xhr){
                // check if we got successfull response from the server
                if (status != 'success') {
                    alert('Помилка на сервері. Спробуйте будь-ласка пізніше. initEditStudentPage() status != "success" ');
                    return false;
                }

                // update modal window with arrived content from the server
                var modal = $('#myModal');
                html = $(data), form = html.find('#content-column form');
                modal.find('.modal-title').html(html.find('#content-column h2').text());
                modal.find('.modal-body').html(form);

                // init our edit form
                initEditStudentForm(form, modal);

                // setup and show modal window finally
                modal.modal({
                    'keyboard': false,
                    'backdrop': false,
                    'show': true
                });
            },
            'error': function(){
                alert('Помилка на сервері. Спробуйте будь-ласка пізніше. initEditStudentPage() error');
                return false;
            },
            'beforeSend': function () {
                $('.ajax-loader').show();
            },
            'complete': function () {
                $('.ajax-loader').hide();
            }
        });

        return false;
    });
}


$(document).ready(function(){
    initJournal();
    initGroupSelector();
    initDateFields();
    initEditStudentPage();
}
);
