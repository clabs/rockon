const { ref, computed } = Vue

const NewsEditorApp = {
  setup() {
    const posts = ref(window.rockon_data.posts)
    const events = ref(window.rockon_data.events)
    const csrfToken = window.rockon_data.csrf_token

    const editing = ref(false)
    const saving = ref(false)
    const error = ref(null)
    const previewHtml = ref('')
    let previewTimer = null

    const emptyForm = () => ({
      id: null,
      title: '',
      body_markdown: '',
      status: 'draft',
      publish_at: '',
      event: '',
      audience_crew: false,
      audience_bands: false,
      audience_exhibitors: false,
    })
    const form = ref(emptyForm())

    function statusLabel(status) {
      return status === 'published' ? 'Veröffentlicht' : 'Entwurf'
    }

    function formatDate(iso) {
      if (!iso) return ''
      return new Date(iso).toLocaleString('de-DE')
    }

    function toDatetimeLocal(iso) {
      if (!iso) return ''
      const d = new Date(iso)
      const pad = (n) => String(n).padStart(2, '0')
      return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
    }

    function startCreate() {
      form.value = emptyForm()
      previewHtml.value = ''
      error.value = null
      editing.value = true
    }

    function startEdit(post) {
      form.value = {
        id: post.id,
        title: post.title,
        body_markdown: post.body_markdown,
        status: post.status,
        publish_at: toDatetimeLocal(post.publish_at),
        event: post.event || '',
        audience_crew: post.audience_crew,
        audience_bands: post.audience_bands,
        audience_exhibitors: post.audience_exhibitors,
      }
      previewHtml.value = post.body_html
      error.value = null
      editing.value = true
    }

    function cancelEdit() {
      editing.value = false
    }

    async function fetchPreview() {
      try {
        const res = await fetch('/api/v2/news/preview/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          body: JSON.stringify({ body_markdown: form.value.body_markdown }),
        })
        if (!res.ok) return
        const data = await res.json()
        previewHtml.value = data.body_html
      } catch (e) {
        // Preview failures are non-fatal; leave the last known preview in place.
      }
    }

    function schedulePreview() {
      if (previewTimer) clearTimeout(previewTimer)
      previewTimer = setTimeout(fetchPreview, 400)
    }

    function publishAtPayload() {
      return form.value.publish_at ? new Date(form.value.publish_at).toISOString() : null
    }

    async function save() {
      saving.value = true
      error.value = null
      const payload = {
        title: form.value.title,
        body_markdown: form.value.body_markdown,
        status: form.value.status,
        publish_at: publishAtPayload(),
        event: form.value.event || null,
        audience_crew: form.value.audience_crew,
        audience_bands: form.value.audience_bands,
        audience_exhibitors: form.value.audience_exhibitors,
      }
      const isCreate = !form.value.id
      const url = isCreate ? '/api/v2/news/' : `/api/v2/news/${form.value.id}/`
      try {
        const res = await fetch(url, {
          method: isCreate ? 'POST' : 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          body: JSON.stringify(payload),
        })
        if (!res.ok) {
          const text = await res.text()
          throw new Error(`HTTP ${res.status}: ${text}`)
        }
        const saved = await res.json()
        if (isCreate) {
          posts.value.unshift(saved)
        } else {
          const idx = posts.value.findIndex((p) => p.id === saved.id)
          if (idx !== -1) posts.value[idx] = saved
        }
        editing.value = false
      } catch (e) {
        error.value = e.message
      } finally {
        saving.value = false
      }
    }

    async function removePost(post) {
      if (!confirm(`"${post.title}" wirklich löschen?`)) return
      try {
        const res = await fetch(`/api/v2/news/${post.id}/`, {
          method: 'DELETE',
          headers: { 'X-CSRFToken': csrfToken },
        })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        posts.value = posts.value.filter((p) => p.id !== post.id)
      } catch (e) {
        error.value = e.message
      }
    }

    return {
      posts,
      events,
      editing,
      saving,
      error,
      previewHtml,
      form,
      statusLabel,
      formatDate,
      startCreate,
      startEdit,
      cancelEdit,
      schedulePreview,
      save,
      removePost,
    }
  },
}
