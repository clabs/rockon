const { createApp, ref } = Vue

const DateTime = luxon.DateTime

const SongInfo = Vue.defineComponent({
  props: ['song', 'band'],
  template: `
    <div>
      <p><h5>Band</h5> {{ band.name }}</p>
      <p><h5>Song</h5> {{ song.file_name_original }}</p>
    </div>
  `
})

const BandLinks = Vue.defineComponent({
  props: ['selectedBand', 'links'],
  computed: {
    filteredLinks () {
      console.debug(
        'BandLinks computed filtering for:',
        this.selectedBand,
        this.links
      )
      const filtered_links = this.links.filter(
        link => link.band_id === this.selectedBand.id
      )
      console.debug('BandLinks computed filtered_links:', filtered_links)
      return filtered_links
    }
  },
  template: `
    <div>
      <ul>
        <li v-for="link in filteredLinks" :key="link.id">
          <a :href="link.url" target="_blank">{{ link.url }}</a>
        </li>
      </ul>
    </div>
  `
})

const BandDocuments = Vue.defineComponent({
  props: ['bandDocuments', 'selectedBand', 'mediaUrl'],
  computed: {
    filteredBandDocuments () {
      console.debug(
        'BandDocuments computed filtering for:',
        this.selectedBand,
        this.bandDocuments
      )
      const filtered_band_documents = this.bandDocuments.filter(
        document => document.band_id === this.selectedBand.id
      )
      console.debug(
        'BandDocuments computed filtered_band_documents:',
        filtered_band_documents
      )
      return filtered_band_documents
    }
  },
  template: `
    <div>
      <ul>
        <li v-for="document in filteredBandDocuments" :key="document.id">
          <a :href="mediaUrl + document.file" target="_blank">{{ document.file_name_original }}</a>
        </li>
      </ul>
    </div>
  `
})

const BandImages = Vue.defineComponent({
  props: ['bandPhotos', 'bandLogos', 'selectedBand', 'mediaUrl'],
  computed: {
    currentBandPhoto () {
      console.debug('BandImages computed bandPhotos:', this.bandPhotos)
      const filteredBandPhotos = this.bandPhotos.filter(
        photo => photo.band_id === this.selectedBand.id
      )
      console.debug(
        'BandImages computed filteredBandPhotos:',
        filteredBandPhotos
      )
      return filteredBandPhotos[filteredBandPhotos.length - 1]
    },
    currentBandLogo () {
      console.debug('BandImages computed bandLogos:', this.bandLogos)
      const filteredBandLogos = this.bandLogos.filter(
        logo => logo.band_id === this.selectedBand.id
      )
      console.debug('BandImages computed filteredBandLogos:', filteredBandLogos)
      return filteredBandLogos[filteredBandLogos.length - 1]
    }
  },
  template: `
    <div class="row gallery">
      <div v-if="currentBandPhoto" class="col">
        <div><h5>Photo</h5></div>
        <a :href="mediaUrl + currentBandPhoto.file">
        <img :src="mediaUrl + currentBandPhoto.file" class="img-thumbnail" :alt="mediaUrl + currentBandPhoto.file" style="max-height: 250px;">
        </a>
      </div>
      <div v-if="currentBandLogo" class="col">
        <div><h5>Logo</h5></div>
        <a :href="mediaUrl + currentBandLogo.file">
        <img :src="mediaUrl + currentBandLogo.file" class="img-thumbnail" :alt="mediaUrl + currentBandLogo.file" style="max-height: 250px;">
        </a>
      </div>
    </div>
  `,
  mounted () {
    const options = {
      overlayOpacity: 0.2
    }
    const lightbox = new SimpleLightbox('.gallery a', options)
    console.debug('BandImages mounted lightbox:', lightbox)
  }
})

const SongList = Vue.defineComponent({
  props: ['songs', 'selectedBand'],
  emits: ['select-song'],
  computed: {
    filteredSongs () {
      console.debug(
        'SongList computed filtering for:',
        this.selectedBand,
        this.songs
      )
      const filtered_songs = this.songs.filter(
        song => song.band_id === this.selectedBand.id
      )
      console.debug('SongList:', filtered_songs)
      return filtered_songs
    }
  },
  template: `
    <div>
      <ol>
        <li v-for="song in filteredSongs" :key="song.id" @click="handleSongClick(song)" style="cursor: pointer;">
          {{ song.file_name_original }}
        </li>
      </ol>
    </div>
  `,
  methods: {
    handleSongClick (song) {
      console.log('Clicked song:', song)
      this.$emit('select-song', song)
    }
  }
})

