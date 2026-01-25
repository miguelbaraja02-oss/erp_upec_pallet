document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Sidebar Toggle (Móvil)
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.erp-main');

    if(sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.stopPropagation(); // Evitar cierre inmediato
            sidebar.classList.toggle('active');
        });
    }

    // Cerrar sidebar al hacer click fuera en móvil
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });

    // 2. User Dropdown
    window.toggleUserMenu = function() {
        const menu = document.getElementById('userMenuContent');
        menu.classList.toggle('show');
    }

    // Cerrar dropdown al hacer click fuera
    window.addEventListener('click', function(e) {
        if (!e.target.closest('.user-dropdown')) {
            const menu = document.getElementById('userMenuContent');
            if (menu && menu.classList.contains('show')) {
                menu.classList.remove('show');
            }
        }
    });

});