const { ref, computed, onMounted, nextTick } = Vue

const LineupApp = {
  setup() {
    // ── reactive state ──────────────────────────────────────
    const timeslots = ref(window.rockon_data.timeslots)
    const unassignedBands = ref(window.rockon_data.unassigned_bands)
    const saving = ref(false)
    const error = ref(null)
    const csrfToken = window.rockon_data.csrf_token
    const voteUrlBase = window.rockon_data.vote_url_base

    function voteUrl(guid) {
      return `${voteUrlBase}#/bid/${guid}/`
    }

    // ── track colors ────────────────────────────────────────
    const trackColorCache = {}
    const TRACK_PALETTE = [
      '#e91e63', '#9c27b0', '#673ab7', '#3f51b5',
      '#2196f3', '#00bcd4', '#009688', '#4caf50',
      '#ff9800', '#ff5722', '#795548', '#607d8b',
    ]
    let paletteIdx = 0

    function trackColor(trackName) {
      if (!trackName) return null
      if (!trackColorCache[trackName]) {
        trackColorCache[trackName] = TRACK_PALETTE[paletteIdx % TRACK_PALETTE.length]
        paletteIdx++
      }
      return trackColorCache[trackName]
    }

    function trackStyle(trackName) {
      const bg = trackColor(trackName)
      if (!bg) return {}
      return { background: bg, color: '#fff', border: 'none' }
    }

    function bandCardStyle(trackName) {
      const hex = trackColor(trackName)
      if (!hex) return {}
      // Convert hex to rgba with low alpha for a subtle tint
      const r = parseInt(hex.slice(1, 3), 16)
      const g = parseInt(hex.slice(3, 5), 16)
      const b = parseInt(hex.slice(5, 7), 16)
      return {
        background: `rgba(${r}, ${g}, ${b}, 0.2)`,
        borderColor: `rgba(${r}, ${g}, ${b}, 0.6)`,
      }
    }

    // ── slot element refs for SortableJS ────────────────────
    const slotRefs = {}
    function setSlotRef(slotId, el) {
      if (el) slotRefs[slotId] = el
    }

    const bandPool = ref(null)
    const wildcardPool = ref(null)
    const replacementPool = ref(null)

    // ── computed ────────────────────────────────────────────
    const assignedCount = computed(
      () => timeslots.value.filter((ts) => ts.band_id).length
    )

    const regularBands = computed(
      () => unassignedBands.value.filter((b) => b.bid_status !== 'replacement' && b.track !== 'Wildcard')
    )
    const wildcardBands = computed(
      () => unassignedBands.value.filter((b) => b.bid_status !== 'replacement' && b.track === 'Wildcard')
    )
    const replacementBands = computed(
      () => unassignedBands.value.filter((b) => b.bid_status === 'replacement')
    )

    const days = computed(() => {
      const map = {}
      for (const ts of timeslots.value) {
        if (!map[ts.day]) {
          map[ts.day] = { date: ts.day, label: ts.day_label }
        }
      }
      return Object.values(map)
    })

    // Rows keyed by time range, each cell maps to a timeslot per day
    const timeRows = computed(() => {
      const rowMap = {}
      const rowOrder = []
      for (const ts of timeslots.value) {
        const key = `${ts.start}-${ts.end}`
        if (!rowMap[key]) {
          rowMap[key] = { key, start: ts.start, end: ts.end, slotsByDay: {} }
          rowOrder.push(key)
        }
        rowMap[key].slotsByDay[ts.day] = ts
      }
      return rowOrder.map((k) => rowMap[k]).sort((a, b) => a.start.localeCompare(b.start))
    })

    // ── helpers ─────────────────────────────────────────────
    function findTimeslot(id) {
      return timeslots.value.find((ts) => ts.id === id)
    }

    function findBandInPool(id) {
      return unassignedBands.value.find((b) => b.id === id)
    }

    function removeBandFromPool(bandId) {
      unassignedBands.value = unassignedBands.value.filter((b) => b.id !== bandId)
    }

    function addBandToPool(bandId, bandName, genre, track, guid, bidStatus) {
      if (!findBandInPool(bandId)) {
        unassignedBands.value.push({ id: bandId, name: bandName, genre: genre || '', track: track || null, guid: guid || null, bid_status: bidStatus || 'lineup' })
      }
    }

    // ── API call ────────────────────────────────────────────
    async function patchTimeslot(slotId, bandId) {
      saving.value = true
      error.value = null
      try {
        const res = await fetch(`/api/v2/timeslots/${slotId}/`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          body: JSON.stringify({ band_id: bandId }),
        })
        if (!res.ok) {
          const text = await res.text()
          throw new Error(`HTTP ${res.status}: ${text}`)
        }
        return await res.json()
      } catch (e) {
        error.value = e.message
        throw e
      } finally {
        saving.value = false
      }
    }

    // ── assign / unassign ───────────────────────────────────
    async function assignBand(slotId, bandId) {
      const ts = findTimeslot(slotId)
      if (!ts) return

      // If slot already had a band, return it to pool
      const oldBandId = ts.band_id
      const oldBandName = ts.band_name
      const oldBandGenre = ts.band_genre
      const oldBandTrack = ts.band_track
      const oldBandGuid = ts.band_guid
      const oldBandBidStatus = ts.band_bid_status

      // Find band info (pool or another slot)
      const poolBand = findBandInPool(bandId)
      let bandName = poolBand ? poolBand.name : null
      let bandGenre = poolBand ? poolBand.genre : null
      let bandTrack = poolBand ? poolBand.track : null
      let bandGuid = poolBand ? poolBand.guid : null
      let bandBidStatus = poolBand ? poolBand.bid_status : null

      // If band came from another slot, clear that slot (or swap)
      const sourceSlot = timeslots.value.find(
        (s) => s.band_id === bandId && s.id !== slotId
      )
      if (sourceSlot) {
        bandName = bandName || sourceSlot.band_name
        bandGenre = bandGenre || sourceSlot.band_genre
        bandTrack = bandTrack || sourceSlot.band_track
        bandGuid = bandGuid || sourceSlot.band_guid
        bandBidStatus = bandBidStatus || sourceSlot.band_bid_status

        // Swap: move the target slot's band into the source slot
        if (oldBandId && oldBandId !== bandId) {
          sourceSlot.band_id = oldBandId
          sourceSlot.band_name = oldBandName
          sourceSlot.band_genre = oldBandGenre
          sourceSlot.band_track = oldBandTrack
          sourceSlot.band_guid = oldBandGuid
          sourceSlot.band_bid_status = oldBandBidStatus
        } else {
          sourceSlot.band_id = null
          sourceSlot.band_name = null
          sourceSlot.band_genre = null
          sourceSlot.band_track = null
          sourceSlot.band_guid = null
          sourceSlot.band_bid_status = null
        }
      }

      // Optimistic update
      removeBandFromPool(bandId)
      ts.band_id = bandId
      ts.band_name = bandName
      ts.band_genre = bandGenre
      ts.band_track = bandTrack
      ts.band_guid = bandGuid
      ts.band_bid_status = bandBidStatus

      // If the old band wasn't swapped into source slot, return it to pool
      if (oldBandId && oldBandId !== bandId && !sourceSlot) {
        addBandToPool(oldBandId, oldBandName, oldBandGenre, oldBandTrack, oldBandGuid, oldBandBidStatus)
      }

      try {
        const result = await patchTimeslot(slotId, bandId)
        // Update with server-confirmed data
        ts.band_id = result.band_id
        ts.band_name = result.band_name
        ts.band_genre = result.band_genre
        ts.band_track = result.band_track
        ts.band_guid = result.band_guid
        ts.band_bid_status = result.band_bid_status

        // If we swapped, also persist the source slot
        if (sourceSlot && sourceSlot.band_id) {
          const swapResult = await patchTimeslot(sourceSlot.id, sourceSlot.band_id)
          sourceSlot.band_id = swapResult.band_id
          sourceSlot.band_name = swapResult.band_name
          sourceSlot.band_genre = swapResult.band_genre
          sourceSlot.band_track = swapResult.band_track
          sourceSlot.band_guid = swapResult.band_guid
          sourceSlot.band_bid_status = swapResult.band_bid_status
        } else if (sourceSlot) {
          await patchTimeslot(sourceSlot.id, null)
        }
      } catch (e) {
        // Revert on error
        ts.band_id = oldBandId
        ts.band_name = oldBandName
        ts.band_genre = oldBandGenre
        ts.band_track = oldBandTrack
        ts.band_guid = oldBandGuid
        ts.band_bid_status = oldBandBidStatus
        if (sourceSlot) {
          sourceSlot.band_id = bandId
          sourceSlot.band_name = bandName
          sourceSlot.band_genre = bandGenre
          sourceSlot.band_track = bandTrack
          sourceSlot.band_guid = bandGuid
          sourceSlot.band_bid_status = bandBidStatus
        }
        if (poolBand) {
          addBandToPool(bandId, bandName, bandGenre)
        }
        if (oldBandId && !sourceSlot) {
          removeBandFromPool(oldBandId)
        }
      }

      // Re-init sortables after state change
      await nextTick()
      initSlotSortables()
    }

    async function removeBand(ts) {
      const bandId = ts.band_id
      const bandName = ts.band_name
      const bandGenre = ts.band_genre
      const bandTrack = ts.band_track
      const bandGuid = ts.band_guid
      const bandBidStatus = ts.band_bid_status
      if (!bandId) return

      // Optimistic
      ts.band_id = null
      ts.band_name = null
      ts.band_genre = null
      ts.band_track = null
      ts.band_guid = null
      ts.band_bid_status = null
      addBandToPool(bandId, bandName, bandGenre, bandTrack, bandGuid, bandBidStatus)

      try {
        await patchTimeslot(ts.id, null)
      } catch (e) {
        // Revert
        ts.band_id = bandId
        ts.band_name = bandName
        ts.band_genre = bandGenre
        ts.band_track = bandTrack
        ts.band_guid = bandGuid
        ts.band_bid_status = bandBidStatus
        removeBandFromPool(bandId)
      }

      await nextTick()
      initSlotSortables()
    }

    // ── SortableJS setup ────────────────────────────────────
    let poolSortable = null
    let wildcardSortable = null
    let replacementSortable = null
    const slotSortables = new Map()

    function _makePoolSortable(el) {
      return new Sortable(el, {
        group: { name: 'bands', pull: true, put: true },
        sort: false,
        animation: 150,
        ghostClass: 'sortable-ghost',
        dragClass: 'sortable-drag',
        onAdd(evt) {
          const bandId = evt.item.dataset.bandId
          if (!bandId) return
          evt.item.remove()
          const slot = timeslots.value.find((s) => s.band_id === bandId)
          if (slot) {
            removeBand(slot)
          }
        },
      })
    }

    function initPoolSortable() {
      if (poolSortable) poolSortable.destroy()
      if (wildcardSortable) wildcardSortable.destroy()
      if (replacementSortable) replacementSortable.destroy()
      if (bandPool.value) poolSortable = _makePoolSortable(bandPool.value)
      if (wildcardPool.value) wildcardSortable = _makePoolSortable(wildcardPool.value)
      if (replacementPool.value) replacementSortable = _makePoolSortable(replacementPool.value)
    }

    function initSlotSortables() {
      // Destroy old ones
      for (const [, sortable] of slotSortables) {
        sortable.destroy()
      }
      slotSortables.clear()

      for (const ts of timeslots.value) {
        const el = slotRefs[ts.id]
        if (!el) continue

        const sortable = new Sortable(el, {
          group: { name: 'bands', pull: true, put: true },
          animation: 150,
          ghostClass: 'sortable-ghost',
          dragClass: 'sortable-drag',
          onAdd(evt) {
            const bandId = evt.item.dataset.bandId
            if (!bandId) return

            // Revert SortableJS DOM manipulation: put the element back
            // where it came from so Vue's virtual DOM stays consistent.
            // Vue will re-render both source and target from reactive state.
            const srcContainer = evt.from
            if (srcContainer) {
              const refNode = srcContainer.children[evt.oldIndex] || null
              srcContainer.insertBefore(evt.item, refNode)
            } else {
              evt.item.remove()
            }

            assignBand(ts.id, bandId)
          },
        })
        slotSortables.set(ts.id, sortable)
      }
    }

    onMounted(() => {
      nextTick(() => {
        initPoolSortable()
        initSlotSortables()
      })
    })

    return {
      timeslots,
      unassignedBands,
      regularBands,
      wildcardBands,
      saving,
      error,
      assignedCount,
      days,
      timeRows,
      bandPool,
      wildcardPool,
      replacementPool,
      replacementBands,
      setSlotRef,
      removeBand,
      voteUrl,
      trackStyle,
      bandCardStyle,
    }
  },
}
