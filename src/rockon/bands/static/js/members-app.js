const { createApp, ref, reactive, computed } = Vue

const validateEmail = email =>
    /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(
        String(email).toLowerCase()
    )

const emptyPerson = () => ({
    first_name: '',
    last_name: '',
    email: '',
    address: '',
    housenumber: '',
    zip_code: '',
    place: '',
    nutrition: '',
    position: '',
})

const MembersApp = {
    setup() {
        const cfg = window.rockon_data
        const csrf = window.rockon_api.csrfToken

        const currentMembers = ref(cfg.current_members || [])
        const draftMembers = ref([])
        const submitted = ref(false)
        const submitting = ref(false)
        const apiError = ref('')
        const showConfirm = ref(false)

        const slots = computed(
            () => cfg.max_members - currentMembers.value.length - draftMembers.value.length
        )
        const totalCount = computed(
            () => currentMembers.value.length + draftMembers.value.length
        )

        // Add form
        const showForm = ref(false)
        const form = reactive(emptyPerson())
        const formErrors = reactive({})

        // Edit form
        const editingIndex = ref(null)
        const editForm = reactive(emptyPerson())
        const editErrors = reactive({})

        const clearErrors = target => {
            Object.keys(target).forEach(k => delete target[k])
        }

        const validatePerson = (data, errors) => {
            clearErrors(errors)
            const required = [
                'first_name', 'last_name', 'email',
                'address', 'housenumber', 'zip_code', 'place',
                'nutrition', 'position',
            ]
            let valid = true
            for (const field of required) {
                if (!data[field] || data[field] === 'unknown') {
                    errors[field] = 'Pflichtfeld'
                    valid = false
                }
            }
            if (data.email && !validateEmail(data.email)) {
                errors.email = 'Ungültige E-Mail-Adresse'
                valid = false
            }
            return valid
        }

        const openAddForm = () => {
            Object.assign(form, emptyPerson())
            clearErrors(formErrors)
            editingIndex.value = null
            showForm.value = true
        }

        const cancelAdd = () => {
            showForm.value = false
            clearErrors(formErrors)
        }

        const addToDraft = () => {
            if (!validatePerson(form, formErrors)) return
            draftMembers.value.push({ ...form })
            showForm.value = false
        }

        const editDraft = i => {
            showForm.value = false
            Object.assign(editForm, { ...draftMembers.value[i] })
            clearErrors(editErrors)
            editingIndex.value = i
        }

        const cancelEdit = () => {
            editingIndex.value = null
            clearErrors(editErrors)
        }

        const saveDraft = i => {
            if (!validatePerson(editForm, editErrors)) return
            draftMembers.value[i] = { ...editForm }
            editingIndex.value = null
        }

        const removeDraft = i => {
            draftMembers.value.splice(i, 1)
            if (editingIndex.value === i) {
                editingIndex.value = null
            }
        }

        const submitAll = async () => {
            submitting.value = true
            apiError.value = ''
            try {
                const resp = await fetch(cfg.api_signup, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrf,
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({
                        band: cfg.band_id,
                        persons: draftMembers.value,
                    }),
                })
                if (resp.ok) {
                    const posMap = Object.fromEntries(cfg.position_choices.map(c => [c.value, c.label]))
                    const nutMap = Object.fromEntries(cfg.nutrition_choices.map(c => [c.value, c.label]))
                    for (const p of draftMembers.value) {
                        currentMembers.value.push({
                            id: null,
                            position_label: posMap[p.position] ?? p.position,
                            nutrition_label: nutMap[p.nutrition] ?? p.nutrition,
                            user: { first_name: p.first_name, last_name: p.last_name, email: p.email },
                        })
                    }
                    draftMembers.value = []
                    submitted.value = true
                    showConfirm.value = false
                } else {
                    const data = await resp.json().catch(() => ({}))
                    apiError.value = data.message || `Fehler ${resp.status}`
                }
            } catch (e) {
                apiError.value = 'Netzwerkfehler – bitte erneut versuchen.'
            } finally {
                submitting.value = false
            }
        }

        return {
            cfg,
            currentMembers,
            draftMembers,
            submitted,
            submitting,
            apiError,
            showConfirm,
            slots,
            totalCount,
            showForm,
            form,
            formErrors,
            editingIndex,
            editForm,
            editErrors,
            openAddForm,
            cancelAdd,
            addToDraft,
            editDraft,
            cancelEdit,
            saveDraft,
            removeDraft,
            submitAll,
        }
    },

    template: `
<div>

  <!-- Slot badge + info -->
  <div class="alert alert-info">
    <p>Ihr könnt bis zu 10 Personen bei uns anmelden. Für die Versicherung brauchen wir Namen und Meldeanschrift.</p>
    <p>Damit sich unser Catering vorbereiten kann, gebt bitte die Ernährungsgewohnheit an.</p>
    <p>Für einen reibungslosen Ablauf teilt uns bitte auch die Funktion der Personen mit.</p>
    <p class="mb-0">
      <strong>{{ totalCount }} / {{ cfg.max_members }} Personen gemeldet</strong>
      <span v-if="!submitted && slots > 0"> &mdash; {{ slots }} Plätze verfügbar</span>
    </p>
  </div>

  <!-- Already-submitted members -->
  <div v-if="currentMembers.length > 0" class="mb-4">
    <h5>Bereits gemeldet</h5>
    <table class="table table-dark table-striped table-hover">
      <thead>
        <tr>
          <th>Vorname</th>
          <th>Nachname</th>
          <th>Funktion</th>
          <th>Ernährung</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="m in currentMembers" :key="m.id">
          <td>{{ m.user.first_name }}</td>
          <td>{{ m.user.last_name }}</td>
          <td>{{ m.position_label }}</td>
          <td>{{ m.nutrition_label }}</td>
        </tr>
      </tbody>
    </table>
    <p class="text-muted small">
      Für Änderungen an bestehenden Meldungen bitte die Bandbetreuung kontaktieren.
    </p>
  </div>

  <!-- Draft section (hidden once submitted) -->
  <div v-if="!submitted">

    <!-- Draft table -->
    <div v-if="draftMembers.length > 0" class="mb-4">
      <h5>Neu hinzugefügt <span class="badge bg-secondary">{{ draftMembers.length }}</span></h5>
      <table class="table table-dark table-striped table-hover">
        <thead>
          <tr>
            <th>#</th>
            <th>Vorname</th>
            <th>Nachname</th>
            <th>E-Mail</th>
            <th>Funktion</th>
            <th>Ernährung</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(m, i) in draftMembers" :key="i">
            <!-- Normal row -->
            <tr v-if="editingIndex !== i">
              <td>{{ i + 1 }}</td>
              <td>{{ m.first_name }}</td>
              <td>{{ m.last_name }}</td>
              <td>{{ m.email }}</td>
              <td>{{ cfg.position_choices.find(c => c.value === m.position)?.label }}</td>
              <td>{{ cfg.nutrition_choices.find(c => c.value === m.nutrition)?.label }}</td>
              <td class="text-nowrap">
                <button type="button" class="btn btn-sm btn-outline-light me-1"
                        @click="editDraft(i)">
                  <i class="fa-solid fa-pen"></i>
                </button>
                <button type="button" class="btn btn-sm btn-outline-danger"
                        @click="removeDraft(i)">
                  <i class="fa-solid fa-trash-can"></i>
                </button>
              </td>
            </tr>
            <!-- Inline edit row -->
            <tr v-else class="table-active">
              <td colspan="7">
                <div class="row g-2 my-1">
                  <div class="col-md-3">
                    <label class="form-label">Vorname</label>
                    <input v-model="editForm.first_name" type="text" class="form-control form-control-sm"
                           :class="editErrors.first_name ? 'is-invalid' : ''">
                    <div class="invalid-feedback">{{ editErrors.first_name }}</div>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">Nachname</label>
                    <input v-model="editForm.last_name" type="text" class="form-control form-control-sm"
                           :class="editErrors.last_name ? 'is-invalid' : ''">
                    <div class="invalid-feedback">{{ editErrors.last_name }}</div>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">E-Mail</label>
                    <input v-model="editForm.email" type="email" class="form-control form-control-sm"
                           :class="editErrors.email ? 'is-invalid' : ''">
                    <div class="invalid-feedback">{{ editErrors.email }}</div>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Straße</label>
                    <input v-model="editForm.address" type="text" class="form-control form-control-sm"
                           :class="editErrors.address ? 'is-invalid' : ''">
                    <div class="invalid-feedback">{{ editErrors.address }}</div>
                  </div>
                  <div class="col-md-2">
                    <label class="form-label">Hausnr.</label>
                    <input v-model="editForm.housenumber" type="text" class="form-control form-control-sm"
                           :class="editErrors.housenumber ? 'is-invalid' : ''">
                    <div class="invalid-feedback">{{ editErrors.housenumber }}</div>
                  </div>
                  <div class="col-md-2">
                    <label class="form-label">PLZ</label>
                    <input v-model="editForm.zip_code" type="text" class="form-control form-control-sm"
                           :class="editErrors.zip_code ? 'is-invalid' : ''">
                    <div class="invalid-feedback">{{ editErrors.zip_code }}</div>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Ort</label>
                    <input v-model="editForm.place" type="text" class="form-control form-control-sm"
                           :class="editErrors.place ? 'is-invalid' : ''">
                    <div class="invalid-feedback">{{ editErrors.place }}</div>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">Funktion</label>
                    <select v-model="editForm.position" class="form-select form-select-sm"
                            :class="editErrors.position ? 'is-invalid' : ''">
                      <option value="">– bitte wählen –</option>
                      <option v-for="c in cfg.position_choices" :key="c.value" :value="c.value">{{ c.label }}</option>
                    </select>
                    <div class="invalid-feedback">{{ editErrors.position }}</div>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">Ernährung</label>
                    <select v-model="editForm.nutrition" class="form-select form-select-sm"
                            :class="editErrors.nutrition ? 'is-invalid' : ''">
                      <option value="">– bitte wählen –</option>
                      <option v-for="c in cfg.nutrition_choices" :key="c.value" :value="c.value">{{ c.label }}</option>
                    </select>
                    <div class="invalid-feedback">{{ editErrors.nutrition }}</div>
                  </div>
                  <div class="col-12 d-flex gap-2">
                    <button type="button" class="btn btn-sm btn-primary" @click="saveDraft(i)">Speichern</button>
                    <button type="button" class="btn btn-sm btn-secondary" @click="cancelEdit()">Abbruch</button>
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Add button -->
    <div v-if="slots > 0 && editingIndex === null" class="mb-3">
      <button type="button" class="btn btn-primary" @click="openAddForm()">
        <i class="fa-solid fa-plus me-1"></i>Person hinzufügen
      </button>
    </div>

    <!-- Submit button -->
    <div v-if="draftMembers.length > 0 && editingIndex === null" class="mt-3">
      <button type="button" class="btn btn-success" @click="showConfirm = true">
        Meldung abschicken
      </button>
    </div>

  </div><!-- /draft section -->

  <!-- Add person modal -->
  <div v-if="showForm" class="modal d-block" tabindex="-1" @click.self="cancelAdd()">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Neue Person</h5>
          <button type="button" class="btn-close" @click="cancelAdd()"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label">Vorname</label>
              <input v-model="form.first_name" type="text" class="form-control"
                     :class="formErrors.first_name ? 'is-invalid' : ''"
                     autocomplete="given-name">
              <div class="invalid-feedback">{{ formErrors.first_name }}</div>
            </div>
            <div class="col-md-4">
              <label class="form-label">Nachname</label>
              <input v-model="form.last_name" type="text" class="form-control"
                     :class="formErrors.last_name ? 'is-invalid' : ''"
                     autocomplete="family-name">
              <div class="invalid-feedback">{{ formErrors.last_name }}</div>
            </div>
            <div class="col-md-4">
              <label class="form-label">E-Mail</label>
              <input v-model="form.email" type="email" class="form-control"
                     :class="formErrors.email ? 'is-invalid' : ''"
                     autocomplete="email">
              <div class="invalid-feedback">{{ formErrors.email }}</div>
            </div>
            <div class="col-md-5">
              <label class="form-label">Straße</label>
              <input v-model="form.address" type="text" class="form-control"
                     :class="formErrors.address ? 'is-invalid' : ''"
                     autocomplete="street-address">
              <div class="invalid-feedback">{{ formErrors.address }}</div>
            </div>
            <div class="col-md-2">
              <label class="form-label">Hausnr.</label>
              <input v-model="form.housenumber" type="text" class="form-control"
                     :class="formErrors.housenumber ? 'is-invalid' : ''">
              <div class="invalid-feedback">{{ formErrors.housenumber }}</div>
            </div>
            <div class="col-md-2">
              <label class="form-label">PLZ</label>
              <input v-model="form.zip_code" type="text" class="form-control"
                     :class="formErrors.zip_code ? 'is-invalid' : ''"
                     autocomplete="postal-code">
              <div class="invalid-feedback">{{ formErrors.zip_code }}</div>
            </div>
            <div class="col-md-3">
              <label class="form-label">Ort</label>
              <input v-model="form.place" type="text" class="form-control"
                     :class="formErrors.place ? 'is-invalid' : ''"
                     autocomplete="address-level2">
              <div class="invalid-feedback">{{ formErrors.place }}</div>
            </div>
            <div class="col-md-4">
              <label class="form-label">Funktion</label>
              <select v-model="form.position" class="form-select"
                      :class="formErrors.position ? 'is-invalid' : ''">
                <option value="">– bitte wählen –</option>
                <option v-for="c in cfg.position_choices" :key="c.value" :value="c.value">{{ c.label }}</option>
              </select>
              <div class="invalid-feedback">{{ formErrors.position }}</div>
            </div>
            <div class="col-md-4">
              <label class="form-label">Ernährung</label>
              <select v-model="form.nutrition" class="form-select"
                      :class="formErrors.nutrition ? 'is-invalid' : ''">
                <option value="">– bitte wählen –</option>
                <option v-for="c in cfg.nutrition_choices" :key="c.value" :value="c.value">{{ c.label }}</option>
              </select>
              <div class="invalid-feedback">{{ formErrors.nutrition }}</div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="cancelAdd()">Abbruch</button>
          <button type="button" class="btn btn-primary" @click="addToDraft()">Hinzufügen</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="showForm" class="modal-backdrop show"></div>

  <!-- Confirm modal -->
  <div v-if="showConfirm" class="modal d-block" tabindex="-1" @click.self="showConfirm = false">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Meldung abschicken</h5>
          <button type="button" class="btn-close" :disabled="submitting"
                  @click="showConfirm = false"></button>
        </div>
        <div class="modal-body">
          <p class="mb-0">
            {{ draftMembers.length }} Person(en) werden jetzt gemeldet.
            Diese Aktion kann nicht rückgängig gemacht werden.
          </p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" :disabled="submitting"
                  @click="showConfirm = false">Abbruch</button>
          <button type="button" class="btn btn-success" :disabled="submitting"
                  @click="submitAll()">
            <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
            Ja, jetzt melden
          </button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="showConfirm" class="modal-backdrop show"></div>

  <!-- Success -->
  <div v-if="submitted" class="alert alert-primary mt-3" role="alert">
    Meldung erfolgreich abgeschlossen.
  </div>

  <!-- Full (no draft slot, nothing submitted yet) -->
  <div v-if="!submitted && slots === 0 && draftMembers.length === 0" class="alert alert-primary mt-3" role="alert">
    Meldung bereits abgeschlossen. Solltet ihr Hilfe brauchen, wendet euch bitte an die Bandbetreuung.
  </div>

  <!-- API error -->
  <div v-if="apiError" class="alert alert-danger mt-3" role="alert">
    {{ apiError }}
  </div>

</div>
    `,
}

document.addEventListener('DOMContentLoaded', () => {
    createApp(MembersApp).mount('#app')
})
