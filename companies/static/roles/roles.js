/**
 * JavaScript para la lista de roles
 */
document.addEventListener('DOMContentLoaded', function() {
    // Auto-cerrar alertas después de 5 segundos
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
    });
    
    // Inicializar búsqueda de usuarios para asignar rol
    initUserSearch();
});


// ================================
// BÚSQUEDA Y ASIGNACIÓN DE USUARIOS
// ================================

let selectedUser = null;
let searchTimeout = null;

function initUserSearch() {
    const searchInput = document.getElementById('searchUserInput');
    const searchResults = document.getElementById('userSearchResults');
    const selectedContainer = document.getElementById('selectedUserContainer');
    const clearBtn = document.getElementById('clearSelectedUser');
    const assignBtn = document.getElementById('assignRoleBtn');
    const roleSelect = document.getElementById('roleSelectAssign');
    
    if (!searchInput) return;
    
    // Búsqueda con debounce
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            searchResults.classList.remove('show');
            return;
        }
        
        searchTimeout = setTimeout(() => {
            searchUsers(query);
        }, 300);
    });
    
    // Cerrar resultados al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.remove('show');
        }
    });
    
    // Limpiar usuario seleccionado
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            clearSelectedUser();
        });
    }
    
    // Asignar rol
    if (assignBtn) {
        assignBtn.addEventListener('click', function() {
            if (!selectedUser) {
                showToast('Selecciona un usuario primero', 'error');
                return;
            }
            
            const roleId = roleSelect.value;
            assignRoleToUser(selectedUser.id, roleId);
        });
    }
}

function searchUsers(query) {
    const searchResults = document.getElementById('userSearchResults');
    
    fetch(`/companies/users/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderSearchResults(data.users);
            }
        })
        .catch(error => {
            console.error('Error buscando usuarios:', error);
        });
}

function renderSearchResults(users) {
    const searchResults = document.getElementById('userSearchResults');
    
    if (users.length === 0) {
        searchResults.innerHTML = `
            <div class="search-no-results">
                <i class="fas fa-search"></i>
                <p>No se encontraron usuarios</p>
            </div>
        `;
        searchResults.classList.add('show');
        return;
    }
    
    let html = '';
    users.forEach(user => {
        const roleClass = user.role_name ? 'has-role' : '';
        const roleText = user.role_name || 'Sin rol';
        
        html += `
            <div class="search-result-item" data-user='${JSON.stringify(user)}'>
                <div class="user-avatar">
                    ${user.avatar 
                        ? `<img src="${user.avatar}" alt="Avatar">` 
                        : '<i class="fas fa-user"></i>'
                    }
                </div>
                <div class="user-info">
                    <div class="user-name">${user.full_name}</div>
                    <div class="user-email">@${user.username} · ${user.email}</div>
                </div>
                <span class="current-role ${roleClass}">${roleText}</span>
            </div>
        `;
    });
    
    searchResults.innerHTML = html;
    searchResults.classList.add('show');
    
    // Agregar event listeners a los resultados
    searchResults.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', function() {
            const userData = JSON.parse(this.dataset.user);
            selectUser(userData);
        });
    });
}

function selectUser(user) {
    selectedUser = user;
    
    const searchInput = document.getElementById('searchUserInput');
    const searchResults = document.getElementById('userSearchResults');
    const selectedContainer = document.getElementById('selectedUserContainer');
    const selectedUserAvatar = document.getElementById('selectedUserAvatar');
    const selectedUserInfo = document.getElementById('selectedUserInfo');
    const roleSelect = document.getElementById('roleSelectAssign');
    
    // Ocultar búsqueda
    searchInput.value = '';
    searchResults.classList.remove('show');
    
    // Mostrar usuario seleccionado
    selectedUserAvatar.innerHTML = user.avatar 
        ? `<img src="${user.avatar}" alt="Avatar">` 
        : '<i class="fas fa-user"></i>';
    
    selectedUserInfo.innerHTML = `
        <div class="name">${user.full_name}</div>
        <div class="username">@${user.username}</div>
    `;
    
    // Pre-seleccionar el rol actual
    if (user.role_id) {
        roleSelect.value = user.role_id;
    } else {
        roleSelect.value = '';
    }
    
    selectedContainer.style.display = 'flex';
}

function clearSelectedUser() {
    selectedUser = null;
    
    const selectedContainer = document.getElementById('selectedUserContainer');
    const roleSelect = document.getElementById('roleSelectAssign');
    
    selectedContainer.style.display = 'none';
    roleSelect.value = '';
}

function assignRoleToUser(companyUserId, roleId) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                      getCookie('csrftoken');
    
    fetch(`/companies/users/${companyUserId}/assign-role/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ role_id: roleId || null })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            clearSelectedUser();
            
            // Recargar la página para actualizar los contadores
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showToast(data.error || 'Error al asignar el rol', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error de conexión', 'error');
    });
}

function showToast(message, type) {
    // Remover toast existente
    const existingToast = document.querySelector('.toast-message');
    if (existingToast) {
        existingToast.remove();
    }
    
    const toast = document.createElement('div');
    toast.className = `toast-message ${type}`;
    toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${message}`;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
