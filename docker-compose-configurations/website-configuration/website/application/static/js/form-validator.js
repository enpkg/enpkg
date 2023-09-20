// Set of functions to validate the form, first
// via client-side and then via server-side.
//
// We validate all input fields with class "validate".
// We performs some validations by default, unless a specific
// attribute is present in the input field. For instance, we
// assume that all input fields cannot be empty, unless the
// attribute "empty" is present in the input field.
// Similarly, some specific validations are performed only if
// a specific attribute is present in the input field.
//
// Since we need to provide uniform error messages both when
// validating the form via client-side and server-side, and
// we need them to be adapted to the language of the user,
// we use a method called 'get_translation' that retrieves the
// error message from the backend associated to a given label
// and user language, as defined by the 'lang' attribute of
// the html tag.
//

// The translations vocabulary.
var translations = {};

// Function that retrieves the error message from the backend
// associated to a given label and user language.
//
// label: the label of the input field
//
function get_translation(label) {
    // If the label is already present in the client-side
    // translations vocabulary, we return it.
    if (label in translations) {
        return translations[label];
    }

    // We retrieve the language from the html tag.
    var lang = $('html').attr('lang');

    // We compose the URL from the lang and the label.
    var url = '/' + lang + '/translation/' + label;

    // We retrieve the message from the backend.
    var message = $.ajax({
        url: url,
        async: false
    }).responseText;
    return message;
}

function form_is_valid(form) {
    var valid = true;
    form.find('.validate').each(function () {
        var input = $(this);
        if (!input.hasClass('valid')) {
            valid = false;
        }
    });
    return valid;
}

// Function that displayes a new error message
// under the input field.
function show_error_message(input, message_label) {
    // We retrieve the error message from the backend.
    var message = get_translation(message_label);
    // We create a new span object with class "error-message".
    var p = $('<p></p>');
    p.addClass('error-message');
    // We add an attribute "for" to the span object
    // with the name of the input field.
    p.attr('for', input.attr('name'));
    p.text(message);
    // We find the parent p containing the input field.
    var parent = input.parent('p');
    // We append the p object after the parent.
    parent.after(p);
    // We add the class "error" to the input field.
    input.addClass('error');
}

// Function that checks if the input is empty.
function check_not_empty(input) {
    // If the input has the attribute "empty", we return true.
    if (input.attr('empty') != undefined) {
        return true;
    }
    // We retrieve the value of the input field.
    var value = input.val();
    // We strip the value of the input field.
    value = value.trim();
    // If the input field is empty, we return the error message.
    if (value == '') {
        show_error_message(
            input,
            "empty_input_field"
        );
        return false;
    }
    return true;
}

function validation_callback(input){
    // We remove error messages associated
    // to the input field, as defined by p objects
    // with the class "error-message" and with
    // the attribute "for" equal to the name of the
    // input field.
    $('p.error-message[for="' + input.attr('name') + '"]').remove();
    // We remove the class "error".
    input.removeClass('error');
    input.removeClass('valid');
    // We check if the input is empty.
    if (check_not_empty(input)) {
        input.addClass('valid');
        // If the parent form is now valid, we enable the submit button.
    }
    input.parents('form').find('button[type="submit"]').prop('disabled', !form_is_valid(input.parents('form')));
}

$(document).ready(function () {
    // When the user goes out of focus of the input with
    // class "validate", we validate the input.
    $('.validate').blur(function () {
        validation_callback($(this));
    });

    // When the user has a keyup event on the input with
    // class "validate", and stops typing for 500 milliseconds,
    // we validate the input.
    $('.validate').keyup(function () {
        var input = $(this);
        // We set up a timeout to validate the input after 500 milliseconds.
        var timeout = null;
        // If there is a timeout, we clear it.
        if (timeout) {
            clearTimeout(timeout);
        }
        // We set up a new timeout.
        timeout = setTimeout(function () {
            validation_callback(input);
        }, 300);
    });


    // We iterate across all form objects and if any of them
    // contains an input field with class "validate" which does
    // not have the class "valid", we disable the submit button.
    $('form').each(function () {
        var form = $(this);
        if (!form_is_valid(form)) {
            form.find('button[type="submit"]').prop('disabled', true);
        }
    });

    // We iterate across all form objects and if any of them
    // contains an input field with class "validate" which does
    // not have the class "valid", we prevent the form from
    // being submitted.
    $('form').submit(function (event) {
        // We always stop the form from being submitted.
        event.preventDefault();
        // We check if the form is valid.
        if (!form_is_valid($(this))) {
            // If the form is not valid, we return.
            return;
        }
        // We send the form via ajax.
        var form = $(this);
        var url = form.attr('action');
        var method = form.attr('method');
        var data = form.serialize();
        $.ajax({
            url: url,
            method: method,
            data: data,
            success: function (data) {
                // We clear out the form.
                form.find('input').val('');
                form.find('textarea').val('');

                // On success, we redirect the user to the
                // page defined by the url attribute of the
                // data returned, if any.
                if (!('redirect_url' in data)) {
                    return;
                }
                
                var redirect_url = data['redirect_url'];
                window.location.replace(redirect_url); 
            },
            error: function (data) {
                // We retrieve the error messages from the backend.
                var errors = data['errors'];
                // We iterate across the error messages.
                for (var i = 0; i < errors; i++) {
                    // We retrieve the error message.
                    var error = errors[i];
                    // We retrieve the input field.
                    var input = form.find('input[name="' + error['field'] + '"]');
                    // We display the error message.
                    show_error_message(input, error['message']);
                }
            }
        });
    });
});