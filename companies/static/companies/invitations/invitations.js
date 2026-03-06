// invitations.js - AJAX búsqueda y tarjetas de invitación

document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('user-search');
    const results = document.getElementById('user-results');
    const companyId = input ? input.dataset.companyId : null;
    let timeout = null;

    if (!input || !results || !companyId) return;

    input.addEventListener('input', function() {
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            const query = input.value;
            if (!query) {
                results.innerHTML = '';
                return;
            }
            fetch(`/companies/${companyId}/search_users/?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    results.innerHTML = '';
                    if (data.users.length === 0) {
                        results.innerHTML = '<div class="user-card">No hay resultados</div>';
                        return;
                    }
                    data.users.forEach(user => {
                        const form = document.createElement('form');
                        form.className = 'user-card';
                        form.method = 'post';
                        form.action = `/companies/${companyId}/invite/`;
                        form.innerHTML = `
                            <input type='hidden' name='username' value='${user.username}'>
                            <div class='user-card-username'>${user.username}</div>
                            <div class='user-card-email'>${user.email}</div>
                            <button type='submit' class='user-card-invite-btn'>Invitar</button>
                            <input type='hidden' name='csrfmiddlewaretoken' value='${window.csrfToken}'>
                        `;
                        results.appendChild(form);
                    });
                })
                .catch(() => {
                    results.innerHTML = '<div class="user-card">Error al buscar usuarios</div>';
                });
        }, 300);
    });
});
