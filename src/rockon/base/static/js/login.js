$(document).ready(() => {
  $('#form_signup_submit').on('click', (event) => {
    event.preventDefault()
    console.debug("submit")
    const form = $('#signup')
    var validated = false
    el = form.find('.not-empty')
    console.debug("not-empty elements", el)
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
    console.debug("validated", validated)
    const form_data = form.serializeArray()
    console.debug("form data", form_data)
    if (validated) {
      send_form(form_data)
    }
  })

  $('#signup .not-empty').on('blur', event => {
    console.debug("not-empty handler triggered", event)
    validate_input(event)
    render_error_message()
  })

  $('form').on('submit', event => {
    event.preventDefault()
  })
  $('#form_login_submit').click((event) => {
    event.preventDefault()
    form_login_submit()
  })
  $('#login_form .not-empty').on('blur keyup change', event => {
    console.debug("not-empty handler triggered", event.target.value)
    if (validateEmail(event.target.value)) {
      event.target.classList.remove('is-invalid')
      event.target.classList.add('is-valid')
      $('#form_login_submit').prop('disabled', false)
    } else {
      event.target.classList.remove('is-valid')
      event.target.classList.add('is-invalid')
      $('#form_login_submit').prop('disabled', true)
    }
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
  }
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

ajax_account_create_success = (data) => {
  console.info(data)
  $(window).unbind('beforeunload')
  window.location.href = window.rockon_data.account_created_redirect
}
ajax_error = (data) => {
  // FIXME: needs error handling
  console.error(data.responseJSON)
  if (data.responseJSON && data.responseJSON.status === "exists") {
    $('#form_message').html('<div class="alert alert-danger" role="alert">Diese E-Mail-Adresse ist bereits registiert, lasse dir einen magischen Link zukommen, um dich einzulogen.</div>')
    $("#signup :input").prop("disabled", true)
    $('#form_submit').prop("disabled", true)
  }
}
ajax_complete = (data) => {
  // hopefully this is never triggered
  console.info(data)
}

const send_form = (fields) => {
  console.debug(fields)
  $.ajax({
    type: "POST",
    url: window.rockon_data.api_crm_account_create,
    data: JSON.stringify(fields),
    contentType: "application/json",
    headers: {
      "X-CSRFToken": $('[name=csrfmiddlewaretoken]').val(),
    },
    mode: "same-origin",
    dataType: "json",
    success: (data) => ajax_account_create_success(data),
    error: (data) => ajax_error(data),
    complete: (data) => ajax_complete(data)
  })
}

ajax_complete_login = (data) => {
  // hopenfully this is never triggered
  console.info(data)
  $('#form_login_submit').prop('disabled', true)
  $('#user_email').prop('disabled', true)
  $('#login_message').removeClass('d-none')
}

const validateEmail = (email) => {
  return String(email)
    .toLowerCase()
    .match(
      /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    )
}

const form_login_submit = () => {
  console.debug()
  $.ajax({
    type: "POST",
    url: window.rockon_data.api_crm_request_magic_link,
    data: JSON.stringify({user_email: $("input[name=login_user_email]").val()}),
    contentType: "application/json",
    headers: {
      "X-CSRFToken": $('[name=csrfmiddlewaretoken]').val(),
    },
    mode: "same-origin",
    dataType: "json",
    success: (data) => null,
    error: (data) => ajax_error(data),
    complete: (data) => ajax_complete_login(data)
  })
}