const TrackDropdown = Vue.defineComponent({
  props: ['tracks', 'currentTrackId'],
  emits: ['update:selectedTrack'],
  template: `
    <div>
    <select @change="updateSelectedTrack" :value="currentTrackId" v-model="currentTrackId">
      <option value="">Track entfernen</option>
      <option v-for="track in tracks" :value="track.id" :key="track.id">
        {{ track.name }}
      </option>
    </select>
    </div>
  `,
  methods: {
    updateSelectedTrack (event) {
      console.debug('TrackDropdown updateSelectedTrack:', event.target.value)
      this.$emit('update:selectedTrack', event.target.value || null)
    }
  },
  watch: {
    currentTrackId (newVal) {
      const selectedTrack = this.tracks.find(track => track.id === newVal)
      console.log('Selected track:', selectedTrack)
    }
  }
})

const TrackList = Vue.defineComponent({
  props: ['tracks', 'selectedTrack', 'showBandNoName'],
  emits: ['select-track', 'filter-no-name'],
  computed: {
    showBandNoNameComputed () {
      return this.showBandNoName
    }
  },
  template: `
      <section class="row p-4 form-section">
      <div>
        <span v-for="track in tracks" :key="track" class="badge m-2" :class="track === selectedTrack ? 'text-bg-success' : 'text-bg-primary'" @click="handleClick(track)">{{ track.name }}</span>
        <span class="badge text-bg-primary m-2" :key="no-track" @click="handleShowBandsWithoutTrack">Ohne Track</span>
        <span class="badge text-bg-secondary m-2" @click="handleDeselectTrack">Filter entfernen</span>
        <div class="form-check form-switch m-2">
          <input class="form-check-input" type="checkbox" role="switch" :checked="showBandNoName" @change="handleFilterNoNameChange" />
          <label class="form-check-label" >Bands ohne Namen verstecken</label>
        </div>
      </div>
      </section>
    `,
  methods: {
    handleClick (track) {
      console.debug('TrackList handleClick:', track)
      this.selectedTrack = track
      this.$emit('select-track', track)
    },
    handleDeselectTrack () {
      console.debug('TrackList handleDeselectTrack')
      this.selectedTrack = null
      this.$emit('select-track', null)
    },
    handleShowBandsWithoutTrack () {
      console.debug('TrackList handleShowBandsWithoutTrack')
      this.selectedTrack = 'no-track'
      this.$emit('select-track', 'no-track')
    },
    handleFilterNoNameChange (event) {
      console.debug('TrackList handleFilterNoNameChange:', event.target.checked)
      this.showBandNoName = event.target.checked
      this.$emit('filter-no-name', event.target.checked)
    }
  },
  created () {
    console.log(
      'Component created. Initial value of showBandNoName:',
      this.showBandNoName
    )
  }
})

const BandList = Vue.defineComponent({
  props: ['bands', 'selectedTrack', 'showBandNoName'],
  emits: ['select-band'],
  computed: {
    filteredBands () {
      console.debug('selectedTrack:', this.selectedTrack)
      _bands = this.bands
      if (this.showBandNoName) {
        console.debug('Filtering for bands without a name.')
        _bands = _bands.filter(band => band.name)
      }
      if (!this.selectedTrack) {
        console.debug('No selected track id. Returning all.')
        return _bands
      }
      if (this.selectedTrack === 'no-track') {
        console.debug('Filtering for bands without a track.')
        return _bands.filter(band => !band.track_id)
      }
      const filtered = _bands.filter(
        band => band.track_id === this.selectedTrack.id
      )
      console.debug('Filtered bands:', filtered)
      return filtered
    },
    groupedBands () {
      let groups = []
      for (let i = 0; i < this.filteredBands.length; i += 4) {
        groups.push(this.filteredBands.slice(i, i + 4))
      }
      return groups
    }
  },
  methods: {
    selectBand (band) {
      console.debug('BandList selectBand:', band)
      this.$emit('select-band', band)
    }
  },
  template: `
    <section v-if="groupedBands.length > 0" class="row p-4 form-section">
      <div v-for="(group, index) in groupedBands" :key="index">
        <ul class="list-group list-group-horizontal d-flex justify-content-start">
          <li class="list-group-item col" v-for="band in group" :key="band" @click="selectBand(band)" style="cursor: pointer;">
            <span>{{ band.name||band.guid }}</span>
          </li>
        </ul>
      </div>
    </section>
  `
})

