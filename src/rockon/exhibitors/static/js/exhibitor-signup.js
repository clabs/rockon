const { createApp, ref, reactive, computed, onMounted, onBeforeUnmount } = Vue

const ExhibitorSignupApp = {
    setup() {
        // --- Data from Django ---
        const attendances = ref(window.rockon_data.attendances || [])
        const assets = ref(window.rockon_data.assets || [])
        const org = ref(window.rockon_data.org || null)
        const readonly = ref(window.rockon_data.readonly || false)
        const exhibitorData = window.rockon_data.exhibitor || null

        // --- Form data ---
        const formData = reactive({
            organisation_name: org.value ? org.value.org_name : '',
            organisation_address: org.value ? org.value.org_address : '',
            organisation_address_housenumber: org.value ? org.value.org_house_number : '',
            organisation_address_extension: org.value ? org.value.org_address_extension : '',
            organisation_zip: org.value ? org.value.org_zip : '',
            organisation_place: org.value ? org.value.org_place : '',
            offer_note: exhibitorData ? exhibitorData.offer_note : '',
            general_note: exhibitorData ? exhibitorData.general_note : '',
            website: exhibitorData ? exhibitorData.website : '',
            allow_contact: readonly.value,
            read_privacy: readonly.value,
        })

        // --- Attendance & Asset toggles ---
        const attendanceChecked = reactive({})
        const attendanceCounts = reactive({})
        const assetChecked = reactive({})
        const assetCounts = reactive({})

        // Initialize reactive maps
        attendances.value.forEach(day => {
            attendanceChecked[day.id] = false
            attendanceCounts[day.id] = null
        })
        assets.value.forEach(asset => {
            assetChecked[asset.id] = false
            assetCounts[asset.id] = null
        })

        // Pre-populate from submitted exhibitor data
        if (exhibitorData) {
            if (exhibitorData.attendances) {
                exhibitorData.attendances.forEach(att => {
                    attendanceChecked[att.id] = true
                    attendanceCounts[att.id] = att.count
                })
            }
            if (exhibitorData.assets) {
                exhibitorData.assets.forEach(ast => {
                    assetChecked[ast.id] = true
                    assetCounts[ast.id] = ast.count
                })
            }
        }

        // --- Logo ---
        const logoFile = ref(null)
        const logoPreview = ref(exhibitorData && exhibitorData.logo_url ? exhibitorData.logo_url : null)
        const logoFileName = ref(exhibitorData && exhibitorData.logo_name && !exhibitorData.logo_url ? exhibitorData.logo_name : null)
        const logoInput = ref(null)

        // --- UI state ---
        const submitting = ref(false)
        const formError = ref('')
        const formSuccess = ref('')
        const formDirty = ref(false)
        const validation = reactive({})

        // --- Character counter ---
        const offerNoteLength = computed(() => {
            return (formData.offer_note || '').length
        })

        const charCounterClass = computed(() => {
            const len = offerNoteLength.value
            if (len >= 800) return 'text-danger fw-bold'
            if (len >= 700) return 'text-warning'
            return 'text-muted'
        })

        const onOfferNoteInput = () => {
            if (formData.offer_note && formData.offer_note.length > 800) {
                formData.offer_note = formData.offer_note.substring(0, 800)
            }
            markDirty()
        }

        // --- Dirty tracking ---
        const markDirty = () => {
            formDirty.value = true
        }

        const beforeUnloadHandler = (e) => {
            if (formDirty.value) {
                e.preventDefault()
                e.returnValue = 'Die Seite hat ungespeicherte Änderungen.'
                return e.returnValue
            }
        }

        onMounted(() => {
            window.addEventListener('beforeunload', beforeUnloadHandler)
        })

        onBeforeUnmount(() => {
            window.removeEventListener('beforeunload', beforeUnloadHandler)
        })

        // --- Validation ---
        const validateField = (fieldName) => {
            markDirty()
            let valid = false

            switch (fieldName) {
                case 'organisation_name':
                case 'organisation_address':
                case 'organisation_address_housenumber':
                case 'organisation_place':
                    valid = (formData[fieldName] || '').trim() !== ''
                    break
                case 'organisation_zip':
                    valid = /^[0-9]{5}$/.test(formData.organisation_zip || '')
                    break
                case 'website':
                    if (!formData.website || formData.website.trim() === '') {
                        // Optional field — no validation class when empty
                        delete validation[fieldName]
                        return true
                    }
                    try {
                        new URL(formData.website)
                        valid = true
                    } catch {
                        valid = false
                    }
                    break
                case 'allow_contact':
                    valid = formData.allow_contact === true
                    break
                case 'read_privacy':
                    valid = formData.read_privacy === true
                    break
                default:
                    valid = false
            }

            validation[fieldName] = valid
            return valid
        }

        const validateAttendanceCount = (dayId) => {
            markDirty()
            const key = 'attendance_count_' + dayId
            if (!attendanceChecked[dayId]) {
                delete validation[key]
                return true
            }
            const val = attendanceCounts[dayId]
            const valid = val !== null && val !== '' && !isNaN(val) && val >= 1
            validation[key] = valid
            return valid
        }

        const validateAssetCount = (assetId) => {
            markDirty()
            const key = 'asset_count_' + assetId
            const asset = assets.value.find(a => a.id === assetId)
            if (!assetChecked[assetId] || (asset && asset.is_bool)) {
                delete validation[key]
                return true
            }
            const val = assetCounts[assetId]
            const valid = val !== null && val !== '' && !isNaN(val) && val >= 1
            validation[key] = valid
            return valid
        }

        const fieldClass = (fieldName) => {
            if (validation[fieldName] === undefined) return ''
            return validation[fieldName] ? 'is-valid' : 'is-invalid'
        }

        // --- Toggle handlers ---
        const onAttendanceToggle = (dayId) => {
            markDirty()
            if (!attendanceChecked[dayId]) {
                attendanceCounts[dayId] = null
                delete validation['attendance_count_' + dayId]
            }
        }

        const onAssetToggle = (assetId) => {
            markDirty()
            if (!assetChecked[assetId]) {
                assetCounts[assetId] = null
                delete validation['asset_count_' + assetId]
            }
        }

        // --- Logo handlers ---
        const onLogoSelected = (event) => {
            markDirty()
            const file = event.target.files[0]
            if (file) {
                logoFile.value = file
                // Show preview for image files, otherwise just store the file
                if (file.type && file.type.startsWith('image/')) {
                    const reader = new FileReader()
                    reader.onload = (e) => {
                        logoPreview.value = e.target.result
                    }
                    reader.readAsDataURL(file)
                } else {
                    // Non-image file (e.g. EPS, PDF) — show filename instead of preview
                    logoPreview.value = null
                    logoFileName.value = file.name
                }
            }
        }

        const removeLogo = () => {
            logoFile.value = null
            logoPreview.value = null
            logoFileName.value = null
            if (logoInput.value) {
                logoInput.value.value = ''
            }
        }

        // --- Can submit computed ---
        const hasAttendanceChecked = computed(() => {
            return Object.values(attendanceChecked).some(v => v === true)
        })

        const canSubmit = computed(() => {
            return hasAttendanceChecked.value &&
                formData.allow_contact &&
                formData.read_privacy
        })

        // --- Validate all ---
        const validateAll = () => {
            let allValid = true

            // Organisation fields (skip if org pre-filled)
            if (!org.value) {
                const orgFields = [
                    'organisation_name',
                    'organisation_address',
                    'organisation_address_housenumber',
                    'organisation_zip',
                    'organisation_place',
                ]
                orgFields.forEach(field => {
                    if (!validateField(field)) allValid = false
                })
            }

            // Attendance counts
            attendances.value.forEach(day => {
                if (attendanceChecked[day.id]) {
                    if (!validateAttendanceCount(day.id)) allValid = false
                }
            })

            // Asset counts
            assets.value.forEach(asset => {
                if (assetChecked[asset.id] && !asset.is_bool) {
                    if (!validateAssetCount(asset.id)) allValid = false
                }
            })

            // Website (optional)
            if (formData.website && formData.website.trim() !== '') {
                if (!validateField('website')) allValid = false
            }

            // Legal
            if (!validateField('allow_contact')) allValid = false
            if (!validateField('read_privacy')) allValid = false

            return allValid
        }

        // --- Submit ---
        const submitForm = async () => {
            formError.value = ''
            formSuccess.value = ''

            if (!validateAll()) {
                formError.value = 'Bitte korrigiere die Fehler in den markierten Feldern.'
                return
            }

            submitting.value = true

            try {
                // Build the JSON payload
                const payload = {
                    organisation_name: formData.organisation_name || null,
                    organisation_address: formData.organisation_address || null,
                    organisation_address_housenumber: formData.organisation_address_housenumber || null,
                    organisation_address_extension: formData.organisation_address_extension || null,
                    organisation_zip: formData.organisation_zip || null,
                    organisation_place: formData.organisation_place || null,
                    offer_note: formData.offer_note || null,
                    general_note: formData.general_note || null,
                    website: formData.website || null,
                    allow_contact: formData.allow_contact,
                    read_privacy: formData.read_privacy,
                    attendances: [],
                    assets: [],
                }

                if (org.value) {
                    payload.org_id = org.value.id
                }

                // Collect attendance data
                attendances.value.forEach(day => {
                    if (attendanceChecked[day.id]) {
                        payload.attendances.push({
                            id: day.id,
                            count: parseInt(attendanceCounts[day.id]) || 1,
                        })
                    }
                })

                // Collect asset data
                assets.value.forEach(asset => {
                    if (assetChecked[asset.id]) {
                        payload.assets.push({
                            id: asset.id,
                            count: asset.is_bool ? 1 : (parseInt(assetCounts[asset.id]) || 1),
                        })
                    }
                })

                // Build FormData for multipart upload
                const fd = new FormData()
                fd.append('data', JSON.stringify(payload))

                if (logoFile.value) {
                    fd.append('logo', logoFile.value)
                }

                const response = await fetch(window.rockon_api.signup, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': window.rockon_api.csrfToken,
                    },
                    credentials: 'same-origin',
                    body: fd,
                })

                const result = await response.json()

                if (response.ok) {
                    formDirty.value = false
                    // Reload the page to show readonly view
                    window.location.reload()
                } else {
                    formError.value = result.message || 'Ein Fehler ist aufgetreten. Bitte versuche es erneut.'
                    console.error('Signup error:', result)
                }
            } catch (err) {
                formError.value = 'Ein Netzwerkfehler ist aufgetreten. Bitte versuche es erneut.'
                console.error('Signup network error:', err)
            } finally {
                submitting.value = false
            }
        }

        // --- Reset ---
        const resetForm = () => {
            // Reset form fields
            formData.offer_note = ''
            formData.general_note = ''
            formData.website = ''
            formData.allow_contact = false
            formData.read_privacy = false

            if (!org.value) {
                formData.organisation_name = ''
                formData.organisation_address = ''
                formData.organisation_address_housenumber = ''
                formData.organisation_address_extension = ''
                formData.organisation_zip = ''
                formData.organisation_place = ''
            }

            // Reset attendance & assets
            attendances.value.forEach(day => {
                attendanceChecked[day.id] = false
                attendanceCounts[day.id] = null
            })
            assets.value.forEach(asset => {
                assetChecked[asset.id] = false
                assetCounts[asset.id] = null
            })

            // Reset logo
            removeLogo()

            // Reset validation
            Object.keys(validation).forEach(key => delete validation[key])

            // Reset messages
            formError.value = ''
            formSuccess.value = ''
            formDirty.value = false
        }

        return {
            // Data
            attendances,
            assets,
            org,
            readonly,
            formData,
            attendanceChecked,
            attendanceCounts,
            assetChecked,
            assetCounts,
            logoFile,
            logoPreview,
            logoFileName,
            logoInput,
            submitting,
            formError,
            formSuccess,

            // Computed
            offerNoteLength,
            charCounterClass,
            canSubmit,

            // Methods
            fieldClass,
            validateField,
            validateAttendanceCount,
            validateAssetCount,
            onAttendanceToggle,
            onAssetToggle,
            onOfferNoteInput,
            onLogoSelected,
            removeLogo,
            submitForm,
            resetForm,
        }
    },
}

document.addEventListener('DOMContentLoaded', () => {
    createApp(ExhibitorSignupApp).mount('#app')
})
