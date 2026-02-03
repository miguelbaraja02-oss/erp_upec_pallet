// ================================
// USUARIOS DE EMPRESA - JAVASCRIPT
// ================================

document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    initActionsDropdowns();
    initAssignRoleModal();
    initRemoveUserModal();
});

// Tabs
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;

            // Remove active from all
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active to clicked
            btn.classList.add('active');
            document.getElementById(`tab-${tabId}`).classList.add('active');
        });
    });
}

// Actions dropdowns (toggle on click)
function initActionsDropdowns() {
    const dropdowns = document.querySelectorAll('.actions-dropdown');
    
    dropdowns.forEach(dropdown => {
        const btn = dropdown.querySelector('.actions-btn');
        
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            
            // Close other dropdowns
            dropdowns.forEach(d => {
                if (d !== dropdown) d.classList.remove('open');
            });
            
            dropdown.classList.toggle('open');
        });
    });
    
    // Close on click outside
    document.addEventListener('click', () => {
        dropdowns.forEach(d => d.classList.remove('open'));
    });
}

// Modal para asignar rol
function initAssignRoleModal() {
    const modal = document.getElementById('assignRoleModal');
    const closeBtn = document.getElementById('closeRoleModal');
    const cancelBtn = document.getElementById('cancelRoleBtn');
    const form = document.getElementById('assignRoleForm');
    const userNameSpan = document.getElementById('assignRoleUserName');
    const roleSelect = document.getElementById('roleSelect');
    const assignBtns = document.querySelectorAll('.assign-role-btn');
    
    let currentUserId = null;
    
    // Open modal
    assignBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            currentUserId = btn.dataset.userId;
            const userName = btn.dataset.userName;
            const currentRole = btn.dataset.currentRole;
            
            userNameSpan.textContent = userName;
            roleSelect.value = currentRole || '';
            form.action = `/companies/users/${currentUserId}/assign-role/`;
            
            modal.classList.add('show');
        });
    });
    
    // Close modal
    function closeModal() {
        modal.classList.remove('show');
        currentUserId = null;
    }
    
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('show')) {
            closeModal();
        }
    });
}

// Modal para eliminar usuario
function initRemoveUserModal() {
    const modal = document.getElementById('removeUserModal');
    const closeBtn = document.getElementById('closeRemoveModal');
    const cancelBtn = document.getElementById('cancelRemoveBtn');
    const form = document.getElementById('removeUserForm');
    const userNameSpan = document.getElementById('removeUserName');
    const removeBtns = document.querySelectorAll('.remove-user-btn');
    
    // Open modal
    removeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const userId = btn.dataset.userId;
            const userName = btn.dataset.userName;
            
            userNameSpan.textContent = userName;
            form.action = `/companies/users/${userId}/remove/`;
            
            modal.classList.add('show');
        });
    });
    
    // Close modal
    function closeModal() {
        modal.classList.remove('show');
    }
    
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('show')) {
            closeModal();
        }
    });
}
