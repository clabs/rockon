console.debug('bandbewerbung-form.js loaded')

const DateTime = luxon.DateTime

$(document).ready(() => {
  console.debug('document ready')
  const toastAudioPlayerElement = document.getElementById('toastAudioPlayer')
  const toastAudioPlayer = bootstrap.Toast.getOrCreateInstance(
    toastAudioPlayerElement
  )
  $('#save_form').on('click', event => {
    event.preventDefault()
    console.debug('save')
    send_form()
  })
  $('#name').on('change', event => {
    $('#band_title').text(event.target.value)
  })
  $('#add_url').on('click', event => {
    event.preventDefault()
    console.debug('add url')
    const url = $('#url_input').val()
    if (url === '') return
    $('#url_input').val('')
    api_add_url(url, 'link')
    $('#add_url').prop('disabled', true)
  })
  $('#add_web_url').on('click', event => {
    event.preventDefault()
    console.debug('add url')
    const url = $('#web_url_input').val()
    if (url === '') return
    $('#web_url_input').val('')
    api_add_web_url(url, 'web')
    $('#add_web_url').prop('disabled', true)
  })
  $(document).on('click', '[data-remove-url]', event => {
    event.preventDefault()
    const id = event.currentTarget.dataset.removeUrl
    console.debug('remove url', id)
    api_remove_url(id)
  })
  $(document).on('click', '[data-remove-document]', event => {
    event.preventDefault()
    const id = event.currentTarget.dataset.removeDocument
    console.debug('remove document', id)
    api_remove_document(id)
  })
  $(document).on('click', '[data-remove-song]', event => {
    event.preventDefault()
    const id = event.currentTarget.dataset.removeSong
    console.debug('remove song', id)
    api_remove_song(id)
  })
  $('#url_input').on('blur change', function () {
    const url = $(this).val()
    if (isValidURL(url)) {
      $('#add_url').prop('disabled', false)
    } else {
      $('#add_url').prop('disabled', true)
    }
  })
  $('#web_url_input').on('blur change', function () {
    const url = $(this).val()
    if (isValidURL(url)) {
      $('#add_web_url').prop('disabled', false)
    } else {
      $('#add_web_url').prop('disabled', true)
    }
  })
  $('#selectedFileDocument').on('change', event => {
    console.debug('file selected', event)
    const file = event.target.files[0]
    if (!file) return
    console.debug('file', file)
    upload_file(file, 'document')
  })
  $('#selectNewDocument').on('click', function () {
    $('#selectedFileDocument').click()
  })
  $('#selectedSong').on('change', event => {
    console.debug('file selected', event)
    const file = event.target.files[0]
    if (!file) return
    console.debug('file', file)
    const new_song = upload_file(file, 'audio')
  })
  $('#selectNewSong').on('click', function () {
    $('#selectedSong').click()
  })
  $(document).on('click', '.play-audio', function (event) {
    event.preventDefault() // prevent the default action
    console.debug('play audio', event)
    const url = event.currentTarget.href
    console.debug('url', url)
    createAudioPlayer(url, event.currentTarget.innerText)
    bootstrap.Toast.getOrCreateInstance(toastAudioPlayer)
    toastAudioPlayer.show()
    toastAudioPlayerElement.addEventListener('hidden.bs.toast', () => {
      console.debug('toast closed, remove player')
      $('#player-live').remove()
    })
  })
  $('#fileInputBandPressPhoto').on('change', function (event) {
    console.debug('file selected', event)
    const file = event.target.files[0]
    if (!file) return
    console.debug('file', file)
    upload_file(file, 'press_photo')
  })
  $('#bandPressPhoto').on('click', function () {
    $('#fileInputBandPressPhoto').click()
  })
  $('#fileInputBandLogo').on('change', function (event) {
    console.debug('file selected', event)
    const file = event.target.files[0]
    if (!file) return
    console.debug('file', file)
    upload_file(file, 'logo')
  })
  $('#bandLogo').on('click', function () {
    $('#fileInputBandLogo').click()
  })
})

const upload_file = (file, type) => {
  const form_data = new FormData()
  form_data.append('file', file)
  form_data.append('media_type', type)
  form_data.append('band', window.rockon_data.band_id)
  $.ajax({
    type: 'POST',
    url: window.rockon_data.api_url_new_media + 'upload/',
    data: form_data,
    contentType: false,
    processData: false,
    headers: {
      'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
    },
    mode: 'same-origin',
    dataType: 'json',
    success: data => file_upload_success(data, type),
    error: data => ajax_error(data),
    complete: data => ajax_complete(data)
  })
}

const li_add_url = url => {
  const element = `<li id="url-${url.id}"><a href="${url.url}" target="_blank">${url.url}</a><span class="btn btn-default btn-xs" data-remove-url="${url.id}"><i class="fa fa-trash"></i></span></li>`
  $('#url_list').append(element)
}

const li_add_web_url = url => {
  const element = `<li id="url-${url.id}"><a href="${url.url}" target="_blank">${url.url}</a><span class="btn btn-default btn-xs" data-remove-url="${url.id}"><i class="fa fa-trash"></i></span></li>`
  $('#web_url_list').append(element)
}

const li_add_document = document => {
  const element = `<li id="document-${document.id}" class="list-group-item d-flex justify-content-between align-items-center"><a href="${document.file}" target="_blank">${document.file_name_original}</a><span class="btn btn-default btn-xs" data-remove-document="${document.id}"><i class="fa fa-trash"></i></span></li>`
  $('#document_list').append(element)
  $('#document_counter').text($('#document_list li').length)
}

