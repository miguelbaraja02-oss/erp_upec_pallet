document.addEventListener("DOMContentLoaded", () => {

    const openDrawer = document.getElementById("openDrawer");
    const drawer = document.getElementById("drawer");
    const overlay = document.getElementById("drawerOverlay");

    if (!openDrawer || !drawer || !overlay) return;

    let startY = 0;
    let currentY = 0;
    let isDragging = false;

    function open() {
        drawer.classList.add("open");
        overlay.classList.add("show");
        document.body.style.overflow = "hidden";
    }

    function close() {
        drawer.classList.remove("open");
        overlay.classList.remove("show");
        document.body.style.overflow = "";
        drawer.style.transform = ""; // reset
    }

    openDrawer.addEventListener("click", (e) => {
        e.preventDefault();
        open();
    });

    // Toggle active state for the 'Pallet' button so it stays yellow when selected
    const palletBtn = document.querySelector('.nav-btn[aria-label="Pallet"]');
    if (palletBtn) {
        // Set active on pallet when clicked, and remove when clicking anywhere else
        palletBtn.addEventListener('click', (ev) => {
            ev.stopPropagation();
            // remove active from all nav-btns first to keep single active
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            palletBtn.classList.add('active');
        });

        // Remove active when clicking other nav buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            if (btn === palletBtn) return;
            btn.addEventListener('click', () => {
                palletBtn.classList.remove('active');
            });
        });

        // Remove active when clicking anywhere outside the nav buttons
        document.addEventListener('click', (ev) => {
            if (!ev.target.closest || !ev.target.closest('.nav-btn')) {
                palletBtn.classList.remove('active');
            }
        });
    }

    overlay.addEventListener("click", close);

    // SWIPE
    drawer.addEventListener("touchstart", (e) => {
        startY = e.touches[0].clientY;
        isDragging = true;
    }, { passive: true });

    drawer.addEventListener("touchmove", (e) => {
        if (!isDragging) return;

        currentY = e.touches[0].clientY;
        const diff = currentY - startY;

        if (diff > 0) {
            drawer.style.transform = `translateY(${diff}px)`;
        }
    }, { passive: true });

    drawer.addEventListener("touchend", () => {
        if (!isDragging) return;

        const diff = currentY - startY;

        if (diff > 120) {
            close();
        } else {
            drawer.style.transform = "";
        }

        startY = 0;
        currentY = 0;
        isDragging = false;
    });

    // --- User avatar menu (ribbon) ---
    const userMenuBtn = document.querySelector('.user-menu-btn');
    const userMenuRibbon = document.getElementById('userMenuRibbon');

    if (userMenuBtn && userMenuRibbon) {
        function closeUserMenu() {
            userMenuRibbon.classList.remove('show');
            userMenuRibbon.setAttribute('aria-hidden', 'true');
            userMenuBtn.setAttribute('aria-expanded', 'false');
        }

        function openUserMenu() {
            userMenuRibbon.classList.add('show');
            userMenuRibbon.setAttribute('aria-hidden', 'false');
            userMenuBtn.setAttribute('aria-expanded', 'true');
        }

        userMenuBtn.addEventListener('click', (ev) => {
            ev.stopPropagation();
            // toggle
            if (userMenuRibbon.classList.contains('show')) {
                closeUserMenu();
            } else {
                // close other nav active states
                document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
                openUserMenu();
            }
        });

        // También permitir que al pulsar la etiqueta "Perfil" (texto bajo el avatar)
        // se abra/cierre el menú. Selector: botón seguido de la etiqueta.
        const userNavLabel = document.querySelector('.user-menu-btn + .nav-label');
        if (userNavLabel) {
            userNavLabel.addEventListener('click', (ev) => {
                ev.preventDefault();
                ev.stopPropagation();
                // Reutilizar la lógica del botón
                if (userMenuRibbon.classList.contains('show')) {
                    closeUserMenu();
                } else {
                    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
                    openUserMenu();
                }
            });
        }

        // Close when clicking outside
        document.addEventListener('click', (ev) => {
            if (!ev.target.closest || !ev.target.closest('#userMenuRibbon')) {
                closeUserMenu();
            }
        });

        // Close when selecting a menu item
        userMenuRibbon.querySelectorAll('.user-menu-item').forEach(it => {
            it.addEventListener('click', () => {
                closeUserMenu();
            });
        });
    }

});
