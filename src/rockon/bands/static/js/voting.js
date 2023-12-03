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
      if (track) {
        url.pathname = `/bands/vote/track/${track.slug}/`
      } else {
        url.pathname = `/bands/vote/`
      }
      window.history.pushState({}, '', url)
    },
    selectBand (band) {
      console.debug('app selectBand:', band)
      this.selectedBand = band
      console.debug('Selected band:', this.selectedBand)
      const url = new URL(window.location.href)
      url.pathname = `/bands/vote/bid/${band.guid}/`
      window.history.pushState({}, '', url)
    }
  },
  mounted () {
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
        console.debug('Selected track:', this.selectedTrack)
      }

      if (voteType === 'bid') {
        const band = this.bands.find(band => band.guid === id)
        if (band) {
          this.selectedBand = band
          console.debug('Selected band:', this.selectedBand)
        }
      }
    }
  }
})
app.mount('#app')