const BandTags = Vue.defineComponent({
  props: ['selectedBand', 'federalStates'],
  computed: {
    federalStatesTag () {
      console.debug('BandTags computed federalStatesTag:', this.federalStates)
      const federalState = this.federalStates.find(
        federalState => federalState[0] === this.selectedBand.federal_state
      )
      console.debug('BandTags computed federalState:', federalState)
      return federalState ? federalState[1] : null
    }
  },
  template: `
    <div>
      <span class="badge text-bg-primary m-1">{{ federalStatesTag }}</span>
      <span v-if="selectedBand.has_management" class="badge text-bg-warning m-1">Management</span>
      <span v-if="!selectedBand.has_management" class="badge text-bg-success m-1">Kein Management</span>
      <span v-if="selectedBand.are_students" class="badge text-bg-warning m-1">Schülerband</span>
      <span v-if="!selectedBand.are_students" class="badge text-bg-primary m-1">Keine Schülerband</span>
      <span v-if="selectedBand.repeated" class="badge text-bg-warning m-1">Wiederholer</span>
      <span v-if="!selectedBand.repeated" class="badge text-bg-primary m-1">Neu</span>
      <span class="badge text-bg-primary m-1">{{ selectedBand.genre || "Kein Gerne" }}</span>
      <span v-if="!selectedBand.cover_letter" class="badge text-bg-warning m-1">Kein Coverletter</span>
      <span v-if="!selectedBand.homepage" class="badge text-bg-warning m-1">Keine Homepage</span>
    </div>
  `
})

