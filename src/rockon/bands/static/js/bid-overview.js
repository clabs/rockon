const { createApp, ref, computed, onMounted, nextTick, watch } = Vue

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
  return match ? decodeURIComponent(match[2]) : null
}

const BidOverviewApp = {
  setup() {
    const bands = ref(window.rockon_data.bands)
    const statusChoices = ref(window.rockon_data.statusChoices)
    const statusLabelMap = computed(() => {
      const m = {}
      for (const c of statusChoices.value) m[c.value] = c.label
      return m
    })
    const searchQuery = ref('')
    const sortKey = ref('votes_sum')
    const sortDir = ref('desc')
    const pageSize = ref(-1) // -1 = All
    const currentPage = ref(1)

    // --- Column filters (Excel-style multi-select) ---
    const selectedStatuses = ref(new Set())
    const selectedTracks = ref(new Set())
    const selectedComplete = ref(new Set())
    // Name filter: default to hiding bands without names
    const selectedName = ref(new Set([true])) // true = has name; hide unnamed by default

    // Unique values derived from all bands (not filtered)
    const availableStatuses = computed(() =>
      [...new Set(bands.value.map((b) => b.bid_status))].sort((a, b) => a.localeCompare(b, 'de'))
    )
    const availableTracks = computed(() => {
      const names = [...new Set(bands.value.map((b) => b.track_name))]
      const named = names.filter(Boolean).sort((a, b) => a.localeCompare(b, 'de'))
      const hasEmpty = names.some((n) => !n)
      const result = named.map((n) => ({ value: n, label: n }))
      if (hasEmpty) result.push({ value: '', label: 'Ohne Track' })
      return result
    })
    const availableComplete = computed(() => [
      { value: true, label: 'Vollständig' },
      { value: false, label: 'Unvollständig' },
    ])
    const availableName = computed(() => [
      { value: true, label: 'Mit Name' },
      { value: false, label: 'Ohne Name' },
    ])

    // Track which filter dropdown is open
    const openFilter = ref(null)
    function toggleFilter(name) {
      openFilter.value = openFilter.value === name ? null : name
    }
    function closeFilters() {
      openFilter.value = null
    }

    // Map filter names to their refs for template access
    const filterRefs = { status: selectedStatuses, track: selectedTracks, complete: selectedComplete, name: selectedName }

    function toggleFilterValue(filterName, value) {
      const r = filterRefs[filterName]
      const s = new Set(r.value)
      if (s.has(value)) s.delete(value)
      else s.add(value)
      r.value = s
    }
    function clearFilter(filterName) {
      filterRefs[filterName].value = new Set()
    }
    function isFilterActive(filterName) {
      return filterRefs[filterName].value.size > 0
    }
    function isChecked(filterName, value) {
      return filterRefs[filterName].value.has(value)
    }

    // Close dropdowns on outside click
    onMounted(() => {
      document.addEventListener('click', (e) => {
        if (!e.target.closest('.col-filter')) closeFilters()
      })
    })

    // --- Filtering ---
    const filteredBands = computed(() => {
      let result = bands.value

      // Text search
      if (searchQuery.value.trim()) {
        const q = searchQuery.value.toLowerCase().trim()
        result = result.filter(
          (b) =>
            b.name.toLowerCase().includes(q) ||
            b.bid_status.toLowerCase().includes(q) ||
            b.track_name.toLowerCase().includes(q) ||
            b.contact_email.toLowerCase().includes(q)
        )
      }

      // Column filters
      if (selectedName.value.size > 0) {
        result = result.filter((b) => selectedName.value.has(b.has_name))
      }
      if (selectedStatuses.value.size > 0) {
        result = result.filter((b) => selectedStatuses.value.has(b.bid_status))
      }
      if (selectedTracks.value.size > 0) {
        result = result.filter((b) => selectedTracks.value.has(b.track_name))
      }
      if (selectedComplete.value.size > 0) {
        result = result.filter((b) => selectedComplete.value.has(b.bid_complete))
      }

      return result
    })

    // --- Sorting ---
    const numericKeys = new Set([
      'votes_avg',
      'votes_sum',
      'votes_count',
    ])

    const sortedBands = computed(() => {
      const arr = [...filteredBands.value]
      const key = sortKey.value
      const dir = sortDir.value === 'asc' ? 1 : -1

      arr.sort((a, b) => {
        let va = a[key]
        let vb = b[key]

        if (numericKeys.has(key)) {
          va = Number(va) || 0
          vb = Number(vb) || 0
          return (va - vb) * dir
        }

        if (key === 'bid_complete') {
          return ((va === vb ? 0 : va ? -1 : 1)) * dir
        }

        // String comparison
        va = String(va || '').toLowerCase()
        vb = String(vb || '').toLowerCase()
        return va.localeCompare(vb, 'de') * dir
      })
      return arr
    })

    // --- Pagination ---
    const totalPages = computed(() => {
      if (pageSize.value === -1) return 1
      return Math.max(1, Math.ceil(filteredBands.value.length / pageSize.value))
    })

    const paginatedBands = computed(() => {
      if (pageSize.value === -1) return sortedBands.value
      const start = (currentPage.value - 1) * pageSize.value
      return sortedBands.value.slice(start, start + pageSize.value)
    })

    const paginationPages = computed(() => {
      const total = totalPages.value
      if (total <= 1) return []
      const current = currentPage.value
      const pages = []
      const delta = 2

      let start = Math.max(1, current - delta)
      let end = Math.min(total, current + delta)

      if (current - delta < 1) end = Math.min(total, end + (delta - current + 1))
      if (current + delta > total) start = Math.max(1, start - (current + delta - total))

      if (start > 1) {
        pages.push(1)
        if (start > 2) pages.push('...')
      }
      for (let i = start; i <= end; i++) pages.push(i)
      if (end < total) {
        if (end < total - 1) pages.push('...')
        pages.push(total)
      }
      return pages
    })

    // Reset page when filters or page size change
    watch([searchQuery, pageSize, selectedStatuses, selectedTracks, selectedComplete, selectedName], () => {
      currentPage.value = 1
    })

    // --- Sort toggling ---
    function toggleSort(key) {
      if (sortKey.value === key) {
        sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
      } else {
        sortKey.value = key
        sortDir.value = numericKeys.has(key) || key === 'bid_complete' ? 'desc' : 'asc'
      }
    }

    function sortIcon(key) {
      if (sortKey.value !== key) return '⇅'
      return sortDir.value === 'asc' ? '▲' : '▼'
    }

    // --- Sparkline helpers ---
    const wowColors = {
      0: '#9d9d9d', // Poor (grey)
      1: '#ffffff', // Common (white)
      2: '#1eff00', // Uncommon (green)
      3: '#0070dd', // Rare (blue)
      4: '#a335ee', // Epic (purple)
      5: '#ff8000', // Legendary (orange)
    }
    function barColor(star) {
      return wowColors[star] || '#9d9d9d'
    }

    function barHeight(count, counters) {
      const maxVal = Math.max(...Object.values(counters), 1)
      if (maxVal === 0) return 8 // flat bars for no votes
      return Math.round((count / maxVal) * 24)
    }

    function tooltipHtml(counters) {
      return Object.entries(counters)
        .filter(([, v]) => v > 0)
        .map(([k, v]) => `${v}x ${k}⭐`)
        .join('<br>')
    }

    function hasVotes(counters) {
      return Object.values(counters).some((v) => v > 0)
    }

    // --- Inline status editing ---
    async function updateBandStatus(band, newValue) {
      const oldValue = band.bid_status_value
      const oldDisplay = band.bid_status
      band._saving = true
      band.bid_status_value = newValue
      band.bid_status = statusLabelMap.value[newValue] || newValue
      try {
        const resp = await fetch(`/api/v2/bands/${band.id}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: JSON.stringify({ bid_status: newValue }),
        })
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      } catch (err) {
        console.error('Status update failed:', err)
        band.bid_status_value = oldValue
        band.bid_status = oldDisplay
      } finally {
        band._saving = false
      }
    }

    // --- Excel export ---
    function exportExcel() {
      const rows = sortedBands.value
        .filter((b) => b.has_name)
        .map((b) => ({
        Bandname: b.name,
        'Ø ⭐': b.votes_avg,
        Summe: b.votes_sum,
        Stimmen: b.votes_count,
        '0⭐': b.counters[0] || 0,
        '1⭐': b.counters[1] || 0,
        '2⭐': b.counters[2] || 0,
        '3⭐': b.counters[3] || 0,
        '4⭐': b.counters[4] || 0,
        '5⭐': b.counters[5] || 0,
        Status: b.bid_status,
        Track: b.track_name,
        Vollständig: b.bid_complete ? 'Ja' : 'Nein',
        Kontakt: b.contact_email,
      }))
      const ws = XLSX.utils.json_to_sheet(rows)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, 'Bands')
      XLSX.writeFile(wb, 'bands_uebersicht.xlsx')
    }

    // --- Bootstrap tooltips ---
    function initTooltips() {
      document
        .querySelectorAll('#app [data-bs-toggle="tooltip"]')
        .forEach((el) => {
          const existing = bootstrap.Tooltip.getInstance(el)
          if (existing) existing.dispose()
          new bootstrap.Tooltip(el)
        })
    }

    onMounted(() => nextTick(initTooltips))
    watch(paginatedBands, () => nextTick(initTooltips))

    // --- Page size handler (convert string to number) ---
    function setPageSize(event) {
      const val = event.target.value
      pageSize.value = val === 'all' ? -1 : parseInt(val, 10)
    }

    return {
      bands,
      searchQuery,
      sortKey,
      sortDir,
      pageSize,
      currentPage,
      filteredBands,
      sortedBands,
      paginatedBands,
      totalPages,
      paginationPages,
      toggleSort,
      sortIcon,
      barHeight,
      barColor,
      tooltipHtml,
      hasVotes,
      exportExcel,
      setPageSize,
      // Column filters
      availableStatuses,
      availableTracks,
      availableComplete,
      availableName,
      openFilter,
      toggleFilter,
      closeFilters,
      toggleFilterValue,
      clearFilter,
      isFilterActive,
      isChecked,
      // Inline status editing
      statusChoices,
      updateBandStatus,
    }
  },
}

createApp(BidOverviewApp).mount('#app')
