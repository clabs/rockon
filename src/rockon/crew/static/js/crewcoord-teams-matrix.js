document.addEventListener('DOMContentLoaded', () => {
    const matrix = document.getElementById('crewcoord-teams-matrix')
    if (!matrix) {
        return
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
    const slug = matrix.dataset.eventSlug

    const STATE_ORDER = ['unknown', 'confirmed', 'rejected']
    const STATE_ICON = {unknown: 'fa-question', confirmed: 'fa-check', rejected: 'fa-xmark'}
    const STATE_BUTTON_CLASS = {unknown: 'btn-secondary', confirmed: 'btn-success', rejected: 'btn-danger'}
    const STATE_LABEL = {unknown: 'Unbekannt', confirmed: 'Bestätigt', rejected: 'Abgelehnt'}

    const applyState = (button, state) => {
        button.dataset.state = state
        const icon = button.querySelector('i')
        icon.className = `fa-solid ${STATE_ICON[state]}`
        Object.values(STATE_BUTTON_CLASS).forEach((cls) => button.classList.remove(cls))
        button.classList.add(STATE_BUTTON_CLASS[state])
        button.title = STATE_LABEL[state]
        const memberName = button.dataset.memberName || ''
        const teamName = button.dataset.teamName || ''
        button.setAttribute('aria-label', `${memberName} ${teamName} – ${STATE_LABEL[state]}`)
    }

    const errorEl = matrix.querySelector('.crewcoord-teams-matrix-error')

    matrix.addEventListener('click', async (event) => {
        const button = event.target.closest('.team-cell-btn')
        if (!button) {
            return
        }

        const nextState = STATE_ORDER[(STATE_ORDER.indexOf(button.dataset.state) + 1) % STATE_ORDER.length]

        errorEl?.classList.add('d-none')
        button.disabled = true

        try {
            const response = await fetch(`/api/v2/team-members/${slug}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    event_team_id: button.dataset.eventTeamId,
                    crewmember_id: button.dataset.crewmemberId,
                    state: nextState
                })
            })

            if (!response.ok) {
                throw new Error(`Unexpected status ${response.status}`)
            }

            applyState(button, nextState)
        } catch (error) {
            console.error('Failed to update team member state', error)
            if (errorEl) {
                errorEl.textContent = 'Status konnte nicht gespeichert werden.'
                errorEl.classList.remove('d-none')
            }
        } finally {
            button.disabled = false
        }
    })
})
