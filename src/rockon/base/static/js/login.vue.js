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
        const emailRegex = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/

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

        // --- Passkey ---
        const passkeySupported = ref(typeof window !== 'undefined' && !!window.PublicKeyCredential)
        const passkeyLoading = ref(false)
        const passkeyError = ref('')
        // True when browser handles passkey via autofill — explicit button becomes redundant
        const passkeyConditional = ref(false)

        const _b64urlToBuffer = (b64url) => {
            const padded = b64url.replace(/-/g, '+').replace(/_/g, '/')
            const bin = atob(padded.padEnd(padded.length + (4 - padded.length % 4) % 4, '='))
            return Uint8Array.from(bin, c => c.charCodeAt(0)).buffer
        }

        const _bufferToB64url = (buf) => {
            return btoa(String.fromCharCode(...new Uint8Array(buf)))
                .replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
        }

        // Shared: serialize a PublicKeyCredential assertion and call auth/complete
        const _completeAuth = async (credential) => {
            const credJson = {
                id: credential.id,
                rawId: credential.id,
                type: credential.type,
                response: {
                    authenticatorData: _bufferToB64url(credential.response.authenticatorData),
                    clientDataJSON: _bufferToB64url(credential.response.clientDataJSON),
                    signature: _bufferToB64url(credential.response.signature),
                    userHandle: credential.response.userHandle
                        ? _bufferToB64url(credential.response.userHandle)
                        : null,
                },
            }
            const resp = await fetch(window.rockon_api.passkeyAuthComplete, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.rockon_api.csrfToken,
                },
                credentials: 'same-origin',
                body: JSON.stringify({ credential: credJson }),
            })
            return resp.ok
        }

        // Fetch a fresh challenge from the server
        const _fetchAuthOptions = async () => {
            const resp = await fetch(window.rockon_api.passkeyAuthBegin, {
                method: 'POST',
                headers: { 'X-CSRFToken': window.rockon_api.csrfToken },
                credentials: 'same-origin',
            })
            if (!resp.ok) return null
            const { options } = await resp.json()
            return {
                ...options,
                challenge: _b64urlToBuffer(options.challenge),
                allowCredentials: (options.allowCredentials || []).map(c => ({
                    ...c, id: _b64urlToBuffer(c.id),
                })),
            }
        }

        // Abort controller for the conditional (autofill) request
        let _conditionalAbort = null

        // Start conditional UI: browser shows passkey suggestion in email autofill
        const startConditionalPasskey = async () => {
            if (!window.PublicKeyCredential) return
            const available = await PublicKeyCredential.isConditionalMediationAvailable?.()
            if (!available) return

            passkeyConditional.value = true
            _conditionalAbort = new AbortController()

            try {
                const publicKey = await _fetchAuthOptions()
                if (!publicKey) return

                const credential = await navigator.credentials.get({
                    publicKey,
                    mediation: 'conditional',
                    signal: _conditionalAbort.signal,
                })
                if (!credential) return

                const ok = await _completeAuth(credential)
                if (ok) window.location.href = window.rockon_api.passkeyLoginRedirect
                else passkeyError.value = 'auth_failed'
            } catch (err) {
                if (err.name !== 'AbortError') {
                    console.error('Conditional passkey failed:', err)
                }
            }
        }

        // Explicit button: abort conditional flow, show native modal picker
        const signInWithPasskey = async () => {
            _conditionalAbort?.abort()
            _conditionalAbort = null

            passkeyLoading.value = true
            passkeyError.value = ''
            try {
                const publicKey = await _fetchAuthOptions()
                if (!publicKey) throw new Error('begin failed')

                const credential = await navigator.credentials.get({ publicKey })
                if (!credential) throw new Error('No credential returned')

                const ok = await _completeAuth(credential)
                if (ok) {
                    window.location.href = window.rockon_api.passkeyLoginRedirect
                } else {
                    passkeyError.value = 'auth_failed'
                }
            } catch (err) {
                if (err.name === 'NotAllowedError') {
                    // User cancelled — restart conditional UI for next autofill attempt
                    startConditionalPasskey()
                } else {
                    console.error('Passkey sign-in failed:', err)
                    passkeyError.value = 'network'
                }
            } finally {
                passkeyLoading.value = false
            }
        }

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
            // Passkey
            passkeySupported,
            passkeyLoading,
            passkeyError,
            passkeyConditional,
            signInWithPasskey,
            startConditionalPasskey,
        }
    },
}

document.addEventListener('DOMContentLoaded', () => {
    const app = createApp(LoginApp)
    const instance = app.mount('#app')
    instance.startConditionalPasskey()
})
