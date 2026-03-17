// Animación de aparición secuencial para las cards de rack
// Se adapta a móvil automáticamente

document.addEventListener('DOMContentLoaded', function () {
    const cards = document.querySelectorAll('.rack-card');
    const isMobile = window.matchMedia('(max-width: 768px)').matches;

    // Reset styles and force reflow for animación
    cards.forEach(card => {
        card.style.transition = 'none';
        card.style.opacity = 0;
        if (isMobile) {
            card.style.transform = 'translateX(60vw)';
        } else {
            card.style.transform = 'translateY(40px)';
        }
    });
    // Force reflow
    void document.body.offsetHeight;
    // Set transition
    cards.forEach(card => {
        card.style.transition = 'opacity 0.6s cubic-bezier(0.4,0,0.2,1), transform 0.6s cubic-bezier(0.4,0,0.2,1)';
    });

    function animateCards() {
        cards.forEach((card, i) => {
            setTimeout(() => {
                card.style.opacity = 1;
                card.style.transform = 'translateX(0) translateY(0)';
            }, i * 180);
        });
    }

    if (cards.length > 0) {
        animateCards();
    }
});
