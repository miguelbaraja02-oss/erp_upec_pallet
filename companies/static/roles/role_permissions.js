/**
 * JavaScript para la gestión de permisos de roles
 */
document.addEventListener('DOMContentLoaded', function() {
    const table = document.getElementById('permissionsTable');
    if (!table) return;
    
    const roleId = table.dataset.roleId;
    
    // Manejar cambios en los checkboxes
    const checkboxes = table.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            togglePermission(this);
        });
    });
    
    // Función para activar/desactivar permiso
    async function togglePermission(checkbox) {
        const moduleId = checkbox.dataset.moduleId;
        const permissionTypeId = checkbox.dataset.permissionTypeId;
        
        // Deshabilitar temporalmente
        checkbox.disabled = true;
        
        try {
            const response = await fetch(TOGGLE_PERMISSION_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF_TOKEN,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    module_id: parseInt(moduleId),
                    permission_type_id: parseInt(permissionTypeId)
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                checkbox.checked = data.has_permission;
                showToast('Permiso actualizado', 'El permiso se ha actualizado correctamente.', 'success');
            } else {
                // Revertir el cambio
                checkbox.checked = !checkbox.checked;
                showToast('Error', data.error || 'No se pudo actualizar el permiso.', 'error');
            }
        } catch (error) {
            // Revertir el cambio
            checkbox.checked = !checkbox.checked;
            showToast('Error', 'Error de conexión. Intenta nuevamente.', 'error');
            console.error('Error:', error);
        } finally {
            checkbox.disabled = false;
        }
    }
    
    // Función para mostrar toast
    function showToast(title, message, type) {
        const toast = document.getElementById('permissionToast');
        const toastTitle = document.getElementById('toastTitle');
        const toastMessage = document.getElementById('toastMessage');
        const toastIcon = document.getElementById('toastIcon');
        
        if (!toast) return;
        
        toastTitle.textContent = title;
        toastMessage.textContent = message;
        
        // Cambiar icono según el tipo
        toastIcon.className = type === 'success' 
            ? 'fas fa-check-circle text-success me-2'
            : 'fas fa-exclamation-circle text-danger me-2';
        
        // Mostrar toast con Bootstrap
        const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
        bsToast.show();
    }
    
    // Botón: Seleccionar todos
    const selectAllBtn = document.getElementById('selectAll');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            setAllPermissions(true);
        });
    }
    
    // Botón: Deseleccionar todos
    const deselectAllBtn = document.getElementById('deselectAll');
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', function() {
            setAllPermissions(false);
        });
    }
    
    // Botón: Solo ver (solo permisos de "view")
    const selectViewBtn = document.getElementById('selectView');
    if (selectViewBtn) {
        selectViewBtn.addEventListener('click', function() {
            // Primero deseleccionar todos
            checkboxes.forEach(cb => {
                if (cb.checked) {
                    cb.click();
                }
            });
            
            // Luego seleccionar solo los de "view" (asumiendo que el primer tipo es view)
            setTimeout(() => {
                const viewCheckboxes = table.querySelectorAll('input[data-permission-type-id="1"]');
                viewCheckboxes.forEach(cb => {
                    if (!cb.checked) {
                        cb.click();
                    }
                });
            }, 500);
        });
    }
    
    // Función para establecer todos los permisos
    function setAllPermissions(checked) {
        let delay = 0;
        checkboxes.forEach(checkbox => {
            if (checkbox.checked !== checked) {
                setTimeout(() => {
                    checkbox.click();
                }, delay);
                delay += 100; // Pequeño delay entre cada petición
            }
        });
    }
});
