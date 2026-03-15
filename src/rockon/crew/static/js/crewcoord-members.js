document.addEventListener('DOMContentLoaded', () => {
    const stateSelects = document.querySelectorAll('select[data-autosubmit-state]')

    stateSelects.forEach((select) => {
        select.addEventListener('change', () => {
            const form = select.form
            if (!form) {
                return
            }

            if (typeof form.requestSubmit === 'function') {
                form.requestSubmit()
                return
            }

            form.submit()
        })
    })
})
