const { createApp, ref } = Vue

const DateTime = luxon.DateTime

const LoadingSpinner = Vue.defineComponent({
  props: ['bands', 'bandsToFetch'],
  computed: {
    progress () {
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

const SongInfo = Vue.defineComponent({
  props: ['song', 'band'],
  template: `
    <div>
      <p><h5>Band</h5> {{ band.name || band.guid }}</p>
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
  methods: {
    pressPhoto (band) {
      let file = band?.press_photo?.encoded_file || band?.press_photo?.file
      if (!file) {
        return window.rockon_data.placeholder
      }
      if (!file.endsWith('.webp')) {
        return window.rockon_data.media_offline
      }
      return file
    },
    logo (band) {
      let file = band?.logo?.encoded_file || band?.logo?.file
      if (!file) {
        return window.rockon_data.placeholder
      }
      if (!file.endsWith('.webp')) {
        return window.rockon_data.media_offline
      }
      return file
    }
  },
  template: `
    <div class="row gallery">
      <div v-if="selectedBandDetails.press_photo" class="col">
        <div><h5>Photo</h5></div>
        <a :href="selectedBandDetails.press_photo.file">
        <img :src="pressPhoto(selectedBandDetails)" :alt="selectedBandDetails.press_photo.encoded_file" style="max-height: 250px;">
        </a>
      </div>
      <div v-if="selectedBandDetails.logo" class="col">
        <div><h5>Logo</h5></div>
        <a :href="selectedBandDetails.logo.file">
        <img :src="logo(selectedBandDetails)" :alt="selectedBandDetails.logo.encoded_file" style="max-height: 250px;">
        </a>
      </div>
    </div>
  `,
  mounted () {
    const options = {
      overlayOpacity: 0.4,
      history: false
    }
    const lightbox = new SimpleLightbox('.gallery a', options)
    console.debug('BandImages mounted lightbox:', lightbox)
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
    handleSongClick (song) {
      console.log('Clicked song:', song)
      this.$emit('select-song', song)
    }
  }
})

const TrackDropdown = Vue.defineComponent({
  props: ['tracks', 'selectedBandDetails'],
  emits: ['update:selectedTrack'],
  mounted () {
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
    updateSelectedTrack (event) {
      console.debug('TrackDropdown updateSelectedTrack:', event.target.value)
      this.$emit('update:selectedTrack', event.target.value || null)
    }
  },
  watch: {
    currentTrackId (newVal) {
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
    updateBidStatus (event) {
      console.debug('BidStatusDropdown updateBidStatus:', event.target.value)
      this.$emit('update:bidStatus', event.target.value)
    }
  }
})

const BackstageLink = Vue.defineComponent({
  props: ['selectedBandDetails'],
  computed: {
    url () {
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
    'selectedTrack',
    'showBandNoName',
    'showIncompleteBids',
    'showDeclinedBids'
  ],
  emits: [
    'select-track',
    'filter-no-name',
    'filter-incomplete-bids',
    'filter-declined-bids'
  ],
  template: `
      <section class="row p-4 form-section">
      <div>
      <div><h5>Tracks</h5></div>
        <span v-for="track in tracks" :key="track" class="badge m-2" :class="track === selectedTrack ? 'text-bg-success' : 'text-bg-primary'" style="cursor: pointer;" @click="handleClick(track)">{{ track.name }}</span>
        <div><h5>Filter</h5></div>
        <span class="badge text-bg-primary m-2" :key="no-track" @click="handleShowBandsWithoutTrack" style="cursor: pointer;">Ohne Track</span>
        <span class="badge text-bg-primary m-2" :key="no-vote" @click="handleShowBandsWithoutVote" style="cursor: pointer;">Unbewertete Bands</span>
        <span class="badge text-bg-primary m-2" @click="handleShowStudentBands" style="cursor: pointer;">Schülerbands</span>
        <span class="badge text-bg-primary m-2" @click="handleDeselectTrack" style="cursor: pointer;">Alle Bands</span>
        <div class="form-check form-switch m-2">
          <input class="form-check-input" type="checkbox" role="switch" :checked="showIncompleteBids" @change="handleFilterIncompleteBids" />
          <label class="form-check-label" >Unvollständige Bewerbungen anzeigen</label>
        </div>
        <div class="form-check form-switch m-2">
          <input class="form-check-input" type="checkbox" role="switch" :checked="showBandNoName" @change="handleFilterNoNameChange" />
          <label class="form-check-label" >Bands ohne Namen anzeigen</label>
        </div>
        <div class="form-check form-switch m-2">
        <input class="form-check-input" type="checkbox" role="switch" :checked="showDeclinedBids" @change="handleFilterDeclinedeBids"/>
        <label class="form-check-label" >Abgelehnte Bewerbungen anzeigen</label>
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
    handleShowStudentBands () {
      console.debug('TrackList handleShowStudentBands')
      this.selectedTrack = 'student-bands'
      this.$emit('select-track', 'student-bands')
    },
    handleShowBandsWithoutVote () {
      console.debug('TrackList handleShowBandsWithoutTrack')
      this.selectedTrack = 'no-vote'
      this.$emit('select-track', 'no-vote')
    },
    handleFilterNoNameChange (event) {
      console.debug('TrackList handleFilterNoNameChange:', event.target.checked)
      this.showBandNoName = event.target.checked
      this.$emit('filter-no-name', event.target.checked)
    },
    handleFilterIncompleteBids (event) {
      console.debug(
        'TrackList handleFilterIncompleteBids:',
        event.target.checked
      )
      this.showIncompleteBids = event.target.checked
      this.$emit('filter-incomplete-bids', event.target.checked)
    },
    handleFilterDeclinedeBids (event) {
      console.debug(
        'TrackList handleFilterDeclinedeBids:',
        event.target.checked
      )
      this.showDeclinedBids = event.target.checked
      this.$emit('filter-declined-bids', event.target.checked)
    }
  },
  created () {
    console.log(
      'Component created. Initial value of showBandNoName:',
      this.showBandNoName
    )
  }
})

const BandTags = Vue.defineComponent({
  props: ['selectedBandDetails', 'federalStates'],
  computed: {
    federalStatesTag () {
      console.debug('BandTags computed federalStatesTag:', this.federalStates)
      const federalState = this.federalStates.find(
        federalState =>
          federalState[0] === this.selectedBandDetails.federal_state
      )
      console.debug('BandTags computed federalState:', federalState)
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
    federalStatesTag () {
      console.debug('BandTags computed federalStatesTag:', this.federalStates)
      const federalState = this.federalStates.find(
        federalState =>
          federalState[0] === this.selectedBandDetails.federal_state
      )
      console.debug('BandTags computed federalState:', federalState)
      return federalState ? federalState[1] : null
    }
  },
  methods: {
    hasVote (band) {
      const userVote = this.userVotes.find(vote => vote.band__id === band.id)
      console.debug('BandList hasVote:', userVote)
      return userVote
    },
    voteCount (band) {
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
  components: { BandListTags },
  emits: ['select-band'],
  computed: {
    filteredBands () {
      console.debug('selectedTrack:', this.selectedTrack)
      _bands = this.bands
      if (!this.showIncompleteBids) {
        console.debug('Filtering for bands with incomplete bids.')
        _bands = _bands.filter(band => band.bid_complete === true)
      }
      if (!this.showBandNoName) {
        console.debug('Filtering for bands without a name.')
        _bands = _bands.filter(band => band.name)
      }
      if (!this.showDeclinedBids) {
        console.debug('Filtering for bands with declined bids.')
        _bands = _bands.filter(band => band.bid_status !== 'declined')
      }
      if (this.selectedTrack === 'no-track') {
        console.debug('Filtering for bands without a track.')
        return _bands.filter(band => !band.track)
      }
      if (this.selectedTrack === 'student-bands') {
        console.debug('Filtering for student bands.')
        return _bands.filter(band => band.are_students)
      }
      if (this.selectedTrack === 'no-vote') {
        console.debug('Filtering for bands without a track.')
        _bands = _bands.filter(band => band.bid_status !== 'declined')
        return _bands.filter(
          a1 => !this.userVotes.some(a2 => a2.band__id === a1.id)
        )
      }
      if (!this.selectedTrack) {
        console.debug('No selected track id. Returning all.')
        return _bands
      }
      const filtered = _bands.filter(
        band => band.track && band.track === this.selectedTrack.id
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
  data () {
    return {
      selectedBand: null,
      bgColor: 'var(--rockon-card-bg)'
    }
  },
  methods: {
    selectBand (band) {
      console.debug('BandList selectBand:', band)
      this.$emit('select-band', band)
    },
    cardImage (band) {
      let file = band?.press_photo?.encoded_file || band?.press_photo?.file
      if (!file) {
        return window.rockon_data.placeholder
      }
      if (!file.endsWith('.webp')) {
        return window.rockon_data.media_offline
      }
      return file
    },
    hoverBand (band) {
      this.selectedBand = band
      this.bgColor = 'var(--rockon-secondary-text-emphasis)'
    },
    leaveBand (band) {
      if (this.selectedBand === band) {
        this.selectedBand = null
        this.bgColor = 'var(--rockon-card-bg)'
      }
    }
  },
  template: `
    <section class="row p-4 form-section">
    <div class="row">
      <h3>{{ filteredBands.length }} Bands<span v-if="selectedTrack"> in Track {{selectedTrack.name}}</span></h3>
    </div>
    <div v-if="groupedBands.length > 0" v-for="(group, index) in groupedBands" :key="index">
      <div class="card-group">
        <div class="card" v-for="band in group" @click="selectBand(band)" style="cursor: pointer; max-width: 312px; height: 380px" :style="{ backgroundColor: selectedBand === band ? bgColor : 'var(--rockon-card-bg)' }" @mouseover="hoverBand(band)" @mouseleave="leaveBand(band)">
          <div class="image-container">
            <img :src="cardImage(band)" class="card-img-top img-fluid zoom-image" style="height: 250px; object-fit: cover; object-position: center;" :alt="band.name || band.guid" :loading="index > 2 ? 'lazy' : 'auto'">
          </div>
            <div class="card-body">
            <h6 class="card-title">{{ band.name || band.guid }}</h6>
            <BandListTags :selectedBandDetails="band" :federalStates="federalStates" :userVotes="userVotes" />
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
  mounted () {
    this.fetchRating()
  }
})

const CommentFeed = Vue.defineComponent({
  props: ['commentApi', 'selectedBandDetails', 'newComment'],
  data () {
    return {
      comments: [],
      loading: true
    }
  },
  mounted() {
    this.fetchComments();
  },
  methods: {
    moodIcon (mood) {
      return mood === 'thumbs-up' ? 'fa-thumbs-up' : 'fa-thumbs-down'
    },
    modReason (reason) {
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
    formatDate (isoString) {
      console.debug('BandDetails formatDate:', isoString)
      return DateTime.fromISO(isoString).toFormat('dd.MM.yyyy, HH:mm')
    },
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
        { id: 1, text: 'Hatten wir schonmal' },
        { id: 2, text: 'Solokünstler' },
        { id: 3, text: 'Zu alt' },
        { id: 4, text: 'Zu jung' },
        { id: 5, text: 'Nazis/Schwurbler/Feindliche Gesinnungen' },
        { id: 6, text: 'Unpassend wie Coverband, DJ, keine handgemachte Musik' },
        { id: 7, text: 'Professionals' },
        { id: 8, text: 'Internationals' },
        { id: 9, text: 'Wollen Gage' },
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
    emitComment () {
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
      if (this.selectedMood === 'thumbs-down' && this.selectedReason !== '' && this.commentText.trim() !== '') {
        return false;
      }
      return true;
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
  ],
  emits: ['update:track', 'update:select-song', 'update:rating'],
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
  data () {
    return {
      newComment: null
    }
  },
  created () {
    console.debug('BandDetails created:', this.selectedBandDetails)
    console.debug('BandDetails created allowVotes:', this.allowVotes)
  },
  computed: {
    bandName () {
      if (!this.selectedBandDetails.name) {
        return this.selectedBandDetails.guid
      }
      return this.selectedBandDetails.name
    },
    trackId () {
      console.debug('BandDetails trackId:', this.selectedBandDetails.track)
      if (this.selectedBandDetails.track === null) {
        return 'null'
      }
      return this.selectedBandDetails.track
    },
    coverLetter () {
      if (!this.selectedBandDetails.cover_letter) {
        return 'Kein Cover Letter'
      }
      return this.selectedBandDetails.cover_letter.replace(/\r\n/g, '<br>')
    },
    isUnknownOrPending() {
      return this.selectedBandDetails.bid_status === 'unknown' || this.selectedBandDetails.bid_status === 'pending';
    }
  },
  template: `
    <section :v-if="selectedBandDetails" class="row p-4 form-section">
      <div class="col">
          <h3>{{ bandName }}</h3>
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
      <div class="col-auto">
          <div v-html="coverLetter" class="alert alert-secondary" role="alert"></div>
      </div>
      <div class="col">
          <div><h4>Web</h4></div>
          <BandLinks :links="selectedBandDetails.web_links" />
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
    updateTrack (trackId) {
      console.debug('BandDetails updateTrack:', trackId)
      this.$emit('update:track', trackId)
    },
    handleNewComment (commentData) {
      console.debug('BandDetails emitComment:', commentData)
      this.newComment = commentData;
    },
    updateBidStatus (bidStatus) {
      console.debug('BandDetails updateBidStatus:', bidStatus)
      this.$emit('update:bidStatus', bidStatus)
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
})

const app = createApp({
  data () {
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
      toastAudioPlayer: null,
      toastVisible: false,
      toastIsMaximized: true,
      wavesurfer: null,
      showBandNoName: null,
      showIncompleteBids: null,
      showDeclinedBids: null,
      BandRating: null,
      lightbox: null
    }
  },
  components: {
    TrackList,
    BandList,
    BandDetails,
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
  created () {
    this.getBandList(this.bandListUrl, window.rockon_data.event_slug)
    window.addEventListener('popstate', this.handlePopState)
  },
  methods: {
    handlePopState (event) {
      const url = new URL(window.location.href)
      const hashSegments = url.hash.split('/').filter(segment => segment)

      if (hashSegments.includes('track')) {
        const trackSlug = hashSegments[hashSegments.indexOf('track') + 1]
        const track =
          this.tracks.find(track => track.slug === trackSlug) || null
        this.selectedTrack = track
        this.selectedBand = null
        this.selectedBandDetails = null
      } else if (hashSegments.includes('bid')) {
        const bandGuid = hashSegments[hashSegments.indexOf('bid') + 1]
        const band = this.bands.find(band => band.guid === bandGuid) || null
        this.selectedBand = band
        this.selectedTrack = null
        this.selectedBandDetails = null
        if (band) {
          this.getBandDetails(band.id)
        }
      } else {
        this.selectedTrack = null
        this.selectedBand = null
        this.selectedBandDetails = null
      }
    },
    selectTrack (track) {
      this.selectedTrack = track
      console.debug('Selected track:', this.selectedTrack)
      this.selectedBand = null
      this.selectedBandDetails = null
      console.debug('Selected band:', this.selectedBand)
      const url = new URL(window.location.href)
      if (track === 'no-vote') {
        url.hash = '#/track/no-vote/'
      } else if (track === 'no-track') {
        url.hash = '#/track/no-track/'
      } else if (track === 'student-bands') {
        url.hash = '#/track/student-bands/'
      } else if (track) {
        url.hash = `#/track/${track.slug}/`
      } else {
        url.hash = ''
      }
      window.history.pushState({}, '', url)
    },
    selectBand (band) {
      console.debug('app selectBand:', band)
      this.selectedBand = band
      console.debug('Selected band:', this.selectedBand)
      const url = new URL(window.location.href)
      url.hash = `#/bid/${band.guid}/`
      window.history.pushState({}, '', url)
      this.bandDetailLoaded = false
      this.getBandDetails(band.id)
    },
    updateTrack (trackId) {
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
    updateBidStatus (bidStatus) {
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
      this.selectedBandDetails.bid_state = bidStatus
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
      this.playSongBand = this.selectedBandDetails
      if (!this.toastVisible) {
        this.toastAudioPlayer.show()
        this.toastVisible = true
      }

      if (this.wavesurfer) {
        this.wavesurfer.destroy()
        this.wavesurfer = null
      }

      this.wavesurfer = WaveSurfer.create({
        container: document.getElementById('player-wrapper'),
        waveColor: '#fff300',
        progressColor: '#999400',
        normalize: false,
        splitChannels: false,
        dragToSeek: true,
        cursorWidth: 3,
        url: song.encoded_file || song.file,
        mediaControls: true,
        autoplay: true
      })
    },
    toggleIcon () {
      this.toastIsMaximized = !this.toastIsMaximized
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
      this.toastIsMaximized = true
    },
    handleFilterShowBandNoNameChange (checked) {
      console.debug('app handleFilterShowBandNoNameChange:', checked)
      sessionStorage.setItem('filterShowBandsNoName', JSON.stringify(checked))
      this.showBandNoName = checked
    },
    handleFilterIncompleteBidsChange (checked) {
      console.debug('app handleFilterIncompleteBidsChange:', checked)
      sessionStorage.setItem('filterIncompleteBids', JSON.stringify(checked))
      this.showIncompleteBids = checked
    },
    handleFilterDeclinedBidsChange (checked) {
      console.debug('app handleFilterDeclinedBidsChange:', checked)
      sessionStorage.setItem('filterDeclinedBids', JSON.stringify(checked))
      this.showDeclinedBids = checked
    },
    setRating (rating) {
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
        this.userVotes.push({ band__id: this.selectedBand.id, vote: rating })
      }
    },
    getBandList (url, _event = null) {
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
    getBandDetails (selectedBandId) {
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
  mounted () {
    console.debug('Mounted function called')
    window.addEventListener('popstate', this.handlePopState)
    const toastAudioPlayerElement = document.getElementById('toastAudioPlayer')
    const toastAudioPlayer = bootstrap.Toast.getOrCreateInstance(
      toastAudioPlayerElement
    )
    bootstrap.Toast.getOrCreateInstance(toastAudioPlayer)
    this.toastAudioPlayer = toastAudioPlayer
    this.handlePopState()
    const filterNoName = JSON.parse(
      sessionStorage.getItem('filterShowBandsNoName')
    )
    this.showBandNoName = filterNoName ? filterNoName : false
    const filterIncompleteBids = JSON.parse(
      sessionStorage.getItem('filterIncompleteBids')
    )
    const filterDeclinedBids = JSON.parse(
      sessionStorage.getItem('filterDeclinedBids')
    )
    this.showDeclinedBids = filterDeclinedBids ? filterDeclinedBids : false
    this.showIncompleteBids = filterIncompleteBids
      ? filterIncompleteBids
      : false
  },
  beforeDestroy () {
    window.removeEventListener('popstate', this.handlePopState)
  },
  watch: {
    selectedBand: {
      immediate: true,
      handler (newValue, oldValue) {
        console.log('watch selectedBand changed:', newValue)
        if (newValue && !this.selectedBandDetails) {
          this.getBandDetails(newValue.id)
        }
      }
    },
    selectedBandDetails: {
      immediate: true,
      handler (newValue, oldValue) {
        console.log('watch selectedBandDetails changed:', newValue)
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