const li_add_song = song => {
  const element = `<li id="song-${song.id}" class="list-group-item d-flex justify-content-between align-items-center"><a class="play-audio" href="${song.file}" target="_blank">${song.file_name_original}</a><span class="btn btn-default btn-xs" data-remove-song="${song.id}"><i class="fa fa-trash"></i></span></li>`
  $('#song_list').append(element)
  $('#audio_counter').text($('#song_list li').length)
}

const li_remove_url = id => {
  $(`#url-${id}`).remove()
}

const li_remove_document = id => {
  $(`#document-${id}`).remove()
  $('#document_counter').text($('#document_list li').length)
}

const li_remove_song = id => {
  $(`#song-${id}`).remove()
  $('#audio_counter').text($('#song_list li').length)
}

const render_updated_at = (updated_at) => {
  const date = DateTime.fromISO(updated_at)
  const formattedDate = date.toFormat('d.M.yyyy, H:mm')
  $('#updated_at').text(formattedDate)
}

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
  form_obj['mean_age_under_27'] = form_obj['mean_age_under_27'] || false
  form_obj['is_coverband'] = form_obj['is_coverband'] || false
  form_obj['federal_state'] = $('#federal_state').val() || null

  console.debug('form obj', form_obj)

  $.ajax({
    type: 'PATCH',
    url: window.rockon_data.api_url_band_details,
    data: JSON.stringify(form_obj),
    contentType: 'application/json',
    headers: {
      'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
    },
    mode: 'same-origin',
    dataType: 'json',
    success: data => save_success(data),
    error: data => ajax_error(data, form_obj, window.rockon_data.api_url_band_details),
    complete: data => ajax_complete(data)
  })
}

const save_success = data => {
  console.debug('save success', data)
  render_updated_at(data.updated_at)
  alert("✅ Bandbewerbung gespeichert und abgeschickt.")
}

const api_add_url = (url, type) => {
  console.debug('add url api')
  media_obj = {
    url: url,
    media_type: type,
    band: window.rockon_data.band_id
  }
  $.ajax({
    type: 'POST',
    url: window.rockon_data.api_url_new_media + 'upload/',
    data: JSON.stringify(media_obj),
    contentType: 'application/json',
    headers: {
      'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
    },
    mode: 'same-origin',
    dataType: 'json',
    success: data => li_add_url(data),
    error: data => ajax_error(data),
    complete: data => ajax_complete(data)
  })
}

const api_add_web_url = (url, type) => {
  console.debug('add web url api')
  media_obj = {
    url: url,
    media_type: type,
    band: window.rockon_data.band_id
  }
  $.ajax({
    type: 'POST',
    url: window.rockon_data.api_url_new_media + 'upload/',
    data: JSON.stringify(media_obj),
    contentType: 'application/json',
    headers: {
      'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
    },
    mode: 'same-origin',
    dataType: 'json',
    success: data => li_add_web_url(data),
    error: data => ajax_error(data),
    complete: data => ajax_complete(data)
  })
}

const api_remove_url = id => {
  console.debug('remove url')
  $.ajax({
    type: 'DELETE',
    url: window.rockon_data.api_url_new_media + id + '/',
    contentType: 'application/json',
    headers: {
      'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
    },
    mode: 'same-origin',
    success: data => li_remove_url(id),
    error: data => ajax_error(data),
    complete: data => ajax_complete(data)
  })
}

const api_remove_document = id => {
  console.debug('remove document')
  $.ajax({
    type: 'DELETE',
    url: window.rockon_data.api_url_new_media + id + '/',
    contentType: 'application/json',
    headers: {
      'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
    },
    mode: 'same-origin',
    success: data => li_remove_document(id),
    error: data => ajax_error(data),
    complete: data => ajax_complete(data)
  })
}

const api_remove_song = id => {
  console.debug('remove song')
  $.ajax({
    type: 'DELETE',
    url: window.rockon_data.api_url_new_media + id + '/',
    contentType: 'application/json',
    headers: {
      'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
    },
    mode: 'same-origin',
    success: data => li_remove_song(id),
    error: data => ajax_error(data),
    complete: data => ajax_complete(data)
  })
}

const isValidURL = url => {
  try {
    new URL(url)
    return true
  } catch (_) {
    return false
  }
}

ajax_success = data => {
  console.info(data)
}
ajax_error = (data, form_obj, url) => {
  // FIXME: needs error handling
  console.error(data)
  const response = responseJSON
  $('#api_message').html(`
    <div class="alert alert-danger alert-dismissible fade show" role="alert">
      <strong>Fehler!</strong> Bitte schicke uns folgenden Text an <a href="mailto:hallo@rockon.dev">hallo@rockon.dev</a>: <br>
      <pre style="background-color: black; font-color: white;">
      ${JSON.stringify(data)}
      ${JSON.stringify(form_obj)}
      ${url}
      </pre>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `)
}
ajax_complete = data => {
  console.info(data)
}

const file_upload_success = (data, type) => {
  console.debug('file upload success', data)
  if (type === 'audio') {
    li_add_song(data)
  } else if (type === 'document') {
    li_add_document(data)
  } else if (type === 'press_photo') {
    $('#bandPressPhoto').attr('src', data.file)
  } else if (type === 'logo') {
    $('#bandLogo').attr('src', data.file)
  }
}

const createAudioPlayer = (url, file_name) => {
  if ($('#player-live').length) {
    $('#player-live').remove()
  }
  const player = document.createElement('audio')
  player.id = 'player-live'
  player.controls = true
  player.autoplay = true
  const source = document.createElement('source')
  source.src = url
  player.appendChild(source)
  const filename = document.getElementById('player-filename')
  filename.innerText = file_name

  const player_wrapper = document.getElementById('player-wrapper')
  player_wrapper.appendChild(player)
}
