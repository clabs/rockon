document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('crew-dates-sidebar')
    if (!sidebar) {
        return
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value

    const highlightActiveButton = (card, status) => {
        card.querySelectorAll('.rsvp-btn').forEach((button) => {
            button.classList.toggle('active', button.dataset.status === status)
        })
    }

    sidebar.querySelectorAll('.crew-date-rsvp').forEach((card) => {
        highlightActiveButton(card, card.dataset.status)
    })

    sidebar.addEventListener('click', async (event) => {
        const button = event.target.closest('.rsvp-btn')
        if (!button) {
            return
        }

        const card = button.closest('.crew-date-rsvp')
        const errorEl = card.querySelector('.crew-date-rsvp-error')
        const status = button.dataset.status
        const crewDateId = card.dataset.crewDateId

        errorEl.classList.add('d-none')
        card.querySelectorAll('.rsvp-btn').forEach((btn) => (btn.disabled = true))

        try {
            const response = await fetch('/api/v2/crew-date-responses/', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({crew_date: crewDateId, status: status})
            })

            if (!response.ok) {
                throw new Error(`Unexpected status ${response.status}`)
            }

            card.dataset.status = status
            highlightActiveButton(card, status)
        } catch (error) {
            console.error('Failed to submit RSVP', error)
            errorEl.textContent = 'Rückmeldung konnte nicht gespeichert werden.'
            errorEl.classList.remove('d-none')
        } finally {
            card.querySelectorAll('.rsvp-btn').forEach((btn) => (btn.disabled = false))
        }
    })
})
