document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('input[type="file"]');
    const dropZone = document.getElementById('drop-zone');
    const cameraIconEl = document.querySelector('.camera-icon');
    const previewImg = document.getElementById('avatar-preview');
    const previewDefault = document.getElementById('avatar-preview-default');
    const imageToCrop = document.getElementById('image-to-crop');
    const fileNameSpan = document.getElementById('file-name');
    
    const cropModalEl = document.getElementById('cropModal');
    const cropModal = new bootstrap.Modal(cropModalEl);
    const cropBtn = document.getElementById('btn-crop');

    let cropper = null;

    // Solo abrir selector al pulsar el icono de cámara
    if (cameraIconEl) {
        cameraIconEl.style.cursor = 'pointer';
        cameraIconEl.addEventListener('click', function(e) {
            e.stopPropagation();
            fileInput.click();
        });
    }

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(evt) {
                imageToCrop.src = evt.target.result;
                cropModal.show();
            }
            reader.readAsDataURL(file);
        }
    });

    cropModalEl.addEventListener('shown.bs.modal', function () {
        cropper = new Cropper(imageToCrop, {
            aspectRatio: 1, 
            viewMode: 2,
            autoCropArea: 1,
        });
    });

    cropModalEl.addEventListener('hidden.bs.modal', function () {
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
    });

    cropBtn.addEventListener('click', function() {
        if (cropper) {
            const canvas = cropper.getCroppedCanvas({ width: 400, height: 400 });
            canvas.toBlob(function(blob) {
                const url = URL.createObjectURL(blob);
                
                if (previewDefault) previewDefault.style.display = 'none';
                previewImg.style.display = 'block';
                previewImg.src = url;

                const newFile = new File([blob], "logo_empresa.png", { type: "image/png" });
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(newFile);
                fileInput.files = dataTransfer.files;

                if (fileNameSpan) {
                    fileNameSpan.textContent = "Logo listo para guardar";
                    fileNameSpan.className = "small fw-bold text-success";
                }

                cropModal.hide();
            }, 'image/png');
        }
    });
});