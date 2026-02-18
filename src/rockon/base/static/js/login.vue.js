const { createApp, ref, reactive, computed, watch } = Vue

const LoginApp = {
    setup() {
        // --- Panel state ---
        const activePanel = ref('login')

        // --- Login form ---
        const loginForm = reactive({
            email: '',
            loading: false,
            sent: false,
            error: '',
        })
        const loginTouched = ref(false)

        // --- Signup form ---
        const signupForm = reactive({
            email: '',
            emailConfirm: '',
            allowContact: false,
            readPrivacy: false,
            loading: false,
            error: '',
        })
        const signupTouched = reactive({
            email: false,
            emailConfirm: false,
            allowContact: false,
            readPrivacy: false,
        })

        // --- Validation helpers ---
        const emailRegex = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/

        const isValidEmail = (email) => {
            return emailRegex.test(String(email).toLowerCase())
        }

        // --- Login validation ---
        const loginEmailValid = computed(() => isValidEmail(loginForm.email))

        const loginEmailClass = computed(() => {
            if (!loginTouched.value || !loginForm.email) return ''
            return loginEmailValid.value ? 'is-valid' : 'is-invalid'
        })

        const loginCanSubmit = computed(() => {
            return loginEmailValid.value && !loginForm.loading && !loginForm.sent
        })

        // --- Signup validation ---
        const signupEmailValid = computed(() => isValidEmail(signupForm.email))
        const signupEmailConfirmValid = computed(() => {
            return isValidEmail(signupForm.emailConfirm) && signupForm.emailConfirm === signupForm.email
        })

        const signupFieldClass = (field) => {
            if (!signupTouched[field]) return ''
            switch (field) {
                case 'email':
                    if (!signupForm.email) return ''
                    return signupEmailValid.value ? 'is-valid' : 'is-invalid'
                case 'emailConfirm':
                    if (!signupForm.emailConfirm) return ''
                    return signupEmailConfirmValid.value ? 'is-valid' : 'is-invalid'
                case 'allowContact':
                    return signupForm.allowContact ? 'is-valid' : 'is-invalid'
                case 'readPrivacy':
                    return signupForm.readPrivacy ? 'is-valid' : 'is-invalid'
                default:
                    return ''
            }
        }

        const signupCanSubmit = computed(() => {
            return signupEmailValid.value
                && signupEmailConfirmValid.value
                && signupForm.allowContact
                && signupForm.readPrivacy
                && !signupForm.loading
        })

        // --- Touch handlers ---
        const touchLogin = () => {
            loginTouched.value = true
        }

        const touchSignup = (field) => {
            signupTouched[field] = true
            // Re-validate email confirm when email changes
            if (field === 'email' && signupTouched.emailConfirm) {
                // Force reactivity update (already handled by computed)
            }
        }

        // --- API calls ---
        const requestMagicLink = async () => {
            if (!loginCanSubmit.value) return
            loginForm.loading = true
            loginForm.error = ''
            try {
                const response = await fetch(window.rockon_api.requestMagicLink, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': window.rockon_api.csrfToken,
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({ email: loginForm.email }),
                })
                if (response.ok) {
                    loginForm.sent = true
                } else {
                    loginForm.error = 'unknown'
                }
            } catch (err) {
                console.error('Magic link request failed:', err)
                loginForm.error = 'network'
            } finally {
                loginForm.loading = false
            }
        }

        const createAccount = async () => {
            // Touch all fields to show validation
            Object.keys(signupTouched).forEach(k => signupTouched[k] = true)
            if (!signupCanSubmit.value) return

            signupForm.loading = true
            signupForm.error = ''
            try {
                const payload = {
                    email: signupForm.email,
                    account_context: window.rockon_data.accountContext || 'crew',
                }
                const response = await fetch(window.rockon_api.createAccount, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': window.rockon_api.csrfToken,
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(payload),
                })
                const data = await response.json()
                if (response.ok) {
                    window.location.href = window.rockon_api.accountCreatedRedirect
                } else {
                    if (data && data.status === 'exists') {
                        signupForm.error = 'exists'
                    } else {
                        signupForm.error = 'unknown'
                    }
                }
            } catch (err) {
                console.error('Account creation failed:', err)
                signupForm.error = 'network'
            } finally {
                signupForm.loading = false
            }
        }

        // --- Panel toggle ---
        const setPanel = (panel) => {
            activePanel.value = panel
        }

        // --- Privacy URL (from Django) ---
        const privacyUrl = window.rockon_api.privacyUrl || '#'

        return {
            activePanel,
            setPanel,
            // Login
            loginForm,
            loginTouched,
            loginEmailValid,
            loginEmailClass,
            loginCanSubmit,
            touchLogin,
            requestMagicLink,
            // Signup
            signupForm,
            signupTouched,
            signupFieldClass,
            signupCanSubmit,
            touchSignup,
            createAccount,
            privacyUrl,
        }
    },
}

document.addEventListener('DOMContentLoaded', () => {
    createApp(LoginApp).mount('#app')
})
