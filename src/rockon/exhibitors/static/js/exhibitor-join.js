$(document).ready(() => {
    $('#signup').on('change', _ => {
        $(window).bind('beforeunload', () => {
            return "Die Seite hat ungespeicherte Änderungen.";
        })
    })

    $('[name^=assetrequired_],[name^=attendance_]').on('change', event => {
        event.preventDefault()
        console.debug("toggle", event.target.dataset.id)
        const el = $(`#${event.target.dataset.toggle}${event.target.dataset.id}`)
        if (event.target.checked) {
            $(el).prop('disabled', false)
        } else {
            $(el).prop('disabled', true)
            $(el).val("")
            $(el).removeClass('is-valid is-invalid')
        }
        if (!$(':checkbox[name^=attendance_]:checked').length > 0) {
            $('#form_submit').prop('disabled', true)
        } else {
            $('#form_submit').prop('disabled', false)
        }
    })

    $('#form_reset').click((event) => {
        event.preventDefault()
        $("#signup").trigger("reset")
        $('#signup :input').val('')
        $(".not-empty").removeClass('is-valid is-invalid')
        $('[name^=assetcount_],[name^=attendancecount_]').prop('disabled', true)
        $('#form_message').html("")
    })

    $('#form_submit').on('click', (event) => {
        event.preventDefault()
        console.debug("submit")
        const form = $('#signup')
        let validated = false
        const el = form.find('.not-empty')
        console.debug("not-empty elements", el)
        for (const input of el) {
            if (!input.disabled) {
                validate_input({target: input})
                if (input.classList.contains('is-invalid')) {
                    validated = false
                    render_error_message()
                    break
                } else {
                    render_error_message()
                    validated = true
                }
            }
        }
        console.debug("validated", validated)
        const form_data = form.serializeArray()
        console.debug("form data", form_data)
        if (validated) {
            send_form(form_data)
        }
    })

    $('.not-empty').on('blur', event => {
        console.debug("not-empty handler triggered", event)
        validate_input(event)
        render_error_message()
    })
})

validate_input = (input) => {
    if (input.target.type === "checkbox") {
        console.debug("form check", input.target.id)
        if (input.target.checked) {
            inputValid(input, true)
        } else {
            inputValid(input, false)
        }
    } else if (input.target.type === "text" && input.target.disabled === false) {
        console.debug("input field", input.target.id)
        if (input.target.id === "organisation_zip") {
            if (input.target.value.length === 5 && !isNaN(input.target.value)) {
                inputValid(input, true)
            } else {
                inputValid(input, false)
            }
        } else if (input.target.value !== "") {
            inputValid(input, true)
        } else {
            inputValid(input, false)
        }
    } else if (input.target.type === "email") {
        if (input.target.id === "user_email") {
            if (validateEmail(input.target.value)) {
                inputValid(input, true)
            } else {
                inputValid(input, false)
            }
            if ($('#user_email_confirmation').val()) {
                validate_input({target: $('#user_email_confirmation')[0]})
            }
        } else if (input.target.id === "user_email_confirmation") {
            if (validateEmail(input.target.value) && input.target.value === $('#user_email').val()) {
                inputValid(input, true)
            } else {
                inputValid(input, false)
            }
        } else {
            inputValid(input, false)
        }
    } else if (input.target.type === "tel") {
        if (!isNaN(input.target.value) && input.target.value !== "") {
            inputValid(input, true)
        } else {
            inputValid(input, false)
        }
    } else if (input.target.type === "select-one") {
        if (input.target.value !== "") {
            inputValid(input, true)
        } else {
            inputValid(input, false)
        }
    } else if (input.target.type == "number") {
        if (input.target.value !== "" && !isNaN(input.target.value)) {
            inputValid(input, true)
        } else {
            inputValid(input, false)
        }
    } else {
        inputValid(input, false)
    }
}

const validateEmail = (email) => {
    return String(email)
        .toLowerCase()
        .match(
            /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
        )
}

const inputValid = (input, is_valid) => {
    if (is_valid) {
        input.target.classList.add('is-valid')
        input.target.classList.remove('is-invalid')
    } else {
        input.target.classList.add('is-invalid')
        input.target.classList.remove('is-valid')
    }
}

const render_error_message = (message) => {
    el = $('.not-empty')
    for (const input of el) {
        if (input.classList.contains('is-invalid')) {
            $('#form_message').html('<div class="alert alert-danger" role="alert">Bitte korrigiere die Fehler in den markierten Feldern.</div>')
            break
        } else {
            $('#form_message').html("")
        }
    }
}

ajax_success = (data) => {
    console.info(data)
    $(window).unbind('beforeunload')
    window.location.href = window.rockon.joinSubmitted
}
ajax_error = (data) => {
    // FIXME: needs error handling
    console.error(data)
}
ajax_complete = (data) => {
    // hopefully this is never triggered
    console.info(data)
}

const send_form = (fields) => {
    console.debug(fields)
    $.ajax({
        type: "POST",
        url: window.rockon.signup,
        data: JSON.stringify(fields),
        contentType: "application/json",
        headers: {
            "X-CSRFToken": $('[name=csrfmiddlewaretoken]').val(),
        },
        mode: "same-origin",
        dataType: "json",
        success: (data) => ajax_success(data),
        error: (data) => ajax_error(data),
        complete: (data) => ajax_complete(data)
    })
}
