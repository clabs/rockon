const {createApp, ref} = Vue

// =============================================================================
// Filter Service - Centralized filter logic for band lists
// =============================================================================
const FilterService = {
    STORAGE_KEYS: {
        showBandNoName: 'filterShowBandsNoName',
        showIncompleteBids: 'filterIncompleteBids',
        showDeclinedBids: 'filterDeclinedBids',
        filterCollapsed: 'filterOptionsCollapsed'
    },

    /**
     * Load a filter setting from sessionStorage
     * @param {string} key - The filter key
     * @param {*} defaultValue - Default value if not found
     * @returns {*} The stored value or default
     */
    loadFromStorage(key, defaultValue = false) {
        const storageKey = this.STORAGE_KEYS[key] || key
        const stored = sessionStorage.getItem(storageKey)
        return stored !== null ? JSON.parse(stored) : defaultValue
    },

    /**
     * Save a filter setting to sessionStorage
     * @param {string} key - The filter key
     * @param {*} value - The value to store
     */
    saveToStorage(key, value) {
        const storageKey = this.STORAGE_KEYS[key] || key
        sessionStorage.setItem(storageKey, JSON.stringify(value))
    },

    /**
     * Apply base visibility filters (incomplete, no-name, declined)
     * @param {Array} bands - The bands to filter
     * @param {Object} filters - Filter settings {showIncompleteBids, showBandNoName, showDeclinedBids}
     * @returns {Array} Filtered bands
     */
    applyVisibilityFilters(bands, filters) {
        let result = bands

        if (!filters.showIncompleteBids) {
            result = result.filter(band => band.bid_complete === true)
        }
        if (!filters.showBandNoName) {
            result = result.filter(band => band.name)
        }
        if (!filters.showDeclinedBids) {
            result = result.filter(band => band.bid_status !== 'declined')
        }

        return result
    },

    /**
     * Apply selection filter (track, status, or special filter)
     * @param {Array} bands - The bands to filter (already visibility-filtered)
     * @param {*} selectedTrack - The selected track/filter
     * @param {Array} userVotes - User's votes for no-vote filter
     * @returns {Array} Filtered bands
     */
    applySelectionFilter(bands, selectedTrack, userVotes = []) {
        // No selection - return all
        if (!selectedTrack) {
            return bands
        }

        // String-based filters
        if (typeof selectedTrack === 'string') {
            switch (selectedTrack) {
                case 'no-track':
                    return bands.filter(band => !band.track)

                case 'student-bands':
                    return bands.filter(band => band.are_students)

                case 'under-27':
                    return bands.filter(band => band.mean_age_under_27 === true)

                case 'no-vote':
                    // Exclude declined bands, then filter for unvoted
                    return bands
                        .filter(band => !userVotes.some(vote => vote.band__id === band.id))

                default:
                    // Status filter (status-unknown, status-pending, etc.)
                    if (selectedTrack.startsWith('status-')) {
                        const statusValue = selectedTrack.replace('status-', '')
                        return bands.filter(band => band.bid_status === statusValue)
                    }
                    return bands
            }
        }

        // Track object filter
        if (selectedTrack?.id) {
            return bands.filter(band => band.track && band.track === selectedTrack.id)
        }

        return bands
    },

    /**
     * Apply all filters to a band list
     * @param {Array} bands - All bands
     * @param {Object} options - {filters, selectedTrack, userVotes}
     * @returns {Array} Filtered bands sorted by name (case-insensitive)
     */
    filterBands(bands, { filters, selectedTrack, userVotes = [] }) {
        const visibilityFiltered = this.applyVisibilityFilters(bands, filters)
        const selectionFiltered = this.applySelectionFilter(visibilityFiltered, selectedTrack, userVotes)

        // Sort case-insensitively by band name
        return selectionFiltered.sort((a, b) => {
            const nameA = (a.name || a.guid || '').toLowerCase()
            const nameB = (b.name || b.guid || '').toLowerCase()
            return nameA.localeCompare(nameB)
        })
    }
}

// =============================================================================
// Utils - Shared utility functions
// =============================================================================
const Utils = {
    /**
     * Format an ISO date string to German locale format
     * @param {string} isoString - ISO 8601 date string
     * @returns {string} Formatted date (dd.MM.yyyy, HH:mm)
     */
    formatDate(isoString) {
        return new Intl.DateTimeFormat('de-DE', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(isoString))
    }
}

const LoadingSpinner = Vue.defineComponent({
    props: ['bands', 'bandsToFetch'],
    computed: {
        progress() {
            return (this.bands.length / this.bandsToFetch) * 100
        }
    },
    template: `
  <div class="text-center mt-5">
    <div class="spinner-border text-primary" style="width: 9rem; height: 9rem;" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
  <div class="text-center mt-5">
  <h3 class="mt-3">Wir laden eine unfassbare Menge an Daten</h3>
  <div v-if="bandsToFetch">
    <div class="progress" role="progressbar" aria-label="Animated striped example" :aria-valuenow="bands.length" aria-valuemin="0" :aria-valuemax="bandsToFetch">
      <div class="progress-bar progress-bar-striped progress-bar-animated" :style="{ 'width': progress + '%' }"></div>
    </div>
    <p>{{ bands.length }} / {{ bandsToFetch }} Bands</p>
  </div>
  </div>
  `
})

// Skeleton component for band details loading state
const BandDetailsSkeleton = Vue.defineComponent({
    props: ['selectedBand'],
    computed: {
        bandName() {
            return this.selectedBand?.name || this.selectedBand?.guid || 'Lädt...'
        }
    },
    template: `
    <section class="row p-4 form-section">
      <!-- Band name - show actual name from list data -->
      <div class="col">
          <h3>{{ bandName }}</h3>
      </div>

      <!-- Tags skeleton -->
      <div class="row mt-3">
        <div class="col-9">
          <div class="d-flex flex-wrap gap-2">
            <span class="skeleton-text" style="width: 80px; height: 24px;"></span>
            <span class="skeleton-text" style="width: 100px; height: 24px;"></span>
            <span class="skeleton-text" style="width: 60px; height: 24px;"></span>
            <span class="skeleton-text" style="width: 90px; height: 24px;"></span>
          </div>
        </div>
        <div class="col-3">
          <div class="skeleton-text" style="width: 150px; height: 32px;"></div>
        </div>
      </div>

      <!-- Allgemeines section -->
      <h3 class="mt-4">Allgemeines</h3>
      <div class="col-12">
          <div class="alert alert-secondary" role="alert" style="min-height: 120px;">
            <div class="skeleton-text" style="width: 100%; height: 16px; margin-bottom: 8px;"></div>
            <div class="skeleton-text" style="width: 90%; height: 16px; margin-bottom: 8px;"></div>
            <div class="skeleton-text" style="width: 95%; height: 16px; margin-bottom: 8px;"></div>
            <div class="skeleton-text" style="width: 80%; height: 16px;"></div>
          </div>
      </div>
      <div class="col">
          <div><h4>Web</h4></div>
          <ul>
            <li><span class="skeleton-text" style="width: 200px; height: 16px;"></span></li>
            <li><span class="skeleton-text" style="width: 180px; height: 16px;"></span></li>
          </ul>
      </div>

      <!-- Media section -->
      <h3>Media</h3>
      <div class="col">
          <div><h4>Songs</h4></div>
          <ol>
            <li><span class="skeleton-text" style="width: 200px; height: 16px;"></span></li>
            <li><span class="skeleton-text" style="width: 180px; height: 16px;"></span></li>
            <li><span class="skeleton-text" style="width: 220px; height: 16px;"></span></li>
          </ol>
      </div>
      <div class="col">
          <div><h4>Links</h4></div>
          <ul>
            <li><span class="skeleton-text" style="width: 200px; height: 16px;"></span></li>
          </ul>
      </div>

      <!-- Images section -->
      <h4>Bilder</h4>
      <div class="col">
        <div class="row gallery">
          <div class="col">
            <div><h5>Photo</h5></div>
            <div class="detail-image-container">
              <div class="skeleton-loader"></div>
            </div>
          </div>
          <div class="col">
            <div><h5>Logo</h5></div>
            <div class="detail-image-container">
              <div class="skeleton-loader"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Documents section -->
      <h4>Dokumente</h4>
      <div class="col">
          <ul>
            <li><span class="skeleton-text" style="width: 180px; height: 16px;"></span></li>
          </ul>
      </div>

      <!-- Comments section -->
      <h3>Kommentare</h3>
      <div class="mt-2">
        <div class="skeleton-text" style="width: 100%; height: 60px; margin-bottom: 12px;"></div>
        <div class="skeleton-text" style="width: 100%; height: 60px;"></div>
      </div>

      <!-- Comment field -->
      <h4 class="mt-3">Dein Kommentar</h4>
      <div class="form-group">
        <div class="skeleton-text" style="width: 100%; height: 100px;"></div>
      </div>
    </section>
  `
})

const SongInfo = Vue.defineComponent({
    props: ['song', 'band'],
    emits: ['navigate-to-band'],
        template: `
        <div>
            <p><h5>Band</h5> <a :href="'#/bid/' + band.guid + '/'" @click.prevent="$emit('navigate-to-band', band)" class="band-link">{{ band.name || band.guid }}</a></p>
            <p><h5>Song</h5> {{ song.file_name_original }}</p>
        </div>
    `
})

const BandLinks = Vue.defineComponent({
    props: ['links'],
    template: `
    <div>
      <ul>
        <li v-for="link in links" :key="link.id">
          <a :href="link.url" target="_blank">{{ link.url }}</a>
        </li>
      </ul>
    </div>
  `
})

const BandDocuments = Vue.defineComponent({
    props: ['documents'],
    template: `
    <div>
      <ul>
        <li v-for="document in documents" :key="document.id">
          <a :href="document.file" target="_blank">{{ document.file_name_original }}</a>
        </li>
      </ul>
    </div>
  `
})

