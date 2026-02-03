/**
 * JavaScript para crear invitaciones (búsqueda de usuarios)
 */
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('userSearch');
    const searchResults = document.getElementById('searchResults');
    const searchSpinner = document.getElementById('searchSpinner');
    const selectedUser = document.getElementById('selectedUser');
    const selectedUserId = document.getElementById('selectedUserId');
    const selectedName = document.getElementById('selectedName');
    const selectedEmail = document.getElementById('selectedEmail');
    const selectedAvatar = document.getElementById('selectedAvatar');
    const clearSelection = document.getElementById('clearSelection');
    const messageGroup = document.getElementById('messageGroup');
    const submitBtn = document.getElementById('submitBtn');
    
    let searchTimeout = null;
    
    // Búsqueda de usuarios
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            searchResults.innerHTML = '';
            return;
        }
        
        searchSpinner.classList.add('active');
        
        searchTimeout = setTimeout(() => {
            fetch(`${SEARCH_URL}?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    searchSpinner.classList.remove('active');
                    
                    if (data.success && data.users.length > 0) {
                        renderSearchResults(data.users);
                    } else {
                        searchResults.innerHTML = `
                            <div class="empty-state" style="padding: 1rem;">
                                <p style="color: #6c757d; margin: 0;">No se encontraron usuarios</p>
                            </div>
                        `;
                    }
                })
                .catch(error => {
                    searchSpinner.classList.remove('active');
                    console.error('Error:', error);
                });
        }, 300);
    });
    
    // Renderizar resultados de búsqueda
    function renderSearchResults(users) {
        let html = '';
        
        users.forEach(user => {
            const statusHtml = user.is_member 
                ? '<span class="result-status member">Ya es miembro</span>'
                : user.has_pending 
                    ? '<span class="result-status pending">Invitación pendiente</span>'
                    : '';
            
            const disabledClass = !user.can_invite ? 'disabled' : '';
            const clickHandler = user.can_invite ? `onclick="selectUser(${JSON.stringify(user).replace(/"/g, '&quot;')})"` : '';
            
            html += `
                <div class="search-result-item ${disabledClass}" ${clickHandler}>
                    <div class="result-avatar">
                        ${user.avatar 
                            ? `<img src="${user.avatar}" alt="${user.username}">`
                            : `<i class="fas fa-user"></i>`
                        }
                    </div>
                    <div class="result-info">
                        <div class="name">${user.full_name} <span style="color: #4361ee;">@${user.username}</span></div>
                        <div class="email">${user.email}</div>
                    </div>
                    ${statusHtml}
                </div>
            `;
        });
        
        searchResults.innerHTML = html;
    }
    
    // Seleccionar usuario (función global para onclick)
    window.selectUser = function(user) {
        selectedUserId.value = user.id;
        selectedName.textContent = `${user.full_name} (@${user.username})`;
        selectedEmail.textContent = user.email;
        
        if (user.avatar) {
            selectedAvatar.innerHTML = `<img src="${user.avatar}" alt="${user.username}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
        } else {
            selectedAvatar.innerHTML = `<i class="fas fa-user"></i>`;
        }
        
        selectedUser.style.display = 'block';
        messageGroup.style.display = 'block';
        submitBtn.disabled = false;
        
        searchResults.innerHTML = '';
        searchInput.value = '';
    };
    
    // Limpiar selección
    clearSelection.addEventListener('click', function() {
        selectedUserId.value = '';
        selectedUser.style.display = 'none';
        messageGroup.style.display = 'none';
        submitBtn.disabled = true;
    });
});
