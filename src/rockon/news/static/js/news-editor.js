const { ref, computed, nextTick } = Vue

const NewsEditorApp = {
  setup() {
    const posts = ref(window.rockon_data.posts)
    const events = ref(window.rockon_data.events)
    const csrfToken = window.rockon_data.csrf_token

    const editing = ref(false)
    const saving = ref(false)
    const error = ref(null)
    const previewHtml = ref('')
    const bodyTextarea = ref(null)
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

    const hasAudience = computed(
      () => form.value.audience_crew || form.value.audience_bands || form.value.audience_exhibitors
    )

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

    // ── Markdown toolbar ────────────────────────────────────
    // Inserts Markdown syntax around the current textarea selection, then
    // restores focus/selection so typing continues naturally.
    function setSelectionAndRefresh(newValue, selectionStart, selectionEnd) {
      form.value.body_markdown = newValue
      schedulePreview()
      nextTick(() => {
        const el = bodyTextarea.value
        if (!el) return
        el.focus()
        el.selectionStart = selectionStart
        el.selectionEnd = selectionEnd
      })
    }

    function wrapSelection(before, after) {
      const el = bodyTextarea.value
      if (!el) return
      const start = el.selectionStart
      const end = el.selectionEnd
      const value = form.value.body_markdown
      const selected = value.slice(start, end) || 'Text'
      const newValue = value.slice(0, start) + before + selected + after + value.slice(end)
      setSelectionAndRefresh(newValue, start + before.length, start + before.length + selected.length)
    }

    function prefixLines(prefix) {
      const el = bodyTextarea.value
      if (!el) return
      const start = el.selectionStart
      const end = el.selectionEnd
      const value = form.value.body_markdown
      const lineStart = value.lastIndexOf('\n', start - 1) + 1
      const lineEndIdx = value.indexOf('\n', end)
      const lineEnd = lineEndIdx === -1 ? value.length : lineEndIdx
      const block = value.slice(lineStart, lineEnd)
      const prefixed = block
        .split('\n')
        .map((line) => prefix + line)
        .join('\n')
      const newValue = value.slice(0, lineStart) + prefixed + value.slice(lineEnd)
      setSelectionAndRefresh(newValue, lineStart, lineStart + prefixed.length)
    }

    function insertLink() {
      const el = bodyTextarea.value
      if (!el) return
      const start = el.selectionStart
      const end = el.selectionEnd
      const value = form.value.body_markdown
      const selected = value.slice(start, end) || 'Linktext'
      const markdown = `[${selected}](https://)`
      const newValue = value.slice(0, start) + markdown + value.slice(end)
      const urlStart = start + selected.length + 3
      setSelectionAndRefresh(newValue, urlStart, urlStart + 'https://'.length)
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
      bodyTextarea,
      form,
      hasAudience,
      statusLabel,
      formatDate,
      startCreate,
      startEdit,
      cancelEdit,
      schedulePreview,
      wrapSelection,
      prefixLines,
      insertLink,
      save,
      removePost,
    }
  },
}