const BandImages = Vue.defineComponent({
    props: ['selectedBandDetails'],
    data() {
        return {
            pressPhotoLoaded: false,
            logoLoaded: false
        }
    },
    methods: {
        pressPhoto(band) {
            let file = band?.press_photo?.encoded_file || band?.press_photo?.file
            if (!file) {
                return window.rockon_data.placeholder
            }
            if (!file.endsWith('.webp')) {
                return window.rockon_data.media_offline
            }
            return file
        },
        logo(band) {
            let file = band?.logo?.encoded_file || band?.logo?.file
            if (!file) {
                return window.rockon_data.placeholder
            }
            if (!file.endsWith('.webp')) {
                return window.rockon_data.media_offline
            }
            return file
        },
        onPressPhotoLoad() {
            this.pressPhotoLoaded = true
        },
        onLogoLoad() {
            this.logoLoaded = true
        }
        ,
        _checkImageComplete() {
            try {
                const p = this.$refs.pressPhotoImg
                if (p && p.complete && p.naturalWidth > 0) {
                    this.pressPhotoLoaded = true
                }
                const l = this.$refs.logoImg
                if (l && l.complete && l.naturalWidth > 0) {
                    this.logoLoaded = true
                }
            } catch (e) {
                console.debug('checkImageComplete error', e)
            }
        }
    },
    watch: {
        selectedBandDetails() {
            // Reset loaded states when band changes
            this.pressPhotoLoaded = false
            this.logoLoaded = false
        }
    },
    template: `
    <div class="row gallery">
      <div v-if="selectedBandDetails.press_photo" class="col">
        <div><h5>Photo</h5></div>
        <a :href="selectedBandDetails.press_photo.file">
                        <div class="detail-image-container" :class="{ 'loaded': pressPhotoLoaded }">
                        <div v-if="!pressPhotoLoaded" class="skeleton-loader"></div>
                        <img ref="pressPhotoImg" :src="pressPhoto(selectedBandDetails)" :alt="selectedBandDetails.press_photo.encoded_file" class="detail-image" :class="{ 'loaded': pressPhotoLoaded }" @load="onPressPhotoLoad">
                    </div>
        </a>
      </div>
      <div v-if="selectedBandDetails.logo" class="col">
        <div><h5>Logo</h5></div>
        <a :href="selectedBandDetails.logo.file">
                        <div class="detail-image-container" :class="{ 'loaded': logoLoaded }">
                        <div v-if="!logoLoaded" class="skeleton-loader"></div>
                        <img ref="logoImg" :src="logo(selectedBandDetails)" :alt="selectedBandDetails.logo.encoded_file" class="detail-image" :class="{ 'loaded': logoLoaded }" @load="onLogoLoad">
                    </div>
        </a>
      </div>
    </div>
  `,
    mounted() {
        const options = {
            overlayOpacity: 0.4,
            history: false
        }
        const lightbox = new SimpleLightbox('.gallery a', options)
        console.debug('BandImages mounted lightbox:', lightbox)
        this.$nextTick(() => this._checkImageComplete())
    }

    ,
    updated() {
        // If the image was already loaded (from cache), ensure we update the flags
        this.$nextTick(() => this._checkImageComplete())
    }
})

const SongList = Vue.defineComponent({
    props: ['songs'],
    emits: ['select-song'],
    template: `
    <div>
      <ol>
        <li v-for="song in songs" :key="song.id" @click="handleSongClick(song)" style="cursor: pointer;">
          {{ song.file_name_original }}
        </li>
      </ol>
    </div>
  `,
    methods: {
        handleSongClick(song) {
            console.log('Clicked song:', song)
            this.$emit('select-song', song)
        }
    }
})

const TrackDropdown = Vue.defineComponent({
    props: ['tracks', 'selectedBandDetails'],
    emits: ['update:selectedTrack'],
    mounted() {
        console.debug(
            'TrackDropdown mounted:',
            this.tracks,
            this.selectedBandDetails.track
        )
    },
    template: `
    <div class="form-group">
      <label for="trackSelect" class="form-label">Track</label>
      <select id="trackSelect" @change="updateSelectedTrack" v-model="selectedBandDetails.track" class="form-control">
        <option v-if="!selectedBandDetails.track" disabled v-bind:value="null">Track auswählen</option>
        <option v-if="selectedBandDetails.track" value="">Track entfernen</option>
        <option v-for="track in tracks" :value="track.id" :key="track.id">
          {{ track.name || "Kein Track" }}
        </option>
      </select>
    </div>
  `,
    methods: {
        updateSelectedTrack(event) {
            console.debug('TrackDropdown updateSelectedTrack:', event.target.value)
            this.$emit('update:selectedTrack', event.target.value || null)
        }
    },
    watch: {
        currentTrackId(newVal) {
            console.log('Selected track:', newVal)
        }
    }
})

const BidStatusDropdown = Vue.defineComponent({
    props: ['bidStates', 'selectedBandDetails'],
    emits: ['update:bidStatus'],
    template: `
    <div class="form-group">
      <label for="bidStatusSelect" class="form-label">Status</label>
      <select id="bidStatusSelect" @change="updateBidStatus" v-model="selectedBandDetails.bid_status" class="form-control">
        <option v-for="(state, index) in bidStates" :key="index" :value="state[0]">
          {{ state[1] }}
        </option>
      </select>
    </div>
  `,
    methods: {
        updateBidStatus(event) {
            console.debug('BidStatusDropdown updateBidStatus:', event.target.value)
            this.$emit('update:bidStatus', event.target.value)
        }
    }
})

const BackstageLink = Vue.defineComponent({
    props: ['selectedBandDetails'],
    computed: {
        url() {
            return `/backstage/rockonbands/band/${this.selectedBandDetails.id}/change/`
        }
    },
    template: `
  <div class="form-group">
    <label for="backstageBtn" class="form-label">Backstage</label>
    <a id="backstageBtn" :href="url" class="btn btn-primary form-control" role="button">
      Band bearbeiten
    </a>
  </div>
  `
})

const TrackList = Vue.defineComponent({
    props: [
        'tracks',
        'bands',
        'selectedTrack',
        'selectedBand',
        'showBandNoName',
        'showIncompleteBids',
        'showDeclinedBids',
        'bidStates'
    ],
    emits: [
        'select-track',
        'filter-no-name',
        'filter-incomplete-bids',
        'filter-declined-bids'
    ],
    data() {
        return {
            isFilterCollapsed: FilterService.loadFromStorage('filterCollapsed', true)
        }
    },
    computed: {
        isSpecialFilter() {
            return ['no-track', 'no-vote', 'student-bands', 'under-27'].includes(this.selectedTrack) ||
                   (typeof this.selectedTrack === 'string' && this.selectedTrack.startsWith('status-'))
        },
        hasActiveSelection() {
            return this.selectedTrack || this.isSpecialFilter
        },
        selectedStatus() {
            // Extract the status value if a status filter is selected
            if (typeof this.selectedTrack === 'string' && this.selectedTrack.startsWith('status-')) {
                return this.selectedTrack.replace('status-', '')
            }
            return ''
        }
    },

    methods: {
        getTrackCount(track) {
            if (!this.bands) return 0
            // Apply the same visibility filters as the band list
            const visibleBands = FilterService.applyVisibilityFilters(this.bands, {
                showIncompleteBids: this.showIncompleteBids,
                showBandNoName: this.showBandNoName,
                showDeclinedBids: this.showDeclinedBids
            })
            return visibleBands.filter(band => band.track === track.id).length
        },
        handleClick(track) {
            console.debug('TrackList handleClick:', track)
            if (this.selectedBand) {
                this.$emit('select-track', track)
                return
            }

            if (this.selectedTrack === track) {
                this.$emit('select-track', null)
                return
            }
            this.$emit('select-track', track)
        },
        handleDeselectTrack() {
            console.debug('TrackList handleDeselectTrack')
            this.$emit('select-track', null)
        },
        toggleFilter(filterType) {
            console.debug('TrackList toggleFilter:', filterType)
            if (this.selectedBand) {
                this.$emit('select-track', filterType)
                return
            }

            // Toggle behavior: clicking active filter deselects it
            if (this.selectedTrack === filterType) {
                this.$emit('select-track', null)
            } else {
                this.$emit('select-track', filterType)
            }
        },
        handleFilterNoNameChange(event) {
            console.debug('TrackList handleFilterNoNameChange:', event.target.checked)
            this.$emit('filter-no-name', event.target.checked)
        },
        handleFilterIncompleteBids(event) {
            console.debug('TrackList handleFilterIncompleteBids:', event.target.checked)
            this.$emit('filter-incomplete-bids', event.target.checked)
            // If incomplete bids is turned off, also turn off show bands without names
            if (!event.target.checked && this.showBandNoName) {
                this.$emit('filter-no-name', false)
            }
        },
        handleFilterDeclinedBids(event) {
            console.debug('TrackList handleFilterDeclinedBids:', event.target.checked)
            this.$emit('filter-declined-bids', event.target.checked)
        },
        handleStatusChange(event) {
            const status = event.target.value
            console.debug('TrackList handleStatusChange:', status)
            if (status) {
                this.$emit('select-track', `status-${status}`)
            } else {
                this.$emit('select-track', null)
            }
        },
        toggleFilterCollapsed() {
            this.isFilterCollapsed = !this.isFilterCollapsed
            FilterService.saveToStorage('filterCollapsed', this.isFilterCollapsed)
        }
    },
    template: `
      <section class="row p-4 form-section">
        <div>
          <!-- Tracks Section -->
          <div class="d-flex align-items-center mb-2">
            <h5 class="mb-0 me-2"><i class="fas fa-music me-1"></i> Tracks</h5>
          </div>
          <div class="d-flex flex-wrap align-items-center mb-3">
            <span
              v-for="track in tracks"
              :key="track.id"
              class="badge m-1 filter-badge"
              :class="track === selectedTrack ? 'text-bg-success' : 'text-bg-primary'"
              style="cursor: pointer; transition: all 0.2s ease;"
              @click="handleClick(track)">
              <i v-if="track === selectedTrack" class="fas fa-check me-1"></i>
              {{ track.name }} <span class="badge bg-dark ms-1">{{ getTrackCount(track) }}</span>
            </span>
          </div>

          <!-- Quick Filters Section -->
          <div class="d-flex align-items-center mb-2">
            <h5 class="mb-0 me-2"><i class="fas fa-filter me-1"></i> Schnellfilter</h5>
          </div>
          <div class="d-flex flex-wrap align-items-center mb-3">
            <span
              class="badge m-1 filter-badge"
              :class="selectedTrack === 'no-track' ? 'text-bg-success' : 'text-bg-outline-primary'"
              style="cursor: pointer; transition: all 0.2s ease;"
              @click="toggleFilter('no-track')"
              title="Zeigt nur Bands ohne zugewiesenen Track">
              <i :class="selectedTrack === 'no-track' ? 'fas fa-check me-1' : 'fas fa-folder-open me-1'"></i>
              Ohne Track
            </span>
            <span
              class="badge m-1 filter-badge"
              :class="selectedTrack === 'no-vote' ? 'text-bg-success' : 'text-bg-outline-primary'"
              style="cursor: pointer; transition: all 0.2s ease;"
              @click="toggleFilter('no-vote')"
              title="Zeigt nur Bands die du noch nicht bewertet hast">
              <i :class="selectedTrack === 'no-vote' ? 'fas fa-check me-1' : 'fas fa-star-half-alt me-1'"></i>
              Unbewertete Bands
            </span>
            <span
              class="badge m-1 filter-badge"
              :class="selectedTrack === 'student-bands' ? 'text-bg-success' : 'text-bg-outline-primary'"
              style="cursor: pointer; transition: all 0.2s ease;"
              @click="toggleFilter('student-bands')"
              title="Zeigt nur Schülerbands">
              <i :class="selectedTrack === 'student-bands' ? 'fas fa-check me-1' : 'fas fa-graduation-cap me-1'"></i>
              Schülerbands
            </span>
                        <span
                            class="badge m-1 filter-badge"
                            :class="selectedTrack === 'under-27' ? 'text-bg-success' : 'text-bg-outline-primary'"
                            style="cursor: pointer; transition: all 0.2s ease;"
                            @click="toggleFilter('under-27')"
                            title="Zeigt nur Bands mit Durchschnittsalter unter 27">
                            <i :class="selectedTrack === 'under-27' ? 'fas fa-check me-1' : 'fas fa-calendar me-1'"></i>
                            Unter 27
                        </span>
            <select
              class="form-select form-select-sm d-inline-block m-1 status-filter-dropdown"
              :class="selectedStatus ? 'bg-success text-white border-success' : ''"
              style="width: auto; min-width: 150px;"
              :value="selectedStatus"
              @change="handleStatusChange"
              title="Filtere nach Bewerbungsstatus">
              <option value="">Status</option>
              <option v-for="state in bidStates" :key="state[0]" :value="state[0]">
                {{ state[1] }}
              </option>
            </select>
            <span
              v-if="hasActiveSelection"
              class="badge m-1 filter-badge text-bg-outline-primary"
              style="cursor: pointer;"
              @click="handleDeselectTrack"
              title="Alle Filter zurücksetzen">
              <i class="fas fa-times me-1"></i>
              Reset
            </span>
          </div>

          <!-- Toggle Filters Section -->
          <div class="d-flex align-items-center mb-2">
            <h5
              class="mb-0 me-2"
              style="cursor: pointer;"
              @click="toggleFilterCollapsed"
              title="Klicken zum Ein-/Ausklappen">
              <i :class="isFilterCollapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-down'" class="me-1"></i>
              <i class="fas fa-sliders-h me-1"></i> Anzeigeoptionen
            </h5>
          </div>
          <div v-show="!isFilterCollapsed" class="filter-options-container ps-2">
            <div class="form-check form-switch mb-2">
              <input
                class="form-check-input"
                type="checkbox"
                role="switch"
                id="filterIncompleteBids"
                :checked="showIncompleteBids"
                @change="handleFilterIncompleteBids" />
              <label class="form-check-label" for="filterIncompleteBids">
                <i class="fas fa-exclamation-triangle text-warning me-1"></i>
                Unvollständige Bewerbungen anzeigen
              </label>
            </div>
            <div class="form-check form-switch mb-2">
              <input
                class="form-check-input"
                type="checkbox"
                role="switch"
                id="filterNoName"
                :checked="showBandNoName"
                :disabled="!showIncompleteBids"
                @change="handleFilterNoNameChange" />
              <label class="form-check-label" for="filterNoName" :class="{'text-muted': !showIncompleteBids}">
                <i class="fas fa-question-circle me-1" :class="showIncompleteBids ? 'text-secondary' : 'text-muted'"></i>
                Bands ohne Namen anzeigen
              </label>
            </div>
            <div class="form-check form-switch mb-2">
              <input
                class="form-check-input"
                type="checkbox"
                role="switch"
                id="filterDeclinedBids"
                :checked="showDeclinedBids"
                @change="handleFilterDeclinedBids" />
              <label class="form-check-label" for="filterDeclinedBids">
                <i class="fas fa-ban text-danger me-1"></i>
                Abgelehnte Bewerbungen anzeigen
              </label>
            </div>
          </div>
        </div>
      </section>
    `,
    created() {
        console.debug('TrackList created. Initial showBandNoName:', this.showBandNoName)
    }
})

