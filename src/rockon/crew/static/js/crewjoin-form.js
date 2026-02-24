console.debug('crew-signupform.js loaded')

$(document).ready(() => {
    $('#signup').on('change', _ => {
        $(window).bind('beforeunload', () => {
            return 'Die Seite hat ungespeicherte Änderungen.'
        })
    })

    $('#select_all_attendance').change(event => {
        event.preventDefault()
        for (const el of $('[name^=attendance_]')) {
            el.checked = event.target.checked
            el.value = event.target.checked ? 'on' : ''
        }
    })

    $('[name^=attendance_]').on('change', event => {
        event.preventDefault()
        if (!event.target.checked) {
            $('#select_all_attendance').prop('checked', false)
        }
    })

    $('#form_reset').click(event => {
        event.preventDefault()
        if (confirm('Möchtest du das Formular zurücksetzen?')) {
            $('#signup').trigger('reset')
            $('#signup :input').val('')
            $('.not-empty').removeClass('is-valid is-invalid')
            $('#leave_of_absence_note').prop('disabled', true)
            $('#form_message').html('')
        }
    })

    $('#form_submit').on('click', event => {
        event.preventDefault()
        console.debug('submit')
        const form = $('#signup')
        let validated = false;
        const el = form.find('.not-empty')
        console.debug('not-empty elements', el)
        for (const input of el) {
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
        console.debug('validated', validated)

        if (validated) {
            const data = {}
            // Scalar fields
            data.crew_shirt = parseInt($('[name=crew_shirt]').val())
            data.nutrition_type = $('[name=nutriton_type]').val() || ''
            data.nutrition_note = $('[name=nutrition_note]').val() || ''
            data.skills_note = $('[name=skills_note]').val() || ''
            data.attendance_note = $('[name=note_attendance]').val() || ''
            data.stays_overnight = $('[name=stays_overnight]').is(':checked')
            data.general_note = $('[name=general_note]').val() || ''
            data.needs_leave_of_absence = $('[name=leave_of_absence]').is(':checked')
            data.leave_of_absence_note = $('[name=leave_of_absence_note]').val() || ''

            // Collect checked checkbox IDs into typed arrays
            data.skill_ids = []
            $('[name^=skill_]:checked').each(function () {
                data.skill_ids.push(parseInt(this.name.split('_')[1]))
            })
            data.attendance_ids = []
            $('[name^=attendance_]:checked').each(function () {
                data.attendance_ids.push(parseInt(this.name.split('_')[1]))
            })
            data.teamcategory_ids = []
            $('[name^=teamcategory_]:checked').each(function () {
                data.teamcategory_ids.push(parseInt(this.name.split('_')[1]))
            })
            data.team_ids = []
            $('[name^=team_]:checked').each(function () {
                data.team_ids.push(parseInt(this.name.split('_')[1]))
            })

            console.debug('form data', data)
            send_form(data)
        }
    })

    $('.not-empty').on('blur', event => {
        console.debug('not-empty handler triggered', event)
        validate_input(event)
        render_error_message()
    })

    $('#leave_of_absence').on('change', event => {
        event.preventDefault()
        if (event.target.checked) {
            $('#leave_of_absence_note').prop('disabled', false)
        } else {
            $('#leave_of_absence_note').val('')
            $('#leave_of_absence_note').prop('disabled', true)
        }
    })

    const toggleTeamCard = input => {
        const team = input.dataset.teamcategory
        if (input.checked) {
            $('.card[data-teamcategory="' + team + '"]').addClass('bg-primary')
        } else {
            $('.card[data-teamcategory="' + team + '"]').removeClass('bg-primary')
        }
    }

    $('input[data-teamcategory]')
        .each((_, input) => {
            toggleTeamCard(input)
        })
        .on('change', event => {
            toggleTeamCard(event.target)
        })
})

validate_input = input => {
    if (input.target.type === 'checkbox') {
        console.debug('form check', input.target.id)
        if (input.target.checked) {
            inputValid(input, true)
        } else {
            inputValid(input, false)
        }
    } else if (input.target.type === 'text') {
        console.debug('input field', input.target.id)
        if (input.target.value !== '') {
            inputValid(input, true)
        } else {
            inputValid(input, false)
        }
    } else if (input.target.type === 'select-one') {
        if (input.target.value !== '') {
            inputValid(input, true)
        } else {
            inputValid(input, false)
        }
    }
}

const validateEmail = email => {
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

const render_error_message = message => {
    el = $('.not-empty')
    for (const input of el) {
        if (input.classList.contains('is-invalid')) {
            $('#form_message').html(
                '<div class="alert alert-danger" role="alert">Bitte korrigiere die Fehler in den markierten Feldern.</div>'
            )
            break
        } else {
            $('#form_message').html('')
        }
    }
}

ajax_success = data => {
    console.info(data)
    $(window).unbind('beforeunload')
    window.location.href = window.rockon_data.success_redirect
}
ajax_error = data => {
    // FIXME: needs error handling
    console.error(data)
}
ajax_complete = data => {
    // hopefully this is never triggered
    console.info(data)
}

const send_form = fields => {
    console.debug(fields)
    $.ajax({
        type: 'POST',
        url: window.rockon_data.api_crew_signup,
        data: JSON.stringify(fields),
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        mode: 'same-origin',
        dataType: 'json',
        success: data => ajax_success(data),
        error: data => ajax_error(data),
        complete: data => ajax_complete(data)
    })
}
