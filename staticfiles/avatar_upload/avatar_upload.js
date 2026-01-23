document.addEventListener('DOMContentLoaded', function() {
    
    // Elementos del DOM
    const fileInput = document.querySelector('input[type="file"]'); // El input de Django
    const previewImg = document.getElementById('avatar-preview');   // El círculo visual
    const imageToCrop = document.getElementById('image-to-crop');   // Imagen dentro del modal
    const fileNameSpan = document.getElementById('file-name');      // Texto del label
    
    // Elementos del Modal
    const cropModalEl = document.getElementById('cropModal');
    const cropModal = new bootstrap.Modal(cropModalEl);
    const cropBtn = document.getElementById('btn-crop');

    let cropper = null; // Variable para guardar la instancia de Cropper

    // 1. Cuando el usuario selecciona un archivo
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];

            if (file) {
                // Verificar que sea una imagen
                if (!file.type.startsWith('image/')) {
                    alert('Por favor selecciona un archivo de imagen válido.');
                    return;
                }

                // Leer el archivo para mostrarlo en el modal
                const reader = new FileReader();
                reader.onload = function(evt) {
                    // Asignar la imagen al elemento dentro del modal
                    imageToCrop.src = evt.target.result;
                    
                    // Abrir el modal
                    cropModal.show();
                }
                reader.readAsDataURL(file);
                
                // Resetear el valor del input para permitir seleccionar la misma imagen si se cancela
                // (Lo restauraremos después si confirma el recorte)
                // fileInput.value = ''; 
            }
        });
    }

    // 2. Al abrirse el modal, iniciar Cropper.js
    cropModalEl.addEventListener('shown.bs.modal', function () {
        cropper = new Cropper(imageToCrop, {
            aspectRatio: 1, // 1:1 para que sea cuadrado/circular
            viewMode: 2,    // Restringe el cuadro de recorte dentro de la imagen
            autoCropArea: 1,
            responsive: true,
        });
    });

    // 3. Al cerrarse el modal, destruir Cropper para limpiar memoria
    cropModalEl.addEventListener('hidden.bs.modal', function () {
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
    });

    // 4. AL PULSAR "RECORTAR Y USAR"
    cropBtn.addEventListener('click', function() {
        if (cropper) {
            // Obtener el canvas recortado
            const canvas = cropper.getCroppedCanvas({
                width: 400,  // Redimensionar para optimizar (opcional)
                height: 400,
            });

            // Convertir el canvas a un Blob (archivo)
            canvas.toBlob(function(blob) {
                
                // A. Actualizar la vista previa (círculo)
                const url = URL.createObjectURL(blob);
                previewImg.src = url;

                // B. Reemplazar el archivo en el input original
                // Esto es un truco "Pro": Creamos un nuevo objeto File y lo metemos en el input
                const newFile = new File([blob], "avatar_recortado.png", { type: "image/png" });
                
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(newFile);
                fileInput.files = dataTransfer.files;

                // C. Actualizar texto
                fileNameSpan.textContent = "Imagen recortada lista";
                fileNameSpan.style.color = "#006633";
                fileNameSpan.style.fontWeight = "bold";

                // Cerrar modal
                cropModal.hide();

            }, 'image/png');
        }
    });
});