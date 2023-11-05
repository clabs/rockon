console.debug('bandbewerbung-form.js loaded')

$(document).ready(() => {
  $('#save_form').on('click', event => {
    event.preventDefault()
    console.debug('save')
    send_form()
  })
  $('#name').on('change', event => {
    $('#band_title').text(event.target.value)
  })
})

const send_form = () => {
  form = $('#application')
  const form_data = form.serializeArray()
  form_obj = {}
  for (const el of form_data) {
    if (el.name === 'csrfmiddlewaretoken') continue // skip csrf token
    if (el.value === '') continue // skip empty values
    if (el.value === 'on') el.value = true
    form_obj[el.name] = el.value
  }
  form_obj['are_students'] = form_obj['are_students'] || false
  form_obj['has_management'] = form_obj['has_management'] || false
  form_obj['federal_state'] = $('#federal_state').val() || null

  console.debug('form obj', form_obj)

  $.ajax({
    type: 'PATCH',
    url: window.rockon_data.api_url,
    data: JSON.stringify(form_obj),
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

ajax_success = data => {
  console.info(data)
  $(window).unbind('beforeunload')
  // window.location.href = window.rockon_data.success_redirect
}
ajax_error = data => {
  // FIXME: needs error handling
  console.error(data)
}
ajax_complete = data => {
  // hopefully this is never triggered
  console.info(data)
}