const BandTags = Vue.defineComponent({
    props: ['selectedBandDetails', 'federalStates'],
    computed: {
        federalStatesTag() {
            const federalState = this.federalStates.find(
                federalState =>
                    federalState[0] === this.selectedBandDetails.federal_state
            )
            return federalState ? federalState[1] : null
        }
    },
    init: function () {
        console.debug('BandTags init:', this.selectedBandDetails)
    },
    template: `
    <div style="user-select: none;">
      <span v-if="!selectedBandDetails.bid_complete" class="badge text-bg-warning m-1">Bewerbung unvollständig!</span>
      <span class="badge text-bg-primary m-1">{{ federalStatesTag }}</span>
      <span v-if="selectedBandDetails.has_management" class="badge text-bg-warning m-1">Management</span>
      <span v-if="!selectedBandDetails.has_management" class="badge text-bg-success m-1">Kein Management</span>
      <span v-if="selectedBandDetails.are_students" class="badge text-bg-success m-1">Schülerband</span>
      <span v-if="!selectedBandDetails.are_students" class="badge text-bg-primary m-1">Keine Schülerband</span>
      <span v-if="selectedBandDetails.mean_age_under_27" class="badge text-bg-success m-1">Unter 27</span>
      <span v-if="!selectedBandDetails.mean_age_under_27" class="badge text-bg-primary m-1">Über 27</span>
      <span v-if="selectedBandDetails.is_coverband" class="badge text-bg-warning m-1">Coverband</span>
      <span v-if="selectedBandDetails.repeated" class="badge text-bg-warning m-1">Wiederholer</span>
      <span v-if="!selectedBandDetails.repeated" class="badge text-bg-primary m-1">Neu</span>
      <span class="badge text-bg-primary m-1">{{ selectedBandDetails.genre || "Kein Gerne" }}</span>
      <span v-if="!selectedBandDetails.cover_letter" class="badge text-bg-warning m-1">Kein Coverletter</span>
      <span v-if="selectedBandDetails.bid_status === 'declined'" class="badge text-bg-warning m-1">Bewerbung abgelehnt</span>
    </div>
  `
})

const BandListTags = Vue.defineComponent({
    props: ['selectedBandDetails', 'federalStates', 'userVotes'],
    computed: {
        federalStatesTag() {
            const federalState = this.federalStates.find(
                federalState =>
                    federalState[0] === this.selectedBandDetails.federal_state
            )
            return federalState ? federalState[1] : null
        }
    },
    methods: {
        hasVote(band) {
            const userVote = this.userVotes.find(vote => vote.band__id === band.id)
            console.debug('BandList hasVote:', userVote)
            return userVote
        },
        voteCount(band) {
            return this.userVotes.find(vote => vote.band__id === band.id).vote
        }
    },
    init: function () {
        console.debug('BandTags init:', this.selectedBandDetails)
    },
    template: `
    <div>
      <span class="badge text-bg-primary m-1" style="cursor: pointer;">{{ federalStatesTag }}</span>
      <span v-if="hasVote(selectedBandDetails)" class="badge text-bg-success m-1" style="cursor: pointer;">Bewertet: {{ voteCount(selectedBandDetails) }} 💖</span>
      <span v-if="!hasVote(selectedBandDetails) && (selectedBandDetails.bid_status !== 'declined')" class="badge text-bg-secondary m-1" style="cursor: pointer;">Enthalten</span>
      <span v-if="selectedBandDetails.bid_status === 'declined'" class="badge text-bg-warning m-1" style="cursor: pointer;">Abgelehnt</span>
      <span v-if="selectedBandDetails.are_students" class="badge text-bg-success m-1" style="cursor: pointer;">Schülerband</span>
      <span v-if="selectedBandDetails.mean_age_under_27" class="badge text-bg-success m-1" style="cursor: pointer;">Unter 27</span>
      <span v-if="!selectedBandDetails.bid_complete" class="badge text-bg-warning m-1" style="cursor: pointer;">Bewerbung unvollständig!</span>
    </div>
  `
})

const BandList = Vue.defineComponent({
    props: [
        'bands',
        'selectedTrack',
        'showBandNoName',
        'showIncompleteBids',
        'showDeclinedBids',
        'federalStates',
        'userVotes'
    ],
    components: {BandListTags},
    emits: ['select-band'],
    computed: {
        filteredBands() {
            return FilterService.filterBands(this.bands, {
                filters: {
                    showIncompleteBids: this.showIncompleteBids,
                    showBandNoName: this.showBandNoName,
                    showDeclinedBids: this.showDeclinedBids
                },
                selectedTrack: this.selectedTrack,
                userVotes: this.userVotes
            })
        },
        isTrackFilter() {
            // Check if selectedTrack is an actual track object (has .id and .name)
            return this.selectedTrack && typeof this.selectedTrack === 'object' && this.selectedTrack.name
        },
        filterLabel() {
            if (!this.selectedTrack) return ''
            const count = this.filteredBands.length
            const singular = count === 1
            // Actual track
            if (this.isTrackFilter) return `in Track ${this.selectedTrack.name}`
            // Special filters
            const filterLabels = {
                'no-track': 'ohne Track',
                'no-vote': 'ohne Bewertung',
                'student-bands': singular ? 'ist Schülerband' : 'sind Schülerbands'
            }
            if (filterLabels[this.selectedTrack]) return filterLabels[this.selectedTrack]
            // Status filters
            if (typeof this.selectedTrack === 'string' && this.selectedTrack.startsWith('status-')) {
                const statusLabels = {
                    'status-unknown': 'mit Status Unbekannt',
                    'status-pending': 'mit Status Bearbeitung',
                    'status-accepted': 'mit Status Angenommen',
                    'status-declined': 'mit Status Abgelehnt'
                }
                return statusLabels[this.selectedTrack] || ''
            }
            return ''
        },
        // Flat list with indices for better lazy loading control
        filteredBandsWithIndex() {
            return this.filteredBands.map((band, index) => ({ band, index }))
        },
        groupedBands() {
            let groups = []
            for (let i = 0; i < this.filteredBandsWithIndex.length; i += 4) {
                groups.push(this.filteredBandsWithIndex.slice(i, i + 4))
            }
            return groups
        }
    },
    data() {
        return {
            selectedBand: null,
            bgColor: 'var(--rockon-card-bg)',
            imageCache: new Set(),
            loadedImages: {}
        }
    },
    methods: {
        selectBand(band) {
            console.debug('BandList selectBand:', band)
            this.$emit('select-band', band)
        },
        cardImage(band) {
            // Always return a valid src string for <img>
            let file = band?.press_photo?.encoded_file || band?.press_photo?.file;
            if (file && typeof file === 'string') {
                if (file.endsWith('.webp')) {
                    return file;
                } else {
                    return (window.rockon_data && window.rockon_data.media_offline) ? window.rockon_data.media_offline : '';
                }
            }
            // Fallback to placeholder if available, else empty string
            return (window.rockon_data && window.rockon_data.placeholder) ? window.rockon_data.placeholder : '';
        },
        hoverBand(band) {
            this.selectedBand = band
            this.bgColor = 'var(--rockon-secondary-text-emphasis)'
        },
        leaveBand(band) {
            if (this.selectedBand === band) {
                this.selectedBand = null
                this.bgColor = 'var(--rockon-card-bg)'
            }
        },
        onImageLoad(bandId) {
            this.loadedImages[bandId] = true
        },
        preloadImages() {
            // Preload first 12 images (3 rows) immediately
            const toPreload = this.filteredBands.slice(0, 12)
            toPreload.forEach(band => {
                const src = this.cardImage(band)
                if (src && !this.imageCache.has(src)) {
                    const img = new Image()
                    img.src = src
                    this.imageCache.add(src)
                }
            })
        }
    },
    watch: {
        filteredBands: {
            immediate: true,
            handler() {
                this.$nextTick(() => {
                    this.preloadImages()
                })
            }
        }
    },
    template: `
    <section class="row p-4 form-section">
    <div class="row">
      <h3>{{ filteredBands.length }} {{ filteredBands.length === 1 ? 'Band' : 'Bands' }} {{ filterLabel }}</h3>
    </div>
    <div v-if="groupedBands.length > 0" v-for="(group, groupIndex) in groupedBands" :key="'group-' + groupIndex">
      <div class="card-group">
        <div class="card" v-for="item in group" :key="item.band.id" :id="'band-' + item.band.id" @click="selectBand(item.band)" style="cursor: pointer; max-width: 312px; height: 380px" :style="{ backgroundColor: selectedBand === item.band ? bgColor : 'var(--rockon-card-bg)' }" @mouseover="hoverBand(item.band)" @mouseleave="leaveBand(item.band)">
          <div class="image-container">
            <div v-if="!loadedImages[item.band.id]" class="skeleton-loader"></div>
            <img :src="cardImage(item.band)" class="card-img-top img-fluid zoom-image" :class="{ 'loaded': loadedImages[item.band.id] }" style="height: 250px; object-fit: cover; object-position: center;" :alt="item.band.name || item.band.guid" :loading="item.index < 12 ? 'eager' : 'lazy'" decoding="async" fetchpriority="auto" @load="onImageLoad(item.band.id)">
          </div>
            <div class="card-body">
            <h6 class="card-title">{{ item.band.name || item.band.guid }}</h6>
            <BandListTags :selectedBandDetails="item.band" :federalStates="federalStates" :userVotes="userVotes" />
          </div>
        </div>
      </div>
    </div>
    </section>
  `
})

