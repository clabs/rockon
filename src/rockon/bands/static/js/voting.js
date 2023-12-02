const { createApp, ref } = Vue

const UnorderedList = Vue.defineComponent({
  props: ['items'],
  template: `
    <ul>
      <li v-for="item in items" :key="item">{{ item.name||item.guid }}</li>
    </ul>
  `
})

const TrackList = Vue.defineComponent({
  props: ['tracks'],
  emits: ['select-track'],
  template: `
    <ul>
      <li v-for="track in tracks" :key="track">
        <a href="#" @click.prevent="handleClick(track)">{{ track.name }}</a>
      </li>
    </ul>
  `,
  methods: {
    handleClick (track) {
      this.$emit('select-track', track)
      this.logTrackId(track.id)
    },
    logTrackId (id) {
      console.debug(`Track ID: ${id}`)
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
        console.debug('No selected track id. Returning nothing.')
        return null
      }
      const filtered = this.bands.filter(
        band => band.track_id === this.selectedTrack.id
      )
      console.debug('Filtered bands:', filtered)
      return filtered
    }
  },
  methods: {
    selectBand (band) {
      console.debug('BandList selectBand:', band)
      this.$emit('select-band', band)
    }
  },
  template: `
    <ul>
      <li v-for="band in filteredBands" :key="band"><a href="#" @click.prevent="selectBand(band)">{{ band.name||band.guid }}</a></li>
    </ul>
  `
})

const BandDetails = Vue.defineComponent({
  props: ['selectedBand'],
  template: `
    <div v-if="selectedBand">
      <h2>{{ selectedBand.name||selectedBand.guid }}</h2>
      <p>{{ selectedBand.description }}</p>
    </div>
  `,
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
      message: 'Hello Vue!',
      tracks: window.rockon_data.tracks,
      bands: window.rockon_data.bands,
      selectedTrack: window.rockon_data.selectedTrack,
      selectedBand: window.rockon_data.selectedBand
    }
  },
  components: {
    UnorderedList,
    TrackList,
    BandList,
    BandDetails
  },
  methods: {
    selectTrack (track) {
      this.selectedTrack = track
      console.debug('Selected track:', this.selectedTrack)
      this.selectedBand = null
      console.debug('Selected band:', this.selectedBand)
      const url = new URL(window.location.href)
      url.pathname = `/bands/vote/${track.slug}/`
      window.history.pushState({}, '', url)
    },
    selectBand (band) {
      console.debug('app selectBand:', band)
      this.selectedBand = band
      console.debug('Selected band:', this.selectedBand)
      const url = new URL(window.location.href)
      url.pathname = `/bands/vote/${this.selectedTrack.slug}/${band.guid}/`
      window.history.pushState({}, '', url)
    }
  },
  mounted () {
    console.debug('Mounted function called')
    const url = new URL(window.location.href)
    const pathSegments = url.pathname.split('/').filter(segment => segment)

    const voteIndex = pathSegments.indexOf('vote')

    console.debug('Vote index:', voteIndex)

    if (voteIndex !== -1) {
      const segmentsAfterVote = pathSegments.slice(voteIndex + 1)

      console.debug('Segments after vote:', segmentsAfterVote)

      if (segmentsAfterVote.length <= 2) {
        const track_slug = segmentsAfterVote[0]
        const band_guid = segmentsAfterVote[1]

        console.debug('Track ID:', track_slug)
        console.debug('Band ID:', band_guid)

        if (track_slug) {
          const track = this.tracks.find(track => track.slug === track_slug)
          this.selectedTrack = track
          console.debug('Selected track:', this.selectedTrack)
        }

        if (band_guid) {
          const band = this.bands.find(band => band.guid === band_guid)
          if (band) {
            this.selectedBand = band
            console.debug('Selected band:', this.selectedBand)
          }
        }
      }
    }
  }
})
app.mount('#app')
