const { createApp, ref } = Vue

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
    updateSelectedTrack(event) {
      console.debug('TrackDropdown updateSelectedTrack:', event.target.value)
      this.$emit('update:selectedTrack', event.target.value || null);
    }
  },
  watch: {
    currentTrackId(newVal) {
      const selectedTrack = this.tracks.find(track => track.id === newVal);
      console.log('Selected track:', selectedTrack);
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
    groupedBands() {
      let groups = [];
      for (let i = 0; i < this.filteredBands.length; i += 4) {
        groups.push(this.filteredBands.slice(i, i + 4));
      }
      return groups;
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
  props: ['selectedBand', 'tracks'],
  emits: ['update:track'],
  components: { TrackDropdown },
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
      <TrackDropdown :tracks="tracks" :currentTrackId="selectedBand.track_id" @update:selectedTrack="updateTrack" />
    </div>
  `,
  methods: {
    updateTrack(trackId) {
      console.debug('BandDetails updateTrack:', trackId)
      this.$emit('update:track', trackId);
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
      tracks: window.rockon_data.tracks,
      bands: window.rockon_data.bands,
      selectedTrack: window.rockon_data.selectedTrack,
      selectedBand: window.rockon_data.selectedBand,
      currentTrackId: null,
    }
  },
  components: {
    TrackList,
    BandList,
    BandDetails,
    TrackDropdown
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
      window.history.pushState({}, '', url)
    },
    selectBand (band) {
      console.debug('app selectBand:', band)
      this.selectedBand = band
      this.currentTrackId = band.track_id
      console.debug('Selected band:', this.selectedBand)
      const url = new URL(window.location.href)
      url.pathname = `/bands/vote/bid/${band.guid}/`
      window.history.pushState({}, '', url)
    },
    updateTrack(trackId) {
      api_url = window.rockon_api.update_band.replace("pk_placeholder", this.selectedBand.id)
      console.debug('app updateTrack:', trackId)
      this.selectedBand.track_id = trackId;
      this.currentTrackId = trackId;
      console.debug('Selected band:', this.selectedBand.id, this.currentTrackId, api_url)
      fetch(api_url, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.crsf_token
        },
        body: JSON.stringify({
          band: this.selectedBand,
          track: trackId,
        }),
      })
      .then(response => response.json())
      .then(data => console.log('Success:', data))
      .catch((error) => console.error('Error:', error));
    },
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
