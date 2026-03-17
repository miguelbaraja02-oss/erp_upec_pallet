(function () {
    function q(selector, root) {
        return (root || document).querySelector(selector);
    }

    function qa(selector, root) {
        return Array.from((root || document).querySelectorAll(selector));
    }

    function parseNivelIndex(value) {
        var match = /nivel-(\d+)/.exec(value || '');
        return match ? parseInt(match[1], 10) : 0;
    }

    function getNivelBlocks() {
        return qa('#niveles-container .nivel-block');
    }

    function getSeccionesContainers() {
        return qa('.secciones-card-form .secciones-container');
    }

    function showNivel(index) {
        getNivelBlocks().forEach(function (block, i) {
            block.style.display = i === index ? 'block' : 'none';
        });

        getSeccionesContainers().forEach(function (container, i) {
            container.style.display = i === index ? 'block' : 'none';
        });

        var selector = q('#nivel-selector');
        if (selector && selector.value !== 'nivel-' + index) {
            selector.value = 'nivel-' + index;
        }
    }

    function clearField(field) {
        var tag = (field.tagName || '').toLowerCase();
        var type = (field.type || '').toLowerCase();

        if (type === 'checkbox' || type === 'radio') {
            field.checked = false;
            return;
        }

        if (type === 'hidden') {
            if (/-id$/.test(field.name || '')) {
                field.value = '';
            }
            return;
        }

        if (tag === 'select') {
            field.selectedIndex = 0;
            return;
        }

        field.value = '';
    }

    function markFieldError(field, hasError) {
        if (!field) {
            return;
        }

        if (hasError) {
            field.classList.add('input-error');
        } else {
            field.classList.remove('input-error');
        }
    }

    function getNivelCodigoField(index) {
        var nivelBlock = q('#nivel-' + index);
        if (!nivelBlock) {
            return null;
        }

        return q('input[name="niveles-' + index + '-codigo"], textarea[name="niveles-' + index + '-codigo"]', nivelBlock);
    }

    function getSeccionCodigoFields(index) {
        var seccionesContainer = q('#secciones-nivel-' + index);
        if (!seccionesContainer) {
            return [];
        }

        return qa('input[name^="secciones-' + index + '-"][name$="-codigo"], textarea[name^="secciones-' + index + '-"][name$="-codigo"]', seccionesContainer);
    }

    function validateNivelForNext(index) {
        var valid = true;
        var firstInvalid = null;

        var nivelCodigo = getNivelCodigoField(index);
        var nivelCodigoEmpty = !nivelCodigo || !String(nivelCodigo.value || '').trim();
        markFieldError(nivelCodigo, nivelCodigoEmpty);
        if (nivelCodigoEmpty) {
            valid = false;
            firstInvalid = firstInvalid || nivelCodigo;
        }

        getSeccionCodigoFields(index).forEach(function (field) {
            var empty = !String(field.value || '').trim();
            markFieldError(field, empty);
            if (empty) {
                valid = false;
                firstInvalid = firstInvalid || field;
            }
        });

        return {
            valid: valid,
            firstInvalid: firstInvalid
        };
    }

    function updateNivelesTotalForms() {
        var totalInput = q('input[name="niveles-TOTAL_FORMS"]');
        if (totalInput) {
            totalInput.value = String(getNivelBlocks().length);
        }
    }

    function updateSeccionesTotalForms(nivelIndex) {
        var container = q('#secciones-nivel-' + nivelIndex);
        if (!container) {
            return;
        }

        var totalInput = q('input[name="secciones-' + nivelIndex + '-TOTAL_FORMS"]', container);
        if (totalInput) {
            totalInput.value = String(qa('.seccion-block', container).length);
        }
    }

    function replaceNivelIndexAttributes(root, oldIndex, newIndex) {
        var pattern = new RegExp('niveles-' + oldIndex + '-', 'g');

        qa('[name], [id], label[for]', root).forEach(function (el) {
            if (el.name) {
                el.name = el.name.replace(pattern, 'niveles-' + newIndex + '-');
            }
            if (el.id) {
                el.id = el.id.replace(pattern, 'niveles-' + newIndex + '-');
            }
            if (el.getAttribute('for')) {
                el.setAttribute('for', el.getAttribute('for').replace(pattern, 'niveles-' + newIndex + '-'));
            }
        });

        root.id = 'nivel-' + newIndex;
    }

    function replaceSeccionesNivelIndex(root, oldNivelIndex, newNivelIndex) {
        var pattern = new RegExp('secciones-' + oldNivelIndex + '-', 'g');

        qa('[name], [id], label[for]', root).forEach(function (el) {
            if (el.name) {
                el.name = el.name.replace(pattern, 'secciones-' + newNivelIndex + '-');
            }
            if (el.id) {
                el.id = el.id.replace(pattern, 'secciones-' + newNivelIndex + '-');
            }
            if (el.getAttribute('for')) {
                el.setAttribute('for', el.getAttribute('for').replace(pattern, 'secciones-' + newNivelIndex + '-'));
            }
        });

        root.id = 'secciones-nivel-' + newNivelIndex;
    }

    function keepOneSeccionBlock(container, nivelIndex) {
        var blocks = qa('.seccion-block', container);
        blocks.forEach(function (block, i) {
            if (i > 0) {
                block.remove();
            }
        });

        var first = q('.seccion-block', container);
        if (!first) {
            return;
        }

        qa('[name], [id], label[for]', first).forEach(function (el) {
            if (el.name) {
                el.name = el.name.replace(new RegExp('secciones-' + nivelIndex + '-\\d+-', 'g'), 'secciones-' + nivelIndex + '-0-');
            }
            if (el.id) {
                el.id = el.id.replace(new RegExp('secciones-' + nivelIndex + '-\\d+-', 'g'), 'secciones-' + nivelIndex + '-0-');
            }
            if (el.getAttribute('for')) {
                el.setAttribute('for', el.getAttribute('for').replace(new RegExp('secciones-' + nivelIndex + '-\\d+-', 'g'), 'secciones-' + nivelIndex + '-0-'));
            }
        });

        qa('input, textarea, select', first).forEach(clearField);
    }

    function addNivel() {
        var selector = q('#nivel-selector');
        var blocks = getNivelBlocks();
        if (!selector || !blocks.length) {
            return;
        }

        var currentIndex = parseNivelIndex(selector.value);
        var lastIndex = blocks.length - 1;

        // Flujo guiado: siempre completar el ultimo nivel creado.
        if (currentIndex !== lastIndex) {
            showNivel(lastIndex);
            // window.alert('Completa el ultimo nivel creado antes de agregar uno nuevo.');
            return;
        }

        var check = validateNivelForNext(lastIndex);
        if (!check.valid) {
            showNivel(lastIndex);
            // window.alert('Debes completar el nivel actual y su seccion antes de agregar otro nivel.');
            if (check.firstInvalid) {
                check.firstInvalid.focus();
            }
            return;
        }

        var newIndex = lastIndex + 1;
        var lastNivelBlock = blocks[lastIndex];

        var newNivelBlock = lastNivelBlock.cloneNode(true);
        replaceNivelIndexAttributes(newNivelBlock, lastIndex, newIndex);
        qa('input, textarea, select', newNivelBlock).forEach(clearField);
        // Asignar automáticamente el valor de 'posicion' (oculto) al nuevo nivel
        var posicionField = q('input[name="niveles-' + newIndex + '-posicion"]', newNivelBlock);
        if (posicionField) {
            posicionField.value = String(newIndex + 1); // 1-based
        }

        var seccionesContainers = getSeccionesContainers();
        var lastSeccionesContainer = seccionesContainers[lastIndex];
        var newSeccionesContainer = lastSeccionesContainer.cloneNode(true);
        replaceSeccionesNivelIndex(newSeccionesContainer, lastIndex, newIndex);
        keepOneSeccionBlock(newSeccionesContainer, newIndex);

        var newTotal = q('input[name="secciones-' + newIndex + '-TOTAL_FORMS"]', newSeccionesContainer);
        var newInitial = q('input[name="secciones-' + newIndex + '-INITIAL_FORMS"]', newSeccionesContainer);
        if (newTotal) {
            newTotal.value = '1';
        }
        if (newInitial) {
            newInitial.value = '0';
        }

        blocks.forEach(function (block) {
            block.style.display = 'none';
        });
        seccionesContainers.forEach(function (container) {
            container.style.display = 'none';
        });

        q('#niveles-container').appendChild(newNivelBlock);
        q('.secciones-card-form .card-body').appendChild(newSeccionesContainer);

        var option = document.createElement('option');
        option.value = 'nivel-' + newIndex;
        option.textContent = 'Nivel ' + (newIndex + 1);
        selector.appendChild(option);

        updateNivelesTotalForms();
        updateSeccionesTotalForms(newIndex);
        showNivel(newIndex);
    }

    function addSeccionForCurrentNivel(button) {
        var selector = q('#nivel-selector');
        if (!selector) {
            return;
        }

        var nivelIndex = parseNivelIndex(selector.value);
        var container = q('#secciones-nivel-' + nivelIndex);
        if (!container) {
            return;
        }

        var blocks = qa('.seccion-block', container);
        if (!blocks.length) {
            return;
        }


        // Restricción eliminada: ahora se pueden agregar secciones sin completar la anterior
        var lastBlock = blocks[blocks.length - 1];
        var newSectionIndex = blocks.length;
        var clone = lastBlock.cloneNode(true);

        qa('[name], [id], label[for]', clone).forEach(function (el) {
            if (el.name) {
                el.name = el.name.replace(new RegExp('secciones-' + nivelIndex + '-\\d+-', 'g'), 'secciones-' + nivelIndex + '-' + newSectionIndex + '-');
            }
            if (el.id) {
                el.id = el.id.replace(new RegExp('secciones-' + nivelIndex + '-\\d+-', 'g'), 'secciones-' + nivelIndex + '-' + newSectionIndex + '-');
            }
            if (el.getAttribute('for')) {
                el.setAttribute('for', el.getAttribute('for').replace(new RegExp('secciones-' + nivelIndex + '-\\d+-', 'g'), 'secciones-' + nivelIndex + '-' + newSectionIndex + '-'));
            }
        });

        qa('input, textarea, select', clone).forEach(clearField);
        container.appendChild(clone);
        updateSeccionesTotalForms(nivelIndex);
    }

    function autoExpandTextareas() {
        function autoExpand(textarea) {
            textarea.style.height = '32px';
            textarea.style.height = textarea.scrollHeight + 'px';
        }

        qa('textarea').forEach(function (textarea) {
            textarea.addEventListener('input', function () {
                autoExpand(textarea);
            });
            autoExpand(textarea);
        });
    }

    // Elimina niveles y secciones vacíos antes de enviar el formulario
    function cleanEmptyNivelesYSecciones() {
        var nivelBlocks = getNivelBlocks();
        var seccionesContainers = getSeccionesContainers();
        var selector = q('#nivel-selector');
        var nivelesAEliminar = [];

        nivelBlocks.forEach(function (nivelBlock, i) {
            var codigoField = getNivelCodigoField(i);
            var codigo = codigoField ? String(codigoField.value || '').trim() : '';
            // Si el código está vacío, marca para eliminar
            if (!codigo) {
                nivelesAEliminar.push(i);
                return;
            }
            // Limpiar secciones vacías dentro de este nivel
            var seccionesContainer = seccionesContainers[i];
            if (seccionesContainer) {
                var seccionBlocks = qa('.seccion-block', seccionesContainer);
                seccionBlocks.forEach(function (block) {
                    var seccionCodigo = q('input[name$="-codigo"], textarea[name$="-codigo"]', block);
                    if (!seccionCodigo || !String(seccionCodigo.value || '').trim()) {
                        block.remove();
                    }
                });
                updateSeccionesTotalForms(i);
            }
        });

        // Eliminar niveles vacíos (de atrás hacia adelante para no romper índices)
        for (var j = nivelesAEliminar.length - 1; j >= 0; j--) {
            var idx = nivelesAEliminar[j];
            if (nivelBlocks[idx]) nivelBlocks[idx].remove();
            if (seccionesContainers[idx]) seccionesContainers[idx].remove();
            if (selector) selector.remove(idx + 1); // +1 porque la opción 0 es el primer nivel
        }

        updateNivelesTotalForms();
    }

    function bindEvents() {
        var selector = q('#nivel-selector');
        if (selector) {
            selector.addEventListener('change', function () {
                showNivel(parseNivelIndex(selector.value));
            });
        }

        var addNivelBtn = q('#add-nivel-btn');
        var addingLevel = false;
        if (addNivelBtn) {
            addNivelBtn.addEventListener('click', function () {
                if (addingLevel) {
                    return;
                }
                addingLevel = true;
                try {
                    addNivel();
                } finally {
                    setTimeout(function () {
                        addingLevel = false;
                    }, 180);
                }
            });
        }

        var seccionesCard = q('.secciones-card-form');
        if (seccionesCard) {
            seccionesCard.addEventListener('click', function (event) {
                var button = event.target.closest('.add-seccion-btn');
                if (button) {
                    addSeccionForCurrentNivel(button);
                }
            });
        }

        var form = q('form[method="post"]');
        if (form) {
            form.addEventListener('submit', function (event) {
                // Limpia niveles y secciones vacíos antes de validar y enviar
                cleanEmptyNivelesYSecciones();
                var lastIndex = getNivelBlocks().length - 1;
                var check = validateNivelForNext(lastIndex);
                if (!check.valid) {
                    event.preventDefault();
                    showNivel(lastIndex);
                    window.alert('Completa el ultimo nivel antes de guardar.');
                    if (check.firstInvalid) {
                        check.firstInvalid.focus();
                    }
                }
            });
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        bindEvents();
        autoExpandTextareas();

        var selector = q('#nivel-selector');
        if (selector) {
            showNivel(parseNivelIndex(selector.value));
        }
    });
})();
