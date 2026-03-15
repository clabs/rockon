const { ref, reactive, computed, watch, onBeforeUnmount } = Vue

const REQUIRED_FIELDS = [
    'nutrition_type',
    'crew_shirt',
    'allow_contact',
    'read_privacy',
]

const CREW_STATE_ALERTS = {
    unknown: {
        className: 'alert-info',
        title: 'Status: Eingegangen.',
        message: 'Deine Anmeldung ist eingegangen und wird von der Crew Koordination geprüft. Du kannst deine Angaben weiterhin bearbeiten.',
    },
    confirmed: {
        className: 'alert-success',
        title: 'Status: Bestätigt.',
        message: 'Du bist als Crewmitglied bestätigt. Deine Angaben sind jetzt schreibgeschützt.',
    },
    rejected: {
        className: 'alert-danger',
        title: 'Status: Abgelehnt.',
        message: 'Deine Anmeldung wurde aktuell nicht bestätigt. Du kannst deine Angaben weiterhin bearbeiten und erneut absenden.',
    },
}

const READ_ONLY_STATES = ['confirmed']

function createInitialFormData() {
    return {
        crew_shirt: '',
        nutrition_type: '',
        nutrition_note: '',
        skills_note: '',
        attendance_note: '',
        stays_overnight: false,
        general_note: '',
        needs_leave_of_absence: false,
        leave_of_absence_note: '',
        skill_ids: [],
        attendance_ids: [],
        teamcategory_ids: [],
        team_ids: [],
        allow_contact: false,
        read_privacy: false,
    }
}

function cloneFormData(formData) {
    return JSON.parse(JSON.stringify(formData))
}

function normalizeInitialFormData(initialData) {
    const base = createInitialFormData()
    const source = initialData || {}

    return {
        ...base,
        ...source,
        crew_shirt: source.crew_shirt || '',
        nutrition_type: source.nutrition_type || '',
        nutrition_note: source.nutrition_note || '',
        skills_note: source.skills_note || '',
        attendance_note: source.attendance_note || '',
        stays_overnight: Boolean(source.stays_overnight),
        general_note: source.general_note || '',
        needs_leave_of_absence: Boolean(source.needs_leave_of_absence),
        leave_of_absence_note: source.leave_of_absence_note || '',
        skill_ids: Array.isArray(source.skill_ids) ? source.skill_ids : [],
        attendance_ids: Array.isArray(source.attendance_ids)
            ? source.attendance_ids
            : [],
        teamcategory_ids: Array.isArray(source.teamcategory_ids)
            ? source.teamcategory_ids
            : [],
        team_ids: Array.isArray(source.team_ids) ? source.team_ids : [],
        allow_contact: Boolean(source.allow_contact),
        read_privacy: Boolean(source.read_privacy),
    }
}

function isFieldValid(formData, fieldName) {
    if (fieldName === 'allow_contact' || fieldName === 'read_privacy') {
        return Boolean(formData[fieldName])
    }
    return formData[fieldName] !== ''
}

