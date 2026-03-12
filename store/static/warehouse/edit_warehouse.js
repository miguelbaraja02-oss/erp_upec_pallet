// Animación de entrada para la card de edición de almacén
// Aplica fade-in y slide-up al cargar la página

document.addEventListener('DOMContentLoaded', function() {
    const card = document.querySelector('.edit-card');
    if (card) {
        // Forzar repintado y añadir la clase tras un pequeño delay
        setTimeout(() => {
            card.classList.add('animate-in');
        }, 100);
    }
});