const BandRating = Vue.defineComponent({
  props: ['selectedBand'],
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
  data () {
    return {
      rating: null,
      hoverIndex: -1,
      isHovering: false
    }
  },
  methods: {
    emitRating (rating) {
      console.debug('BandRating emitRating:', rating)
      this.rating = rating
      this.$emit('update:rating', rating)
    },
    async fetchRating () {
      const url = window.rockon_api.fetch_rating.replace(
        'pk_placeholder',
        this.selectedBand.id
      )
      console.debug('BandRating fetchRating:', url, this.selectedBand.id)
      try {
        const response = await fetch(url)
        if (response.status === 404) {
          console.debug('No rating found for band', this.selectedBand.id)
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
  mounted () {
    this.fetchRating()
  }
  // watch: {
  //   hoverIndex (newVal) {
  //     console.debug('BandRating hoverIndex changed:', newVal)
  //   }
  // }
})

const BandDetails = Vue.defineComponent({
  props: ['selectedBand', 'tracks', 'media', 'mediaUrl', 'federalStates'],
  emits: ['update:track', 'update:select-song', 'update:rating'],
  components: {
    TrackDropdown,
    SongList,
    BandImages,
    BandDocuments,
    BandLinks,
    BandTags,
    BandRating
  },
  template: `
    <section class="row p-4 form-section">
      <div class="row">
        <div class="col">
        <h3>{{ selectedBand.name||selectedBand.guid }}</h3>
        </div>
      </div>
      <div class="row">
        <div class="col-9">
          <BandTags :selectedBand="selectedBand" :federalStates="federalStates" />
        </div>
        <div class="col-3">
          <BandRating :selectedBand="selectedBand" @update:rating="emitRating" />
        </div>
      </div>
      <div class="row">
        <h3>Allgemeines</h3>
        <div class="col">
          <div class="alert alert-secondary" role="alert">
            {{ selectedBand.cover_letter || "Kein Cover Letter" }}
          </div>
        </div>
        <div class="row mb-2">
          <div class="col">
            <div v-if="selectedBand.homepage">
              <div><h5>Homepage</h5></div>
              <a :href="selectedBand.homepage" target="_blank">{{ selectedBand.homepage }}</a>
            </div>
          </div>
          <div class="col">
            <div v-if="selectedBand.facebook">
              <div><h5>Facebook</h5></div>
              <a :href="selectedBand.facebook" target="_blank">{{ selectedBand.facebook }}</a>
            </div>
          </div>
        </div>
      </div>
      <div class="row">
        <h3>Media</h3>
        <div class="col">
          <div><h4>Songs</h4></div>
          <SongList :songs="media[2]" :selectedBand="selectedBand" @select-song="handleSongSelect" />
        </div>
        <div class="col">
          <div><h4>Links</h4></div>
          <BandLinks :selectedBand="selectedBand" :links="media[3]" />
        </div>
      </div>
      <div class="row">
        <h4>Bilder</h4>
        <div class="col">
        <BandImages :selectedBand="selectedBand" :bandPhotos="media[4]" :bandLogos="media[5]" :media-url="mediaUrl"/>
        </div>
      </div>
      <div class="row">
        <h4>Dokumente</h4>
        <div class="col">
        <BandDocuments :selectedBand="selectedBand" :bandDocuments="media[1]" :media-url="mediaUrl"/>
        </div>
      </div>
      <div class="row mb-2">
        <h3>Track</h3>
        <div class="col">
        <TrackDropdown :tracks="tracks" :currentTrackId="selectedBand.track_id" @update:selectedTrack="updateTrack" />
        </div>
      </div>
      <div class="row text-muted">
        <h5>Techniches Zeug</h5>
        <div class="col">
          <p class="iso-datetime">Ertellt: {{ formatDate(selectedBand.created_at) }}</p>
          <p class="iso-datetime">Aktuallisiert: {{ formatDate(selectedBand.updated_at) }}</p>
        </div>
        <div class="col">
          <p>Band ID: {{ selectedBand.id }}</p>
          <p>Event ID: {{ selectedBand.event_id }}</p>
        </div>
        <div class="col">
          <p>Kontakt ID: {{ selectedBand.contact_id }}</p>
          <p>Track ID: {{ selectedBand.track_id }}</p>
        </div>
      </div>
    </section>
  `,
  methods: {
    updateTrack (trackId) {
      console.debug('BandDetails updateTrack:', trackId)
      this.$emit('update:track', trackId)
    },
    handleSongSelect (song) {
      // Update the data with the selected song
      console.debug('BandDetails handleSongSelect:', song)
      this.$emit('update:select-song', song)
    },
    formatDate (isoString) {
      console.debug('BandDetails formatDate:', isoString)
      return DateTime.fromISO(isoString).toFormat('dd.MM.yyyy, HH:mm')
    },
    emitRating (rating) {
      console.debug('BandDetails emitRating:', rating)
      this.$emit('update:rating', rating)
    }
  },
  watch: {
    selectedBand (newVal) {
      console.debug('BandDetails selectedBand changed:', newVal)
    }
  }
})

const app = createApp({
  // setup() {
  //   const message = ref('Hello vue!')
  //   return {
  //     message
  //   }
  // },
  data () {
    return {
      crsf_token: $('[name=csrfmiddlewaretoken]').val(),
      mediaUrl: window.rockon_data.media_url,
      tracks: window.rockon_data.tracks,
      bands: window.rockon_data.bands,
      media: window.rockon_data.media,
      federalStates: window.rockon_data.federal_states,
      selectedTrack: null,
      selectedBand: null,
      currentTrackId: null,
      playSong: null,
      playSongBand: null,
      toastAudioPlayer: null,
      toastVisible: false,
      wavesurfer: null,
      showBandNoName: true,
      BandRating: null,
      lightbox: null
    }
  },
  components: {
    TrackList,
    BandList,
    BandDetails,
    TrackDropdown,
    SongList,
    SongInfo,
    BandImages,
    BandDocuments,
    BandLinks,
    BandTags,
    BandRating
  },
  methods: {
    selectTrack (track) {
      this.selectedTrack = track
      console.debug('Selected track:', this.selectedTrack)
      this.selectedBand = null
      this.currentTrackId = null
      console.debug('Selected band:', this.selectedBand)
      const url = new URL(window.location.href)
      if (track) {
        url.pathname = `/bands/vote/track/${track.slug}/`
      } else {
        url.pathname = `/bands/vote/`
      }
      window.history.replaceState({}, '', url)
    },
    selectBand (band) {
      console.debug('app selectBand:', band)
      this.selectedBand = band
      this.currentTrackId = band.track_id
      console.debug('Selected band:', this.selectedBand)
      const url = new URL(window.location.href)
      url.pathname = `/bands/vote/bid/${band.guid}/`
      window.history.replaceState({}, '', url)
    },
    updateTrack (trackId) {
      api_url = window.rockon_api.update_band.replace(
        'pk_placeholder',
        this.selectedBand.id
      )
      console.debug('app updateTrack:', trackId)
      this.selectedBand.track_id = trackId
      this.currentTrackId = trackId
      console.debug(
        'Selected band:',
        this.selectedBand.id,
        this.currentTrackId,
        api_url
      )
      fetch(api_url, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.crsf_token
        },
        body: JSON.stringify({
          band: this.selectedBand,
          track: trackId
        })
      })
        .then(response => response.json())
        .then(data => console.log('Success:', data))
        .catch(error => console.error('Error:', error))
    },
    updateComponent () {
      console.debug('Mounted function called')
      const url = new URL(window.location.href)
      const pathSegments = url.pathname.split('/').filter(segment => segment)

      if (pathSegments.includes('vote')) {
        const voteType = pathSegments[pathSegments.indexOf('vote') + 1]
        const id = pathSegments[pathSegments.indexOf('vote') + 2]

        console.debug('Vote type:', voteType)
        console.debug('ID:', id)

        if (voteType === 'track') {
          const track = this.tracks.find(track => track.slug === id)
          this.selectedTrack = track
          this.$emit('update:selectedTrack', track)
          console.debug('Selected track:', this.selectedTrack)
        }

        if (voteType === 'bid') {
          const band = this.bands.find(band => band.guid === id)
          if (band) {
            this.selectedBand = band
            this.$emit('update:selectedBand', band)
            console.debug('Selected band:', this.selectedBand)
          }
        }
      }
    },
    handleSongSelect (song) {
      console.debug('app handleSongSelect:', song)
      if (this.playSong === song) {
        console.debug(
          'app handleSongSelect: Song already playing. Doing nothing.'
        )
        return
      }
      this.playSong = song
      this.playSongBand = this.bands.find(band => band.id === song.band_id)
      if (!this.toastVisible) {
        this.toastAudioPlayer.show()
        this.toastVisible = true
      }

      if (this.wavesurfer) {
        this.wavesurfer.destroy()
        this.wavesurfer = null
      }

      this.playSong = song
      this.playSongBand = this.bands.find(band => band.id === song.band_id)

      this.wavesurfer = WaveSurfer.create({
        container: document.getElementById('player-wrapper'),
        waveColor: '#fff300',
        progressColor: '#999400',
        normalize: false,
        splitChannels: false,
        dragToSeek: true,
        cursorWidth: 3,
        url: this.mediaUrl + song.file,
        mediaControls: true,
        autoplay: true
      })
    },
    handleCloseClick () {
      console.debug('app handleCloseClick')
      console.log('this.wavesurfer:', this.wavesurfer)
      if (this.wavesurfer) {
        this.wavesurfer.destroy()
        this.wavesurfer = null
      }
      this.playSong = null
      this.playSongBand = null
      this.toastVisible = false
    },
    handleFilterShowBandNoNameChange (checked) {
      console.debug('app handleFilterShowBandNoNameChange:', checked)
      this.showBandNoName = checked
    },
    setRating (rating) {
      console.debug('BandRating setRating:', rating)
      this.rating = rating
      // TODO: Save rating to backend
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
        .then(data => console.log('Success:', data))
        .catch(error => console.error('Error:', error))
    }
  },
  mounted () {
    window.addEventListener('popstate', this.updateComponent)
    const toastAudioPlayerElement = document.getElementById('toastAudioPlayer')
    const toastAudioPlayer = bootstrap.Toast.getOrCreateInstance(
      toastAudioPlayerElement
    )
    bootstrap.Toast.getOrCreateInstance(toastAudioPlayer)
    this.toastAudioPlayer = toastAudioPlayer
    this.updateComponent()
  },
  beforeUnmount () {
    window.removeEventListener('popstate', this.updateComponent)
  },
  watch: {
    selectedBand: {
      immediate: true,
      handler (newValue, oldValue) {
        console.log('watch selectedBand changed:', newValue)
      }
    },
    showBandNoName: {
      immediate: true,
      handler (newValue, oldValue) {
        console.log('watch showBandNoName changed:', newValue)
      }
    }
  }
})
app.mount('#app')