const BandRating = Vue.defineComponent({
    props: ['selectedBandDetails'],
    emits: ['update:rating'],
    template: `
    <i
      title="Daumen runter, 0 Sterne"
      class="fa-solid fa-thumbs-down m-2"
      @click="emitRating(0)"
      :class="{'highlight': isHovering == true}, {'highlight': rating == 0}"
      @mouseover="isHovering = true"
      @mouseleave="isHovering = false">
    </i>

    <i
      v-for="(star, index) in 5"
        :key="index"
        :index="index"
        @click="emitRating(index + 1)"
        class="fa-solid fa-star m-2"
        :class="{'highlight': hoverIndex >= index}, {'highlight': index < rating}"
        @mouseover="hoverIndex = index"
        @mouseleave="hoverIndex = -1">
    </i>
    <button class="btn btn-outline-primary" @click="emitRating(-1)">Enthaltung</button>
  `,
    data() {
        return {
            rating: null,
            hoverIndex: -1,
            isHovering: false
        }
    },
    methods: {
        emitRating(rating) {
            console.debug('BandRating emitRating:', rating)
            this.rating = rating
            this.$emit('update:rating', rating)
        },
        async fetchRating() {
            const url = window.rockon_api.fetch_rating.replace(
                'pk_placeholder',
                this.selectedBandDetails.id
            )
            console.debug('BandRating fetchRating:', url, this.selectedBandDetails.id)
            try {
                const response = await fetch(url)
                if (response.status === 204) {
                    console.debug('No rating found for band', this.selectedBandDetails.id)
                    return
                }
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`)
                }
                const data = await response.json()
                this.rating = data.vote
            } catch (error) {
                console.error('Error fetching rating:', error)
            }
        }
    },
    mounted() {
        this.fetchRating()
    }
})

const CommentFeed = Vue.defineComponent({
    props: ['commentApi', 'selectedBandDetails', 'newComment'],
    data() {
        return {
            comments: [],
            loading: true
        }
    },
    mounted() {
        this.fetchComments();
    },
    methods: {
        moodIcon(mood) {
            return mood === 'thumbs-up' ? 'fa-thumbs-up' : 'fa-thumbs-down'
        },
        modReason(reason) {
            return reason ? ' - ' + reason : ''
        },
        async fetchComments() {
            console.debug('CommentFeed fetchComments:', this.selectedBandDetails.id);
            try {
                const response = await fetch(`${this.commentApi}?band=${this.selectedBandDetails.id}`);
                if (response.ok) {
                    const apiResponse = await response.json();
                    this.comments = apiResponse.results;
                    console.debug('Fetched comments:', this.comments);
                } else {
                    console.error('Failed to fetch comments:', response.statusText);
                }
            } catch (error) {
                console.error('Error fetching comments:', error);
            } finally {
                this.loading = false;
            }
        },
        formatDate: Utils.formatDate,
    },
    template: `
    <div v-if="loading">Loading comments...</div>
    <div v-else v-for="comment in comments" :key="comment.id" class="comment mt-2 text-justify border-top border-primary border-opacity-50">
        <div><h5>{{ comment.user.first_name }} {{ comment.user.last_name }}</h5></div>
        <span class="text-muted">Zeit: {{ formatDate(comment.created_at) }}</span><br />
        <span>Stimmung: <i :class="'fa-solid ' + moodIcon(comment.mood)"></i>{{ modReason(comment.reason) }}</span>
        <p>Kommentar: {{ comment.text }}</p>
    </div>
    `,
    watch: {
        newComment(newVal) {
            if (newVal) {
                console.debug('CommentFeed reloadComments');
                this.comments = [];
                this.loading = true;
                this.fetchComments();
            }
        }
    }
})

const CommentField = Vue.defineComponent({
    props: ['commentApi', 'selectedBandDetails'],
    emits: ['update:comment'],
    data() {
        return {
            selectedMood: 'thumbs-up',
            selectedReason: '', // Default selected reason
            commentText: '', // Default comment text
            reasons: [
                {id: 1, text: 'Hatten wir schonmal'},
                {id: 2, text: 'Solokünstler'},
                {id: 3, text: 'Zu alt'},
                {id: 4, text: 'Zu jung'},
                {id: 5, text: 'Nazis/Schwurbler/Feindliche Gesinnungen'},
                {id: 6, text: 'Unpassend wie Coverband, DJ, keine handgemachte Musik'},
                {id: 7, text: 'Professionals'},
                {id: 8, text: 'Internationals'},
                {id: 9, text: 'Wollen Gage'},
            ]
        }
    },
    watch: {
        selectedMood(newVal) {
            if (newVal !== 'thumbs-down') {
                this.selectedReason = ''; // Reset the selected reason if thumbs-down is not selected
            }
        }
    },
    methods: {
        emitComment() {
            console.debug('CommentField emitComment:', this.selectedMood, this.selectedReason, this.commentText)
            const commentData = {
                mood: this.selectedMood,
                reason: this.selectedReason,
                text: this.commentText,
                band: this.selectedBandDetails.id,
            };

            // Post the comment to the API
            fetch(`${this.commentApi}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
                },
                body: JSON.stringify(commentData)
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.debug('Successfully posted comment:', data);
                    this.$emit('update:comment', commentData);
                    this.selectedMood = 'thumbs-up';
                    this.selectedReason = '';
                    this.commentText = '';
                })
                .catch(error => {
                    console.error('Error posting comment:', error);
                });
        },
        isButtonDisabled() {
            if (this.selectedMood === 'thumbs-up' && this.commentText.trim() !== '') {
                return false;
            }
            return !(this.selectedMood === 'thumbs-down' && this.selectedReason !== '' && this.commentText.trim() !== '');
        },
    },
    template: `
    <div class="form-group">
      <div class="row mb-2">
        <div class="col-auto">
          <input type="radio" class="btn-check" name="options" id="radio-thumbs-up" autocomplete="off" v-model="selectedMood" value="thumbs-up">
          <label :class="['btn', selectedMood === 'thumbs-up' ? 'btn-primary' : 'btn-secondary']" for="radio-thumbs-up">
            <i class="fa-solid fa-thumbs-up"></i>
          </label>
        </div>
        <div class="col-auto">
          <input type="radio" class="btn-check" name="options" id="radio-thumbs-down" autocomplete="off" v-model="selectedMood" value="thumbs-down">
          <label :class="['btn', selectedMood === 'thumbs-down' ? 'btn-primary' : 'btn-secondary']" for="radio-thumbs-down">
            <i class="fa-solid fa-thumbs-down"></i>
          </label>
        </div>
        <div class="col">
          <select class="form-select" aria-label="Begründung für negativen Kommentar" v-model="selectedReason" :disabled="selectedMood !== 'thumbs-down'">
            <option value="" selected>Wähle eine Begründung</option>
            <option v-for="reason in reasons" :key="reason.id" :value="reason.text">{{ reason.text }}</option>
          </select>
        </div>
      </div>
      <textarea id="comment" class="form-control" rows="4" v-model="commentText"></textarea>
      <button class="btn btn-primary mt-2" @click="emitComment" :disabled="isButtonDisabled()">Kommentar absenden</button>
    </div>
  `,
})

