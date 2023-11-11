console.debug('bandbewerbung-form.js loaded')

$(document).ready(() => {
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
    api_add_url(url)
    $('#add_url').prop('disabled', true)
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
  $('.play-audio').on('click', function (event) {
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
  const element = `<li id="url-${url.id}"><i class="fa-brands fa-youtube"></i> <a href="${url.url}">${url.url}</a> <span class="btn btn-default btn-xs" data-remove-url="${url.id}"><i class="fa fa-trash" ></i></span></li>`
  $('#url_list').append(element)
}

const li_add_document = document => {
  const element = `<li id="document-${document.id}"><i class="fa fa-file"></i> <a href="${document.document}">${document.file_name_original}</a> <span class="btn btn-default btn-xs" data-remove-document="${document.id}"><i class="fa fa-trash"></i></span></li>`
  $('#document_list').append(element)
  $('#document_counter').text($('#document_list li').length)
}

const li_add_song = song => {
  const element = `<li id="song-${song.id}"><i class="fa fa-file"></i> <a href="${song.file}">${song.file_name_original}</a> <span class="btn btn-default btn-xs" data-remove-song="${song.id}"><i class="fa fa-trash"></i></span></li>`
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
    url: window.rockon_data.api_url_band_details,
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

const api_add_url = url => {
  console.debug('add url')
  media_obj = {
    url: url,
    media_type: 'link',
    band: window.rockon_data.band_id
  }
  $.ajax({
    type: 'POST',
    url: window.rockon_data.api_url_new_media,
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
ajax_error = data => {
  // FIXME: needs error handling
  console.error(data)
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