document.addEventListener("DOMContentLoaded", function() {
    
    // 1. Limpieza visual de textos de ayuda de Django (opcional)
    // A veces Django pone textos como "El usuario debe tener..." que se ven feos.
    const helpTexts = document.querySelectorAll('.helptext');
    helpTexts.forEach(text => {
        text.classList.add('text-muted', 'small', 'mt-1', 'd-block');
        text.style.fontSize = '0.8rem';
    });

    // 2. Efecto de foco en labels
    // Cuando el usuario entra a un input, resaltamos el label correspondiente
    const inputs = document.querySelectorAll('.django-form-content input, .django-form-content textarea');
    
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            const label = input.previousElementSibling; // Asumiendo que el label está justo antes (as_p)
            if (label && label.tagName === 'LABEL') {
                label.style.color = '#006633';
            }
        });

        input.addEventListener('blur', () => {
            const label = input.previousElementSibling;
            if (label && label.tagName === 'LABEL') {
                label.style.color = '#555';
            }
        });
    });
});