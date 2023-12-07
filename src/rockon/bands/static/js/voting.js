const { createApp, ref } = Vue

const SongInfo = Vue.defineComponent({
  props: ['song', 'band'],
  template: `
    <div>
      <p><h5>Band</h5> {{ band.name }}</p>
      <p><h5>Song</h5> {{ song.file_name_original }}</p>
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
    <div class="row">
      <div class="col">
        <div><h5>Photo</h5></div>
        <img :src="mediaUrl + currentBandPhoto.file" class="img-thumbnail" :alt="mediaUrl + currentBandPhoto.file" style="max-width: 300px;">
      </div>
      <div class="col">
        <div><h5>Logo</h5></div>
        <img :src="mediaUrl + currentBandLogo.file" class="img-thumbnail" :alt="mediaUrl + currentBandLogo.file" style="max-width: 300px;">
      </div>
    </div>
  `
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
    <ul>
      <li v-for="song in filteredSongs" :key="song.id" @click="handleSongClick(song)">
        {{ song.file_name_original }}
      </li>
    </ul>
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
    <select @change="updateSelectedTrack" :value="currentTrackId">
      <option value="">Track entfernen</option>
      <option v-for="track in tracks" :value="track.id" :key="track.id">
        {{ track.name }}
      </option>
    </select>
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
  props: ['tracks'],
  emits: ['select-track'],
  template: `
      <a href="#" class="badge text-bg-secondary m-3" @click.prevent="handleDeselectTrack">Filter entfernen</a>
      <a v-for="track in tracks" :key="track" class="badge text-bg-primary m-3" href="#" @click.prevent="handleClick(track)">{{ track.name }}</a>
    `,
  methods: {
    handleClick (track) {
      console.debug('TrackList handleClick:', track)
      this.$emit('select-track', track)
    },
    handleDeselectTrack () {
      console.debug('TrackList handleDeselectTrack')
      this.$emit('select-track', null)
    }
  }
})

const BandList = Vue.defineComponent({
  props: ['bands', 'selectedTrack'],
  emits: ['select-band'],
  computed: {
    filteredBands () {
      console.debug('selectedTrack:', this.selectedTrack)
      if (!this.selectedTrack) {
        console.debug('No selected track id. Returning all.')
        return this.bands
      }
      const filtered = this.bands.filter(
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
    <div v-for="(group, index) in groupedBands" :key="index">
      <ul class="list-group list-group-horizontal d-flex justify-content-start">
        <li class="list-group-item col" v-for="band in group" :key="band">
          <a href="#" @click.prevent="selectBand(band)">{{ band.name||band.guid }}</a>
        </li>
      </ul>
    </div>
  `
})

const BandDetails = Vue.defineComponent({
  props: ['selectedBand', 'tracks', 'media', 'mediaUrl'],
  emits: ['update:track', 'update:select-song'],
  components: { TrackDropdown, SongList, BandImages },
  template: `
    <div v-if="selectedBand">
      <h2>{{ selectedBand.name||selectedBand.guid }}</h2>
      <p>Genre: {{ selectedBand.genre }}</p>
      <p>State: {{ selectedBand.federal_state }}</p>
      <p>Homepage: <a :href="selectedBand.homepage" target="_blank">{{ selectedBand.homepage }}</a></p>
      <p>Cover Letter: {{ selectedBand.cover_letter }}</p>
      <p>Status: {{ selectedBand.bid_status }}</p>
      <p>Has Management: {{ selectedBand.has_management }}</p>
      <p>Are Students: {{ selectedBand.are_students }}</p>
      <p>Repeated: {{ selectedBand.repeated }}</p>
      <p>Created At: {{ selectedBand.created_at }}</p>
      <p>Updated At: {{ selectedBand.updated_at }}</p>
      <p>ID: {{ selectedBand.id }}</p>
      <p>Event ID: {{ selectedBand.event_id }}</p>
      <p>Contact ID: {{ selectedBand.contact_id }}</p>
      <p>Track ID: {{ selectedBand.track_id }}</p>
      <div><h3>Media</h3><div>
      <div><h4>Songs</h4><div>
      <div><SongList :songs="media[2]" :selectedBand="selectedBand" @select-song="handleSongSelect" /></div>
      <div><h4>Bilder</h4><div>
      <div><BandImages :selectedBand="selectedBand" :bandPhotos="media[4]" :bandLogos="media[5]" :media-url="mediaUrl"/></div>
      <h3>Track</h3>
      <p><TrackDropdown :tracks="tracks" :currentTrackId="selectedBand.track_id" @update:selectedTrack="updateTrack" /></p>
    </div>
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
      selectedTrack: null,
      selectedBand: null,
      currentTrackId: null,
      playSong: null,
      playSongBand: null,
      toastAudioPlayer: null,
      toastVisible: false,
      wavesurfer: null
    }
  },
  components: {
    TrackList,
    BandList,
    BandDetails,
    TrackDropdown,
    SongList,
    SongInfo,
    BandImages
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
        console.log('selectedBand changed:', newValue)
      }
    }
  }
})
app.mount('#app')