const BandDetails = Vue.defineComponent({
    props: [
        'tracks',
        'bidStates',
        'media',
        'federalStates',
        'selectedBandDetails',
        'currentTrackId',
        'allowChanges',
        'allowVotes',
        'commentApi',
        'filteredBands',
    ],
    emits: ['update:track', 'update:select-song', 'update:rating', 'navigate-to-band'],
    components: {
        TrackDropdown,
        BackstageLink,
        BidStatusDropdown,
        SongList,
        BandImages,
        BandDocuments,
        BandLinks,
        BandTags,
        BandRating,
        CommentFeed,
        CommentField
    },
    data() {
        return {
            newComment: null
        }
    },
    created() {
        console.debug('BandDetails created:', this.selectedBandDetails)
        console.debug('BandDetails created allowVotes:', this.allowVotes)
    },
    computed: {
        bandName() {
            if (!this.selectedBandDetails.name) {
                return this.selectedBandDetails.guid
            }
            return this.selectedBandDetails.name
        },
        trackId() {
            console.debug('BandDetails trackId:', this.selectedBandDetails.track)
            if (this.selectedBandDetails.track === null) {
                return 'null'
            }
            return this.selectedBandDetails.track
        },
        coverLetter() {
            if (!this.selectedBandDetails.cover_letter) {
                return 'Kein Cover Letter'
            }
            return this.selectedBandDetails.cover_letter.replace(/\r\n/g, '<br>')
        },
        isUnknownOrPending() {
            return this.selectedBandDetails.bid_status === 'unknown' || this.selectedBandDetails.bid_status === 'pending';
        },
        currentBandIndex() {
            if (!this.filteredBands || !this.selectedBandDetails) return -1
            return this.filteredBands.findIndex(b => b.id === this.selectedBandDetails.id)
        },
        previousBand() {
            if (this.currentBandIndex <= 0) return null
            return this.filteredBands[this.currentBandIndex - 1]
        },
        nextBand() {
            if (this.currentBandIndex < 0 || this.currentBandIndex >= this.filteredBands.length - 1) return null
            return this.filteredBands[this.currentBandIndex + 1]
        }
    },
    template: `
    <section :v-if="selectedBandDetails" id="band-detail" class="row p-4 form-section">
      <div class="col d-flex align-items-center justify-content-between">
          <button v-if="previousBand" @click="navigateToPrevious()" class="btn btn-nav-chevron me-3" :title="'Vorherige Band: ' + (previousBand.name || previousBand.guid)">
            <i class="fas fa-chevron-left me-2"></i>Vorherige
          </button>
          <button v-else class="btn btn-nav-chevron me-3" disabled style="visibility: hidden;">
            <i class="fas fa-chevron-left me-2"></i>Vorherige
          </button>
          <h3 class="mb-0 flex-grow-1 text-center">{{ bandName }}</h3>
          <button v-if="nextBand" @click="navigateToNext()" class="btn btn-nav-chevron ms-3" :title="'Nächste Band: ' + (nextBand.name || nextBand.guid)">
            Nächste<i class="fas fa-chevron-right ms-2"></i>
          </button>
          <button v-else class="btn btn-nav-chevron ms-3" disabled style="visibility: hidden;">
            Nächste<i class="fas fa-chevron-right ms-2"></i>
          </button>
      </div>
      <div v-if="isUnknownOrPending" class="row mt-2">
      <div class="col">
        <div class="alert alert-secondary" role="alert">
            <h4 class="alert-heading">Unbearbeitet</h4>
            <hr>
            <p>Diese Bewerbung wurde vom Band-Gewerk noch nicht gesichtet.</p>
            <p>Aus Transparenzgründen ist sie hier gelistet und du kannst ihre Tracks anhören, die Band kann aber nicht bewertet werden.</p>
        </div>
        </div>
      </div>
      <div v-if="selectedBandDetails.bid_status === 'declined'" class="row mt-2">
      <div class="col">
        <div class="alert alert-warning" role="alert">
            <h4 class="alert-heading">❌ Bewerbung abgelehnt ❌</h4>
            <hr>
            <p>Diese Band hat es leider in der Vorauswahl nicht geschafft und die organisatorischen Mindestanforderungen an eine Bewerbung erfüllt.</p>
            <p>Aus Transparenzgründen ist sie hier gelistet und du kannst ihre Tracks anhören, die Band kann aber nicht bewertet werden.</p>
        </div>
        </div>
      </div>
      <div class="row">
      <div class="col-9">
          <BandTags :selectedBandDetails="selectedBandDetails" :federalStates="federalStates" />
      </div>
      <div v-if="selectedBandDetails.bid_status === 'accepted' && allowVotes" class="col-3">
          <BandRating :selectedBandDetails="selectedBandDetails" @update:rating="emitRating" />
      </div>
      </div>
      <h3>Allgemeines</h3>
      <div class="row">
          <div class="col-12">
              <div v-html="coverLetter" class="alert alert-secondary" role="alert"></div>
          </div>
      </div>
      <div class="row">
          <div class="col">
              <div><h4>Web</h4></div>
              <BandLinks :links="selectedBandDetails.web_links" />
          </div>
      </div>
      <h3>Media</h3>
      <div class="col">
          <div><h4>Songs</h4></div>
          <SongList :songs="selectedBandDetails.songs" @select-song="handleSongSelect" />
      </div>
      <div class="col">
          <div><h4>Links</h4></div>
          <BandLinks :links="selectedBandDetails.links" />
      </div>
      <h4>Bilder</h4>
      <div class="col">
          <BandImages :selectedBandDetails="selectedBandDetails" />
      </div>
      <h4>Dokumente</h4>
      <div class="col">
          <BandDocuments :documents="selectedBandDetails.documents" />
      </div>
      <!-- feed start -->
      <h3>Kommentare</h3>
      <CommentFeed :comment-api="commentApi" :selectedBandDetails="selectedBandDetails" :new-comment="newComment" />
      <!-- feed end -->
      <!-- comment start -->
      <h4 class="mt-3">Dein Kommentar</h4>
      <CommentField :comment-api="commentApi" :selectedBandDetails="selectedBandDetails" @update:comment="handleNewComment" />
      <!-- comment end -->
      <!-- administrative section start -->
      <div v-if="allowChanges" class="mt-5">
      <h3>Verwaltung</h3>
      <div class="row">
        <div class="col-auto">
            <TrackDropdown :tracks="tracks" :selectedBandDetails="selectedBandDetails" :currentTrackId="currentTrackId" @update:selectedTrack="updateTrack" />
        </div>
        <div class="col-auto">
            <BidStatusDropdown :bidStates="bidStates" :selectedBandDetails="selectedBandDetails" @update:bidStatus="updateBidStatus" />
        </div>
        <div class="col-auto">
          <BackstageLink :selectedBandDetails="selectedBandDetails" />
        </div>
      </div>
      <h4 class="mt-2">Booking</h4>
      <div class="col-auto">
      <p>Name: {{ selectedBandDetails.contact.first_name || "Kein Vorname" }} {{ selectedBandDetails.contact.last_name || "Kein Nachname" }}</p>
      <p>E-Mail: <a :href="'mailto:' + selectedBandDetails.contact.email">{{ selectedBandDetails.contact.email }}</a></p>
      </div>
      <div class="col-auto">
      </div>
      <div class="col-auto">
      </div>
      <div class="row text-muted">
          <h5>Techniches Zeug</h5>
          <div class="col-auto">
          <p class="iso-datetime">Ertellt: {{ formatDate(selectedBandDetails.created_at) }}</p>
          <p class="iso-datetime">Aktuallisiert: {{ formatDate(selectedBandDetails.updated_at) }}</p>
          </div>
          <div class="col-auto">
          <p>Band ID: {{ selectedBandDetails.id }}</p>
          <p>Event ID: {{ selectedBandDetails.event }}</p>
          </div>
          <div class="col-auto">
          <p>Kontakt ID: {{ selectedBandDetails.contact.id }}</p>
          <p>Track ID: {{ trackId }}</p>
          </div>
      </div>
      </div>
    <!-- administrative section end -->
    </section>
  `,
    methods: {
        updateTrack(trackId) {
            console.debug('BandDetails updateTrack:', trackId)
            this.$emit('update:track', trackId)
        },
        handleNewComment(commentData) {
            console.debug('BandDetails emitComment:', commentData)
            this.newComment = commentData;
        },
        updateBidStatus(bidStatus) {
            console.debug('BandDetails updateBidStatus:', bidStatus)
            this.$emit('update:bidStatus', bidStatus)
        },
        handleSongSelect(song) {
            // Update the data with the selected song
            console.debug('BandDetails handleSongSelect:', song)
            this.$emit('update:select-song', song)
        },
        formatDate: Utils.formatDate,
        emitRating(rating) {
            console.debug('BandDetails emitRating:', rating)
            this.$emit('update:rating', rating)
        },
        navigateToPrevious() {
            if (this.previousBand) {
                this.$emit('navigate-to-band', this.previousBand)
            }
        },
        navigateToNext() {
            if (this.nextBand) {
                this.$emit('navigate-to-band', this.nextBand)
            }
        }
    },
})

