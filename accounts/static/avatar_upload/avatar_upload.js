document.addEventListener('DOMContentLoaded', function() {
    
    const fileInput = document.querySelector('input[type="file"]');
    const previewImg = document.getElementById('avatar-preview');
    const previewDefault = document.getElementById('avatar-preview-default'); // Referencia al icono
    const imageToCrop = document.getElementById('image-to-crop');
    const fileNameSpan = document.getElementById('file-name');
    
    const cropModalEl = document.getElementById('cropModal');
    const cropModal = new bootstrap.Modal(cropModalEl);
    const cropBtn = document.getElementById('btn-crop');

    let cropper = null;

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];

            if (file) {
                if (!file.type.startsWith('image/')) {
                    alert('Por favor selecciona un archivo de imagen válido.');
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(evt) {
                    imageToCrop.src = evt.target.result;
                    cropModal.show();
                }
                reader.readAsDataURL(file);
            }
        });
    }

    cropModalEl.addEventListener('shown.bs.modal', function () {
        cropper = new Cropper(imageToCrop, {
            aspectRatio: 1, 
            viewMode: 2,
            autoCropArea: 1,
            responsive: true,
        });
    });

    cropModalEl.addEventListener('hidden.bs.modal', function () {
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
        // Limpiar el input si cancela para poder seleccionar la misma foto de nuevo
        if (!fileNameSpan.textContent.includes("lista")) {
             fileInput.value = '';
        }
    });

    cropBtn.addEventListener('click', function() {
        if (cropper) {
            const canvas = cropper.getCroppedCanvas({
                width: 400,
                height: 400,
            });

            canvas.toBlob(function(blob) {
                const url = URL.createObjectURL(blob);
                
                // --- LÓGICA DE CAMBIO VISUAL ---
                // 1. Ocultar el icono por defecto si existe
                if (previewDefault) previewDefault.style.display = 'none';
                
                // 2. Mostrar la imagen y asignar el src
                previewImg.style.display = 'block';
                previewImg.src = url;
                // -------------------------------

                const newFile = new File([blob], "avatar_recortado.png", { type: "image/png" });
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(newFile);
                fileInput.files = dataTransfer.files;

                fileNameSpan.textContent = "Imagen recortada lista";
                fileNameSpan.style.color = "#006633";
                fileNameSpan.style.fontWeight = "bold";

                cropModal.hide();

            }, 'image/png');
        }
    });
});