const CrewJoinApp = {
    setup() {
        const shirts = ref(window.rockon_data.shirts || [])
        const skills = ref(window.rockon_data.skills || [])
        const attendancePhases = ref(window.rockon_data.attendance_phases || [])
        const teamCategories = ref(window.rockon_data.team_categories || [])

        const eventName = ref(window.rockon_data.event_name || '')
        const eventImageUrl = ref(window.rockon_data.event_image_url || '')
        const privacyUrl = ref(window.rockon_data.privacy_url || '')
        const allowOvernight = ref(Boolean(window.rockon_data.allow_overnight))
        const crewMemberState = ref(window.rockon_data.crew_member_state || 'unknown')
        const isReadOnly = ref(Boolean(window.rockon_data.form_is_readonly))

        const formData = reactive(
            normalizeInitialFormData(window.rockon_data.initial_form_data)
        )
        const touchedFields = reactive({})

        const isSubmitting = ref(false)
        const submitAttempted = ref(false)
        const formMessage = ref('')
        const formMessageClass = ref('alert-danger')

        const beforeUnloadHandler = (event) => {
            event.preventDefault()
            event.returnValue = 'Die Seite hat ungespeicherte Änderungen.'
            return event.returnValue
        }

        const initialSnapshot = ref('')
        const selectAllAttendance = ref(false)

        function refreshInitialSnapshot() {
            initialSnapshot.value = JSON.stringify(cloneFormData(formData))
        }

        function allAttendanceIds() {
            const ids = []
            for (const phase of attendancePhases.value) {
                for (const day of phase.days) {
                    ids.push(day.id)
                }
            }
            return ids
        }

        const hasUnsavedChanges = computed(() => {
            return JSON.stringify(cloneFormData(formData)) !== initialSnapshot.value
        })

        const stateAlert = computed(() => {
            return CREW_STATE_ALERTS[crewMemberState.value] || CREW_STATE_ALERTS.unknown
        })

        function syncSelectAllAttendance() {
            const allIds = allAttendanceIds()
            selectAllAttendance.value = allIds.length > 0 && allIds.every((id) => {
                return formData.attendance_ids.includes(id)
            })
        }

        function clearFormMessage() {
            formMessage.value = ''
        }

        function focusSubmitFeedback() {
            const feedback = document.getElementById('submit-feedback')
            if (!feedback) {
                return
            }
            feedback.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }

        function touchField(fieldName) {
            touchedFields[fieldName] = true
        }

        function fieldClass(fieldName) {
            const shouldShow = submitAttempted.value || touchedFields[fieldName]
            if (!shouldShow) {
                return ''
            }
            return isFieldValid(formData, fieldName) ? 'is-valid' : 'is-invalid'
        }

        function validateRequiredFields() {
            let isValid = true
            for (const fieldName of REQUIRED_FIELDS) {
                touchField(fieldName)
                if (!isFieldValid(formData, fieldName)) {
                    isValid = false
                }
            }
            return isValid
        }

        function renderValidationMessage() {
            const isValid = validateRequiredFields()
            if (!isValid) {
                formMessageClass.value = 'alert-danger'
                formMessage.value = 'Bitte korrigiere die Fehler in den markierten Feldern.'
            } else {
                clearFormMessage()
            }
            return isValid
        }

        function toggleAllAttendance() {
            if (selectAllAttendance.value) {
                formData.attendance_ids = allAttendanceIds()
            } else {
                formData.attendance_ids = []
            }
        }

        function resetValidationState() {
            submitAttempted.value = false
            for (const key of Object.keys(touchedFields)) {
                delete touchedFields[key]
            }
            clearFormMessage()
        }

        function resetForm() {
            if (isReadOnly.value) {
                return
            }
            if (!window.confirm('Möchtest du das Formular zurücksetzen?')) {
                return
            }

            const freshFormData = createInitialFormData()
            for (const key of Object.keys(freshFormData)) {
                formData[key] = freshFormData[key]
            }

            selectAllAttendance.value = false
            resetValidationState()
            refreshInitialSnapshot()
        }

        function submitPayload() {
            return {
                crew_shirt: formData.crew_shirt,
                nutrition_type: formData.nutrition_type,
                nutrition_note: formData.nutrition_note,
                skills_note: formData.skills_note,
                attendance_note: formData.attendance_note,
                stays_overnight: formData.stays_overnight,
                general_note: formData.general_note,
                needs_leave_of_absence: formData.needs_leave_of_absence,
                leave_of_absence_note: formData.leave_of_absence_note,
                skill_ids: formData.skill_ids,
                attendance_ids: formData.attendance_ids,
                teamcategory_ids: formData.teamcategory_ids,
                team_ids: formData.team_ids,
            }
        }

        async function submitForm() {
            if (isReadOnly.value) {
                return
            }
            submitAttempted.value = true
            if (!renderValidationMessage()) {
                focusSubmitFeedback()
                return
            }

            isSubmitting.value = true
            formMessageClass.value = 'alert-info'
            formMessage.value = 'Anmeldung wird gespeichert. Bitte kurz warten...'
            focusSubmitFeedback()

            try {
                const response = await fetch(window.rockon_data.api_crew_signup, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': window.rockon_data.csrf_token,
                    },
                    body: JSON.stringify(submitPayload()),
                })

                if (!response.ok) {
                    let apiMessage = 'Die Anmeldung konnte nicht gespeichert werden. Bitte versuche es erneut.'
                    try {
                        const body = await response.json()
                        if (body && body.message) {
                            apiMessage = body.message
                        }
                    } catch (_error) {
                        // Keep the fallback message if the response body is not JSON.
                    }
                    throw new Error(apiMessage)
                }

                formMessageClass.value = 'alert-success'
                formMessage.value = 'Deine Anmeldung wurde gespeichert. Du kannst deine Angaben hier weiter einsehen und bei Bedarf erneut absenden.'
                refreshInitialSnapshot()
                submitAttempted.value = false
                focusSubmitFeedback()
            } catch (error) {
                console.error(error)
                formMessageClass.value = 'alert-danger'
                formMessage.value = error.message || 'Die Anmeldung konnte nicht gespeichert werden.'
                focusSubmitFeedback()
            } finally {
                isSubmitting.value = false
            }
        }

        watch(
            () => formData.attendance_ids,
            () => {
                syncSelectAllAttendance()
            },
            { deep: true }
        )

        watch(
            () => formData.needs_leave_of_absence,
            (enabled) => {
                if (!enabled) {
                    formData.leave_of_absence_note = ''
                }
            }
        )

        if (!allowOvernight.value) {
            formData.stays_overnight = false
        }

        if (READ_ONLY_STATES.includes(crewMemberState.value)) {
            isReadOnly.value = true
        }

        refreshInitialSnapshot()
        syncSelectAllAttendance()

        watch(
            hasUnsavedChanges,
            (isDirty) => {
                if (isDirty) {
                    window.addEventListener('beforeunload', beforeUnloadHandler)
                } else {
                    window.removeEventListener('beforeunload', beforeUnloadHandler)
                }
            },
            { immediate: true }
        )

        onBeforeUnmount(() => {
            window.removeEventListener('beforeunload', beforeUnloadHandler)
        })

        return {
            shirts,
            skills,
            attendancePhases,
            teamCategories,
            eventName,
            eventImageUrl,
            privacyUrl,
            allowOvernight,
            crewMemberState,
            isReadOnly,
            stateAlert,
            formData,
            selectAllAttendance,
            isSubmitting,
            formMessage,
            formMessageClass,
            fieldClass,
            touchField,
            toggleAllAttendance,
            submitForm,
            resetForm,
        }
    },
}
