/**
 * JavaScript para la lista de invitaciones
 */
document.addEventListener('DOMContentLoaded', function() {
    // Tabs functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            
            // Desactivar todos los tabs
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Activar el tab seleccionado
            this.classList.add('active');
            document.getElementById('tab-' + tabId).classList.add('active');
        });
    });
    
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
});