const app = createApp({
    data() {
        return {
            bandListLoaded: false,
            bandsToFetch: null,
            eventSlug: window.rockon_data.event_slug,
            allowChanges: window.rockon_api.allow_changes,
            allowVotes: window.rockon_api.allow_votes,
            crsf_token: $('[name=csrfmiddlewaretoken]').val(),
            bandListUrl: window.rockon_api.list_bands,
            bandCommentsUrl: window.rockon_api.comments_api,
            tracks: window.rockon_data.tracks,
            bands: [],
            federalStates: window.rockon_data.federal_states,
            bidStates: window.rockon_data.bid_states,
            selectedTrack: null,
            selectedBand: null,
            userVotes: window.rockon_data.user_votes,
            selectedBandDetails: null,
            bandDetailLoaded: false,
            playSong: null,
            playSongBand: null,
            _wavePlaying: false,
            playerEndBehavior: 'next',
            toastAudioPlayer: null,
            toastVisible: false,
            toastIsMaximized: true,
            raccoonRadioPlaylist: [],
            playQueue: [],
            playQueueIndex: -1,
            wavesurfer: null,
            showBandNoName: null,
            showIncompleteBids: null,
            showDeclinedBids: null,
            BandRating: null,
            lightbox: null
            ,
            currentTime: 0,
            duration: 0,
            volume: 1
            ,
            volumePopupOpen: false,
            volumeDragging: false,
            // Numeric tooltip for the volume thumb and inactivity timer
            volumeTooltip: 100,
            volumeTooltipVisible: false,
            _volumePopupTimerId: null,
            _volumePopupTimeoutMs: 2500
        }
    },
    computed: {
        currentSongIndex() {
            // If a play queue is active, return its index
            if (this.playQueue && this.playQueue.length) return this.playQueueIndex
            if (!this.playSong || !this.playSongBand || !this.playSongBand.songs) return -1
            return this.playSongBand.songs.findIndex(s => s.id === this.playSong.id)
        },
        canPlayPrevious() {
            if (this.playQueue && this.playQueue.length) return this.playQueueIndex > 0
            return this.currentSongIndex > 0
        },
        canPlayNext() {
            if (this.playQueue && this.playQueue.length) return this.playQueueIndex < this.playQueue.length - 1
            if (!this.playSongBand || !this.playSongBand.songs) return false
            return this.currentSongIndex < this.playSongBand.songs.length - 1
        },
        isPlaying() {
            try {
                if (this._wavePlaying) return true
                if (!this.wavesurfer) return false
                if (typeof this.wavesurfer.isPlaying === 'function') return this.wavesurfer.isPlaying()
                // fallback: check currentTime vs duration
                const cur = typeof this.wavesurfer.getCurrentTime === 'function' ? this.wavesurfer.getCurrentTime() : 0
                const dur = typeof this.wavesurfer.getDuration === 'function' ? this.wavesurfer.getDuration() : 0
                return dur > 0 && cur < dur && !this.wavesurfer.paused
            } catch (e) {
                console.error('isPlaying check failed', e)
                return false
            }
        },
        playerEndIcon() {
            switch (this.playerEndBehavior) {
                case 'stop':
                    return 'fa-solid fa-stop'
                case 'loop-one':
                    return 'fa-solid fa-repeat'
                default:
                    return 'fa-solid fa-forward'
            }
        },
        playerEndTitle() {
            switch (this.playerEndBehavior) {
                case 'stop':
                    return 'Am Ende stoppen'
                case 'loop-one':
                    return 'Aktuellen Titel wiederholen'
                default:
                    return 'Nächsten Titel starten'
            }
        },
        filteredBands() {
            return FilterService.filterBands(this.bands, {
                filters: {
                    showIncompleteBids: this.showIncompleteBids,
                    showBandNoName: this.showBandNoName,
                    showDeclinedBids: this.showDeclinedBids
                },
                selectedTrack: this.selectedTrack,
                userVotes: this.userVotes
            })
        }
    },
    components: {
        TrackList,
        BandList,
        BandDetails,
        BandDetailsSkeleton,
        TrackDropdown,
        BidStatusDropdown,
        SongList,
        SongInfo,
        BandImages,
        BandDocuments,
        BandLinks,
        BandTags,
        BandListTags,
        BandRating,
        LoadingSpinner
    },
    created() {
        this.getBandList(this.bandListUrl, window.rockon_data.event_slug)
        // restore saved player behavior (stop | next | loop)
        try {
            const saved = sessionStorage.getItem('playerEndBehavior')
            if (saved) this.playerEndBehavior = saved
        } catch (e) {
            console.error('Could not read playerEndBehavior from sessionStorage', e)
        }
        window.addEventListener('popstate', this.handlePopState)
    },
    methods: {
        handlePopState(event) {
            const url = new URL(window.location.href)
            const hashSegments = url.hash.split('/').filter(segment => segment)
            const previousBandId = this.selectedBand?.id
            const shouldScrollToDetail = hashSegments.includes('bid') || window.location.hash.includes('/bid/')

            if (hashSegments.includes('status')) {
                const statusFilter = hashSegments[hashSegments.indexOf('status') + 1]
                // Map URL value back to internal filter name (status-unknown, status-pending, etc.)
                this.selectedTrack = `status-${statusFilter}`
                this.selectedBand = null
                this.selectedBandDetails = null
            } else if (hashSegments.includes('filter')) {
                const filterName = hashSegments[hashSegments.indexOf('filter') + 1]
                this.selectedTrack = filterName
                this.selectedBand = null
                this.selectedBandDetails = null
            } else if (hashSegments.includes('track')) {
                const trackSlug = hashSegments[hashSegments.indexOf('track') + 1]
                // Check if it's an old-style special filter URL or actual track
                if (['no-vote', 'no-track', 'student-bands', 'under-27'].includes(trackSlug)) {
                    this.selectedTrack = trackSlug
                } else {
                    this.selectedTrack = this.tracks.find(track => track.slug === trackSlug) || null
                }
                this.selectedBand = null
                this.selectedBandDetails = null
            } else if (hashSegments.includes('bid')) {
                const bandGuid = hashSegments[hashSegments.indexOf('bid') + 1]
                const band = this.bands.find(band => band.guid === bandGuid) || null
                this.selectedBand = band
                // Don't clear selectedTrack when viewing band details - keep the filter active
                this.selectedBandDetails = null
                if (band) {
                    // Scroll to band-detail anchor after DOM update
                    this.$nextTick(() => {
                        const detailElement = document.getElementById('band-detail')
                        if (detailElement && shouldScrollToDetail) {
                            this.scrollToElementById('band-detail', 'start')
                        }
                    })
                }
            } else {
                // No hash present - clear selections, don't restore from sessionStorage
                this.selectedTrack = null
                this.selectedBand = null
                this.selectedBandDetails = null
                // Clear sessionStorage to stay in sync
                sessionStorage.removeItem('selectedTrack')

                // Going back to list view - scroll to the previously selected band tile
                if (previousBandId) {
                    this.$nextTick(() => {
                        this.scrollToElementById(`band-${previousBandId}`, 'center')
                    })
                }
            }
        },
        // Scroll helper that accounts for a fixed navbar height so anchors aren't hidden.
        scrollToElementById(id, block = 'start') {
            const el = document.getElementById(id)
            if (!el) return
            const nav = document.querySelector('.navbar') || document.querySelector('nav') || document.getElementById('navbar')
            const navHeight = nav ? nav.getBoundingClientRect().height : 0
            const extra = 8
            if (block === 'center') {
                const rect = el.getBoundingClientRect()
                const top = rect.top + window.scrollY - (window.innerHeight / 2) + (rect.height / 2) - Math.round(navHeight / 2)
                window.scrollTo({top: Math.max(0, top - extra), behavior: 'auto'})
            } else {
                const top = el.getBoundingClientRect().top + window.scrollY - navHeight - extra
                window.scrollTo({top: Math.max(0, top), behavior: 'auto'})
            }
        },
        togglePlayerEndBehavior() {
            // cycle: stop -> next -> loop-one -> stop
            try {
                if (this.playerEndBehavior === 'stop') this.playerEndBehavior = 'next'
                else if (this.playerEndBehavior === 'next') this.playerEndBehavior = 'loop-one'
                else this.playerEndBehavior = 'stop'
                sessionStorage.setItem('playerEndBehavior', this.playerEndBehavior)
            } catch (e) {
                console.error('Failed to persist playerEndBehavior', e)
            }
        },
        togglePlayPause() {
            if (!this.wavesurfer) return
            try {
                if (typeof this.wavesurfer.isPlaying === 'function' ? this.wavesurfer.isPlaying() : this._wavePlaying) {
                    this.wavesurfer.pause()
                } else {
                    this.wavesurfer.play()
                }
            } catch (e) {
                console.error('togglePlayPause error', e)
            }
        },
        stopPlayback() {
            if (!this.wavesurfer) return
            try {
                if (typeof this.wavesurfer.stop === 'function') {
                    this.wavesurfer.stop()
                } else if (typeof this.wavesurfer.setTime === 'function') {
                    this.wavesurfer.setTime(0)
                    this.wavesurfer.pause && this.wavesurfer.pause()
                }
                this.currentTime = 0
                this._wavePlaying = false
            } catch (e) {
                console.error('stopPlayback error', e)
            }
        },
        toggleVolumePopup() {
            this.volumePopupOpen = !this.volumePopupOpen
            // show numeric tooltip when opening
            if (this.volumePopupOpen) {
                this.showVolumeTooltip(true)
                this.resetVolumePopupInactivityTimer()
            } else {
                this.clearVolumePopupInactivityTimer()
                this.volumeTooltipVisible = false
            }
        },
        startVolumeDrag(event) {
            if (!this.wavesurfer) return
            this.volumeDragging = true
            // capture pointer
            event.target.setPointerCapture && event.target.setPointerCapture(event.pointerId)
            this.handleVolumePointer(event)
            // attach global listeners
            document.addEventListener('pointermove', this.handleVolumePointer)
            document.addEventListener('pointerup', this.endVolumeDrag)
        },
        handleVolumePointer(event) {
            try {
                const track = event.currentTarget || document.elementFromPoint(event.clientX, event.clientY)
                // find the .volume-track element
                const trackEl = track.closest && track.closest('.volume-track') ? track.closest('.volume-track') : (track.querySelector ? track.querySelector('.volume-track') : null)
                if (!trackEl) return
                const rect = trackEl.getBoundingClientRect()
                // vertical from bottom
                const offset = rect.bottom - event.clientY
                const pct = Math.max(0, Math.min(1, offset / rect.height))
                this.volume = pct
                if (this.wavesurfer && typeof this.wavesurfer.setVolume === 'function') this.wavesurfer.setVolume(this.volume)
                try { sessionStorage.setItem('playerVolume', String(this.volume)) } catch (e) {}
                // update and show numeric tooltip, and reset inactivity timer
                this.volumeTooltip = Math.round(this.volume * 100)
                this.showVolumeTooltip()
                this.resetVolumePopupInactivityTimer()
            } catch (e) {
                console.error('handleVolumePointer error', e)
            }
        },
        endVolumeDrag(event) {
            this.volumeDragging = false
            try {
                document.removeEventListener('pointermove', this.handleVolumePointer)
                document.removeEventListener('pointerup', this.endVolumeDrag)
                // after finishing drag, hide tooltip shortly
                setTimeout(() => { try { this.volumeTooltipVisible = false } catch (e) {} }, 900)
            } catch (e) {}
        },
        onVolumeKeyDown(event) {
            if (event.key === 'ArrowUp' || event.key === 'ArrowRight') {
                this.volume = Math.min(1, this.volume + 0.05)
                this.setVolume()
                this.volumeTooltip = Math.round(this.volume * 100)
                this.showVolumeTooltip()
                this.resetVolumePopupInactivityTimer()
                event.preventDefault()
            } else if (event.key === 'ArrowDown' || event.key === 'ArrowLeft') {
                this.volume = Math.max(0, this.volume - 0.05)
                this.setVolume()
                this.volumeTooltip = Math.round(this.volume * 100)
                this.showVolumeTooltip()
                this.resetVolumePopupInactivityTimer()
                event.preventDefault()
            }
        },
        setVolume() {
            if (!this.wavesurfer) return
            try {
                if (typeof this.wavesurfer.setVolume === 'function') {
                    this.wavesurfer.setVolume(this.volume)
                }
                try { sessionStorage.setItem('playerVolume', String(this.volume)) } catch (e) {}
                // reflect in tooltip when programmatically setting volume
                this.volumeTooltip = Math.round(this.volume * 100)
                this.showVolumeTooltip()
                this.resetVolumePopupInactivityTimer()
            } catch (e) {
                console.error('setVolume error', e)
            }
        },

        // Show numeric tooltip next to the thumb. If immediate is true keep visible.
        showVolumeTooltip(immediate = false) {
            try {
                this.volumeTooltipVisible = true
                // keep value synced
                this.volumeTooltip = Math.round(this.volume * 100)
                if (!immediate) {
                    // hide after short delay unless user is actively dragging
                    clearTimeout(this._hideTooltipTimer)
                    this._hideTooltipTimer = setTimeout(() => {
                        try { if (!this.volumeDragging) this.volumeTooltipVisible = false } catch (e) {}
                    }, 900)
                }
            } catch (e) {
                console.error('showVolumeTooltip error', e)
            }
        },

        // Inactivity timer for the popup: close popup when no interaction
        resetVolumePopupInactivityTimer() {
            try {
                this.clearVolumePopupInactivityTimer()
                this._volumePopupTimerId = setTimeout(() => {
                    try {
                        this.volumePopupOpen = false
                        this.volumeTooltipVisible = false
                        this._volumePopupTimerId = null
                    } catch (e) { console.error('volume popup auto-close error', e) }
                }, this._volumePopupTimeoutMs)
            } catch (e) {
                console.error('resetVolumePopupInactivityTimer error', e)
            }
        },

        clearVolumePopupInactivityTimer() {
            try {
                if (this._volumePopupTimerId) {
                    clearTimeout(this._volumePopupTimerId)
                    this._volumePopupTimerId = null
                }
            } catch (e) {}
        },
        formatTime(sec) {
            try {
                sec = Number(sec) || 0
                const m = Math.floor(sec / 60)
                const s = Math.floor(sec % 60)
                return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
            } catch (e) {
                return '0:00'
            }
        },
        selectTrack(track) {
            this.selectedTrack = track
            console.debug('Selected track:', this.selectedTrack)
            this.selectedBand = null
            this.selectedBandDetails = null
            console.debug('Selected band:', this.selectedBand)
            const url = new URL(window.location.href)
            // Check for status filter (status-unknown, status-pending, etc.)
            if (typeof track === 'string' && track.startsWith('status-')) {
                const statusValue = track.replace('status-', '')
                url.hash = `#/status/${statusValue}/`
                sessionStorage.setItem('selectedTrack', JSON.stringify({type: 'status', value: statusValue}))
            } else if (track === 'no-vote') {
                url.hash = '#/filter/no-vote/'
                sessionStorage.setItem('selectedTrack', JSON.stringify({type: 'filter', value: 'no-vote'}))
            } else if (track === 'no-track') {
                url.hash = '#/filter/no-track/'
                sessionStorage.setItem('selectedTrack', JSON.stringify({type: 'filter', value: 'no-track'}))
            } else if (track === 'student-bands') {
                url.hash = '#/filter/student-bands/'
                sessionStorage.setItem('selectedTrack', JSON.stringify({type: 'filter', value: 'student-bands'}))
            } else if (track === 'under-27') {
                url.hash = '#/filter/under-27/'
                sessionStorage.setItem('selectedTrack', JSON.stringify({type: 'filter', value: 'under-27'}))
            } else if (track) {
                url.hash = `#/track/${track.slug}/`
                sessionStorage.setItem('selectedTrack', JSON.stringify({type: 'track', id: track.id}))
            } else {
                url.hash = ''
                sessionStorage.removeItem('selectedTrack')
            }
            window.history.pushState({}, '', url)
        },
        selectBand(band) {
            console.debug('app selectBand:', band)
            this.selectedBand = band
            sessionStorage.setItem('selectedBandId', band.id)
            console.debug('Selected band:', this.selectedBand)
            const url = new URL(window.location.href)
            url.hash = `#/bid/${band.guid}/`
            window.history.pushState({}, '', url)
            document.title = `${band.name || band.guid} - Bandbewertung`
            this.bandDetailLoaded = false
        },

        updateTrack(trackId) {
            api_url = window.rockon_api.update_band.replace(
                'pk_placeholder',
                this.selectedBandDetails.id
            )
            console.debug('app updateTrack:', trackId)
            const track = this.tracks.find(track => track.id === trackId) || null

            console.debug('app updateTrack find:', track)
            console.debug(
                'Selected band:',
                this.selectedBandDetails.id,
                trackId,
                api_url
            )
            fetch(api_url, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.crsf_token
                },
                body: JSON.stringify({
                    track: trackId
                })
            })
                .then(response => response.json())
                .then(data => console.log('Success:', data))
                .catch(error => console.error('Error:', error))
            this.selectedBand.track = trackId
            this.selectedBandDetails.track = trackId
            this.selectedTrack = track
        },
        updateBidStatus(bidStatus) {
            api_url = window.rockon_api.update_band.replace(
                'pk_placeholder',
                this.selectedBandDetails.id
            )
            console.debug(
                'Selected band:',
                this.selectedBandDetails.id,
                bidStatus,
                api_url
            )
            fetch(api_url, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.crsf_token
                },
                body: JSON.stringify({
                    bid_status: bidStatus
                })
            })
                .then(response => response.json())
                .then(data => console.log('Success:', data))
                .catch(error => console.error('Error:', error))
            // Update all references to ensure filters work correctly
            this.selectedBand.bid_status = bidStatus
            this.selectedBandDetails.bid_status = bidStatus
            // Also update the band in the main bands array
            const bandInList = this.bands.find(b => b.id === this.selectedBandDetails.id)
            if (bandInList) {
                bandInList.bid_status = bidStatus
            }
        },
        handleSongSelect(song) {
            console.debug('app handleSongSelect:', song)
            if (this.playSong && this.playSong.id === song.id) {
                console.debug(
                    'app handleSongSelect: Song already playing. Doing nothing.'
                )
                return
            }
            this.playSong = { ...song }
            // Store a deep copy of the band details to preserve songs array during navigation
            this.playSongBand = JSON.parse(JSON.stringify(this.selectedBandDetails))
            if (!this.toastVisible) {
                this.toastAudioPlayer.show()
                this.toastVisible = true
            }

            if (this.wavesurfer) {
                this.wavesurfer.destroy()
                this.wavesurfer = null
                this._wavePlaying = false
            }

            this.initWavesurferForSong(song)
        },
        initWavesurferForSong(song) {
            this.wavesurfer = WaveSurfer.create({
                container: document.getElementById('player-wrapper'),
                waveColor: '#fff300',
                progressColor: '#999400',
                normalize: false,
                splitChannels: false,
                dragToSeek: true,
                cursorWidth: 3,
                url: song.encoded_file || song.file,
                mediaControls: false,
                autoplay: true
            })

            // WaveSurfer ready: set duration and volume
            this.wavesurfer.on('ready', () => {
                try {
                    this.duration = typeof this.wavesurfer.getDuration === 'function' ? this.wavesurfer.getDuration() : 0
                    // restore previously selected volume
                    try {
                        const savedVol = sessionStorage.getItem('playerVolume')
                        if (savedVol !== null) this.volume = parseFloat(savedVol)
                    } catch (e) {}
                    if (typeof this.wavesurfer.setVolume === 'function') {
                        this.wavesurfer.setVolume(this.volume)
                    }
                } catch (e) {
                    console.error('ready handler error', e)
                }
            })

            // Update current time during playback
            this.wavesurfer.on('audioprocess', (time) => {
                try { this.currentTime = time } catch (e) {}
            })

            this.wavesurfer.on('finish', () => {
                try {
                    if (this.playerEndBehavior === 'stop') {
                        this._wavePlaying = false
                    } else if (this.playerEndBehavior === 'next') {
                        if (this.canPlayNext) {
                            this.playNextTrack()
                        } else {
                            this._wavePlaying = false
                        }
                    } else if (this.playerEndBehavior === 'loop-one') {
                        // restart same song
                        if (this.playSong) {
                            if (this.wavesurfer) {
                                if (typeof this.wavesurfer.setTime === 'function') {
                                    this.wavesurfer.setTime(0)
                                    this.wavesurfer.play && this.wavesurfer.play()
                                } else if (typeof this.wavesurfer.setCurrentTime === 'function') {
                                    this.wavesurfer.setCurrentTime(0)
                                    this.wavesurfer.play && this.wavesurfer.play()
                                } else {
                                    // fallback: reload the same track
                                    const first = this.playSongBand && this.playSongBand.songs ? this.playSongBand.songs.find(s => s.id === this.playSong.id) : null
                                    if (first) this.playTrackFromCurrentBand(first)
                                }
                            } else {
                                const first = this.playSongBand && this.playSongBand.songs ? this.playSongBand.songs.find(s => s.id === this.playSong.id) : null
                                if (first) this.playTrackFromCurrentBand(first)
                                else this._wavePlaying = false
                            }
                        } else {
                            this._wavePlaying = false
                        }
                    }
                } catch (e) {
                    console.error('finish handler error', e)
                    this._wavePlaying = false
                }
            })
            this.wavesurfer.on('play', () => { this._wavePlaying = true })
            this.wavesurfer.on('pause', () => { this._wavePlaying = false })
        },
        toggleIcon() {
            this.toastIsMaximized = !this.toastIsMaximized
        },
        playPreviousTrack() {
            if (!this.canPlayPrevious) return
            // If a queue is active, play previous from queue
            if (this.playQueue && this.playQueue.length) {
                this.playQueueIndex = Math.max(0, this.playQueueIndex - 1)
                this.playQueueTrack(this.playQueueIndex)
                return
            }
            const prevSong = this.playSongBand.songs[this.currentSongIndex - 1]
            this.playTrackFromCurrentBand(prevSong)
        },
        skipBack15() {
            if (!this.wavesurfer) return
            try {
                if (typeof this.wavesurfer.skip === 'function') {
                    this.wavesurfer.skip(-10)
                } else {
                    const cur = this.wavesurfer.getCurrentTime ? this.wavesurfer.getCurrentTime() : 0
                    const target = Math.max(0, cur - 10)
                    if (typeof this.wavesurfer.setTime === 'function') {
                        this.wavesurfer.setTime(target)
                    } else if (typeof this.wavesurfer.setCurrentTime === 'function') {
                        this.wavesurfer.setCurrentTime(target)
                    }
                }
            } catch (e) {
                console.error('skipBack15 error', e)
            }
        },
        skipForward15() {
            if (!this.wavesurfer) return
            try {
                if (typeof this.wavesurfer.skip === 'function') {
                    this.wavesurfer.skip(10)
                } else {
                    const cur = this.wavesurfer.getCurrentTime ? this.wavesurfer.getCurrentTime() : 0
                    const dur = this.wavesurfer.getDuration ? this.wavesurfer.getDuration() : Infinity
                    const target = Math.min(dur, cur + 10)
                    if (typeof this.wavesurfer.setTime === 'function') {
                        this.wavesurfer.setTime(target)
                    } else if (typeof this.wavesurfer.setCurrentTime === 'function') {
                        this.wavesurfer.setCurrentTime(target)
                    }
                }
            } catch (e) {
                console.error('skipForward15 error', e)
            }
        },
        playNextTrack() {
            if (!this.canPlayNext) return
            // If a queue is active, play next from queue
            if (this.playQueue && this.playQueue.length) {
                this.playQueueIndex = Math.min(this.playQueue.length - 1, this.playQueueIndex + 1)
                this.playQueueTrack(this.playQueueIndex)
                return
            }
            const nextSong = this.playSongBand.songs[this.currentSongIndex + 1]
            this.playTrackFromCurrentBand(nextSong)
        },
        raccoonRadioMode() {
            try {
                if (this.raccoonRadioPlaylist && this.raccoonRadioPlaylist.length) {
                    console.debug('Toggling off raccoon radio')
                    this.raccoonRadioPlaylist = []
                    if (this.playQueue && this.playQueue.length) {
                        this.playQueue = []
                        this.playQueueIndex = -1
                    }
                    return
                }
                const allSongs = []
                this.bands.forEach(band => {
                    if (band && band.songs && Array.isArray(band.songs)) {
                        band.songs.forEach(song => {
                            allSongs.push({
                                bandId: band.id,
                                bandName: band.name || band.guid || 'Unknown',
                                songName: song.file_name_original || song.file || 'Track',
                                id: song.id,
                                songObj: song,
                            })
                        })
                    }
                })

                if (allSongs.length === 0) {
                    // clear playlist if nothing available
                    this.raccoonRadioPlaylist = []
                    return
                }

                // Shuffle using Fisher-Yates
                for (let i = allSongs.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1))
                    const tmp = allSongs[i]
                    allSongs[i] = allSongs[j]
                    allSongs[j] = tmp
                }

                const selected = allSongs.slice(0, Math.min(10, allSongs.length))
                // Display-friendly playlist with band photo/logo for artwork
                this.raccoonRadioPlaylist = selected.map(s => {
                    // Try to get band object from bands list for artwork
                    let band = this.bands.find(b => b.id === s.bandId) || {};
                    let pressPhoto = band.press_photo?.encoded_file || band.press_photo?.file || null;
                    let logo = band.logo?.encoded_file || band.logo?.file || null;
                    // Fallbacks for artwork
                    if (!pressPhoto || typeof pressPhoto !== 'string') pressPhoto = (window.rockon_data && window.rockon_data.placeholder) ? window.rockon_data.placeholder : '';
                    if (!logo || typeof logo !== 'string') logo = (window.rockon_data && window.rockon_data.placeholder) ? window.rockon_data.placeholder : '';
                    return {
                        bandName: s.bandName,
                        songName: s.songName,
                        id: s.id,
                        bandPressPhoto: pressPhoto,
                        bandLogo: logo
                    };
                })
                // Build playQueue with full song objects and band info, replacing any current queue
                this.playQueue = selected.map(s => ({ song: s.songObj, bandId: s.bandId, bandName: s.bandName }))
                this.playQueueIndex = 0
                // Start playback from the first queued track
                this.playQueueTrack(0)
            } catch (e) {
                console.error('raccoonRadioMode error', e)
            }
        },
        playTrackFromCurrentBand(song) {
            // Play a track from the already stored playSongBand (don't overwrite band info)
            if (this.playSong && this.playSong.id === song.id) {
                return
            }
            this.playSong = { ...song }

            if (this.wavesurfer) {
                this.wavesurfer.destroy()
                this.wavesurfer = null
            }

            this.initWavesurferForSong(song)
        },
        playQueueTrack(index) {
            try {
                if (!this.playQueue || !this.playQueue.length || index < 0 || index >= this.playQueue.length) return
                const entry = this.playQueue[index]
                const song = entry.song
                // Set the playSong and playSongBand for UI consistency
                this.playSong = { ...song }
                this.playSongBand = { id: entry.bandId || null, name: entry.bandName || null, songs: [song] }

                // show toast if hidden
                if (!this.toastVisible && this.toastAudioPlayer) {
                    this.toastAudioPlayer.show()
                    this.toastVisible = true
                }

                if (this.wavesurfer) {
                    this.wavesurfer.destroy()
                    this.wavesurfer = null
                    this._wavePlaying = false
                }

                this.initWavesurferForSong(song)
            } catch (e) {
                console.error('playQueueTrack error', e)
            }
        },
        playQueueStartAt(index) {
            try {
                if (!this.playQueue || !this.playQueue.length) return
                this.playQueueIndex = index
                this.playQueueTrack(index)
                // If few tracks remain, append more
                const remaining = this.playQueue.length - (this.playQueueIndex + 1)
                if (remaining <= 3) {
                    this.appendRandomToQueue(10)
                }
            } catch (e) {
                console.error('playQueueStartAt error', e)
            }
        },

        getAllSongEntries() {
            const entries = []
            this.bands.forEach(band => {
                if (band && band.songs && Array.isArray(band.songs)) {
                    band.songs.forEach(song => {
                        entries.push({
                            bandId: band.id,
                            bandName: band.name || band.guid || 'Unknown',
                            songName: song.file_name_original || song.file || 'Track',
                            id: song.id,
                            songObj: song,
                        })
                    })
                }
            })
            return entries
        },

        appendRandomToQueue(count = 10) {
            try {
                const candidates = this.getAllSongEntries()
                if (!candidates.length) return
                // Exclude already queued ids
                const existingIds = new Set((this.playQueue || []).map(e => e.song && e.song.id))
                const pool = candidates.filter(e => !existingIds.has(e.id))
                if (!pool.length) return
                // Shuffle pool
                for (let i = pool.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1))
                    const tmp = pool[i]
                    pool[i] = pool[j]
                    pool[j] = tmp
                }
                const picked = pool.slice(0, Math.min(count, pool.length))
                // Append to playQueue and display playlist
                picked.forEach(p => {
                    this.playQueue.push({ song: p.songObj, bandId: p.bandId, bandName: p.bandName })
                    // Determine artwork for the appended item (match raccoonRadioMode)
                    let band = this.bands.find(b => b.id === p.bandId) || {}
                    let pressPhoto = band.press_photo?.encoded_file || band.press_photo?.file || null
                    let logo = band.logo?.encoded_file || band.logo?.file || null
                    if (!pressPhoto || typeof pressPhoto !== 'string') pressPhoto = (window.rockon_data && window.rockon_data.placeholder) ? window.rockon_data.placeholder : ''
                    if (!logo || typeof logo !== 'string') logo = (window.rockon_data && window.rockon_data.placeholder) ? window.rockon_data.placeholder : ''
                    this.raccoonRadioPlaylist.push({ bandName: p.bandName, songName: p.songName, id: p.id, bandPressPhoto: pressPhoto, bandLogo: logo })
                })
            } catch (e) {
                console.error('appendRandomToQueue error', e)
            }
        },
        handleCloseClick() {
            console.debug('app handleCloseClick')
            console.log('this.wavesurfer:', this.wavesurfer)
            if (this.wavesurfer) {
                this.wavesurfer.destroy()
                this.wavesurfer = null
                this._wavePlaying = false
            }
            this.playSong = null
            this.playSongBand = null
            this.toastVisible = false
            this.toastIsMaximized = true
            try {
                if (this.raccoonRadioPlaylist && this.raccoonRadioPlaylist.length) {
                    console.debug('Disabling raccoon radio because player toast closed')
                    this.raccoonRadioPlaylist = []
                }
                if (this.playQueue && this.playQueue.length) {
                    this.playQueue = []
                    this.playQueueIndex = -1
                }
            } catch (e) {
                console.error('Error clearing raccoon radio/queue on close', e)
            }
        },
        navigateToPlayingBand() {
            if (!this.playSongBand) return
            console.debug('app navigateToPlayingBand:', this.playSongBand)
            let band = null
            if (this.playSongBand.id != null) {
                band = this.bands.find(b => b.id === this.playSongBand.id)
            }
            if (!band && this.playSongBand.guid) {
                band = this.bands.find(b => b.guid === this.playSongBand.guid)
            }
            if (band) {
                this.selectBand(band)
                return
            }

            if (this.playSongBand.guid) {
                const url = new URL(window.location.href)
                url.hash = `#/bid/${this.playSongBand.guid}/`
                window.history.pushState({}, '', url)
                document.title = `${this.playSongBand.name || this.playSongBand.guid} - Bandbewertung`
                try {
                    this.handlePopState()
                } catch (e) {
                    console.error('navigateToPlayingBand handlePopState error', e)
                }
                if (!this.selectedBand && this.playSongBand) {
                    try {
                        this.selectedBandDetails = JSON.parse(JSON.stringify(this.playSongBand))
                        this.bandDetailLoaded = true
                        this.$nextTick(() => {
                            const detailElement = document.getElementById('band-detail')
                            if (detailElement) this.scrollToElementById('band-detail', 'start')
                        })
                    } catch (e) {
                        console.error('navigateToPlayingBand fallback error', e)
                    }
                }
            }
        },
        handleFilterShowBandNoNameChange(checked) {
            FilterService.saveToStorage('showBandNoName', checked)
            this.showBandNoName = checked
        },
        handleFilterIncompleteBidsChange(checked) {
            FilterService.saveToStorage('showIncompleteBids', checked)
            this.showIncompleteBids = checked
        },
        handleFilterDeclinedBidsChange(checked) {
            FilterService.saveToStorage('showDeclinedBids', checked)
            this.showDeclinedBids = checked
        },
        setRating(rating) {
            console.debug('BandRating setRating:', rating)
            this.rating = rating
            api_url = window.rockon_api.band_vote
            console.debug('BandRating setRating:', this.selectedBand, rating, api_url)
            fetch(api_url, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.crsf_token
                },
                body: JSON.stringify({
                    band: this.selectedBand.id,
                    vote: rating
                })
            })
                .then(response => response)
                .then(data => {
                    console.log('Success:', data)
                })
                .catch(error => {
                    console.error('Error:', error)
                    alert('Fehler beim Speichern der Bewertung, bitte schrei um Hilfe!')
                })
            if (rating === -1) {
                this.userVotes = this.userVotes.filter(
                    vote => vote !== this.selectedBand.id
                )
            } else {
                this.userVotes.push({band__id: this.selectedBand.id, vote: rating})
            }
        },
        getBandList(url, _event = null) {
            console.debug('app getBandList:', url, _event)
            if (_event) {
                url = url + `?event=${_event}`
            }
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    console.debug('app getBandList:', data)
                    this.bands = [...this.bands, ...data.results]
                    this.bandsToFetch = data.count
                    if (data.next) {
                        this.getBandList(data.next)
                    } else {
                        this.bandListLoaded = true
                        console.debug('app getBandList:', this.bands)
                        this.handlePopState()
                    }
                })
                .catch(error => console.error('Error:', error))
        },
        getBandDetails(selectedBandId) {
            url = window.rockon_api.update_band.replace(
                'pk_placeholder',
                selectedBandId
            )
            console.debug('App getBandDetails:', url)
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    console.debug('App getBandDetails:', data)
                    this.selectedBandDetails = data
                    this.bandDetailLoaded = true
                })
                .catch(error => {
                    console.error('Error:', error)
                })
        }
    },
    mounted() {
        console.debug('Mounted function called')
        window.addEventListener('popstate', this.handlePopState)
        const toastAudioPlayerElement = document.getElementById('toastAudioPlayer')
        const toastAudioPlayer = bootstrap.Toast.getOrCreateInstance(
            toastAudioPlayerElement
        )
        bootstrap.Toast.getOrCreateInstance(toastAudioPlayer)
        this.toastAudioPlayer = toastAudioPlayer

        this.showBandNoName = FilterService.loadFromStorage('showBandNoName', false)
        this.showIncompleteBids = FilterService.loadFromStorage('showIncompleteBids', false)
        this.showDeclinedBids = FilterService.loadFromStorage('showDeclinedBids', false)

        const savedTrackData = sessionStorage.getItem('selectedTrack')
        if (savedTrackData) {
            try {
                const trackData = JSON.parse(savedTrackData)
                if (trackData.type === 'status') {
                    this.selectedTrack = `status-${trackData.value}`
                } else if (trackData.type === 'filter') {
                    this.selectedTrack = trackData.value
                } else if (trackData.type === 'track') {
                    const track = this.tracks.find(t => t.id === trackData.id)
                    this.selectedTrack = track || null
                }
            } catch (e) {
                console.error('Error parsing savedTrackData:', e)
                sessionStorage.removeItem('selectedTrack')
            }
        }

        this.handlePopState()

        // Restore selected band from sessionStorage if it exists
        const savedBandId = sessionStorage.getItem('selectedBandId')
        if (savedBandId && this.bands.length > 0) {
            const band = this.bands.find(b => b.id === parseInt(savedBandId))
            if (band) {
                this.selectedBand = band
                document.title = `${band.name || band.guid} - Bandbewertung`
            }
        }
    },
    beforeDestroy() {
        window.removeEventListener('popstate', this.handlePopState)
    },
    watch: {
        selectedBand: {
            immediate: true,
            handler(newValue, oldValue) {
                console.log('watch selectedBand changed:', newValue)
                // Fetch details if we don't have any, or if the currently
                // loaded details don't match the newly selected band.
                if (newValue) {
                    const needFetch = !this.selectedBandDetails || (this.selectedBandDetails.id !== newValue.id)
                    if (needFetch) {
                        // Don't set to null when navigating - just fetch and update
                        // This prevents unmounting the component which causes jumps
                        const isNavigating = oldValue && this.selectedBandDetails
                        if (!isNavigating) {
                            this.selectedBandDetails = null
                        }
                        this.bandDetailLoaded = false
                        this.getBandDetails(newValue.id)
                    }
                }
            }
        },
        selectedBandDetails: {
            immediate: true,
            handler(newValue, oldValue) {
                console.log('watch selectedBandDetails changed:', newValue)
                // Only scroll if we're coming from a non-detail view (oldValue is null/undefined)
                // When navigating between band details, don't auto-scroll
                if (newValue && !oldValue) {
                    this.$nextTick(() => {
                        const detailElement = document.getElementById('band-detail')
                        if (detailElement && (window.location.hash.includes('/bid/') || this.selectedBand)) {
                            this.scrollToElementById('band-detail', 'start')
                        }
                    })
                }
            }
        },
        showBandNoName: {
            immediate: true,
            handler(newValue, oldValue) {
                console.log('watch showBandNoName changed:', newValue)
            }
        }
    }
})
app.mount('#app')
