// rack_validation.js
// Validaciones en tiempo real para rack, niveles y secciones.
// Soporta campos dinamicos agregados en el formset.

function validateFormat(code) {
    return /^[A-Za-z0-9\-]{3,20}$/.test(code);
}

async function checkCodeExists(type, code) {
    try {
        const response = await fetch(`/store/validate_code/?type=${encodeURIComponent(type)}&code=${encodeURIComponent(code)}`);
        if (!response.ok) {
            return null;
        }
        const data = await response.json();
        return Boolean(data.exists);
    } catch (error) {
        return null;
    }
}

function getInputMeta(input) {
    const name = input.name || '';
    const id = input.id || '';

    if (id === 'rack_code' || name === 'codigo') {
        return { type: 'rack', label: 'Codigo de Rack' };
    }

    if (/^niveles-\d+-codigo$/.test(name) || /^level_code_\d+$/.test(id)) {
        return { type: 'level', label: 'Codigo de Nivel' };
    }

    if (/^secciones-\d+-\d+-codigo$/.test(name) || /^section_code_\d+_\d+$/.test(id)) {
        return { type: 'section', label: 'Codigo de Seccion' };
    }

    return null;
}

function findMessageSpanNearInput(input, type) {
    if (type === 'rack') {
        return document.getElementById('rack_code_msg');
    }

    const blockSelector = type === 'level' ? '.nivel-block' : '.seccion-block';
    const idPrefix = type === 'level' ? 'level_code_msg_' : 'section_code_msg_';
    const block = input.closest(blockSelector);

    if (block) {
        const withPrefix = block.querySelector(`span[id^="${idPrefix}"]`);
        if (withPrefix) {
            return withPrefix;
        }

        const genericMsg = block.querySelector('span.live-validation-msg');
        if (genericMsg) {
            return genericMsg;
        }
    }

    let sibling = input.nextElementSibling;
    while (sibling) {
        if (sibling.tagName === 'SPAN') {
            return sibling;
        }
        if (sibling.matches && sibling.matches('input, textarea, select, .nivel-block, .seccion-block')) {
            break;
        }
        sibling = sibling.nextElementSibling;
    }

    return null;
}

function ensureMessageElement(input, type) {
    const found = findMessageSpanNearInput(input, type);
    if (found) {
        return found;
    }

    if (type === 'rack') {
        return null;
    }

    const msg = document.createElement('span');
    msg.className = 'live-validation-msg';
    msg.style.fontSize = '0.9em';
    msg.style.display = 'block';
    input.insertAdjacentElement('afterend', msg);
    return msg;
}

function setMessage(msg, text, color) {
    if (!msg) {
        return;
    }
    msg.textContent = text;
    msg.style.color = color || '';
}

const debounceTimers = new WeakMap();
const latestRequests = new WeakMap();

function scheduleLiveValidation(input, meta) {
    const pending = debounceTimers.get(input);
    if (pending) {
        clearTimeout(pending);
    }

    const timer = setTimeout(function () {
        runLiveValidation(input, meta);
    }, 250);

    debounceTimers.set(input, timer);
}

async function runLiveValidation(input, meta) {
    const msg = ensureMessageElement(input, meta.type);
    if (!msg) {
        return;
    }

    const code = String(input.value || '').trim();
    if (!code) {
        setMessage(msg, '', '');
        return;
    }

    if (!validateFormat(code)) {
        setMessage(msg, `${meta.label} invalido. Usa solo letras, numeros y guiones (3-20 caracteres).`, 'red');
        return;
    }

    setMessage(msg, 'Verificando...', 'gray');

    const requestToken = Symbol('validation-request');
    latestRequests.set(input, requestToken);

    const exists = await checkCodeExists(meta.type, code);

    if (latestRequests.get(input) !== requestToken) {
        return;
    }

    if (exists === null) {
        setMessage(msg, 'No se pudo validar en este momento.', '#b45309');
        return;
    }

    if (exists) {
        setMessage(msg, `El ${meta.label.toLowerCase()} ya existe.`, 'red');
    } else {
        setMessage(msg, `${meta.label} disponible.`, 'green');
    }
}

function validateDuplicateCodesOnSubmit(form) {
    let hasDuplicate = false;

    const levelInputs = Array.from(
        form.querySelectorAll('input[name^="niveles-"][name$="-codigo"], textarea[name^="niveles-"][name$="-codigo"]')
    );

    const levelMap = new Map();
    levelInputs.forEach(function (input) {
        const msg = ensureMessageElement(input, 'level');
        setMessage(msg, '', '');

        const code = String(input.value || '').trim();
        if (!code) {
            return;
        }

        const key = code.toUpperCase();
        if (!levelMap.has(key)) {
            levelMap.set(key, []);
        }
        levelMap.get(key).push(msg);
    });

    levelMap.forEach(function (messages) {
        if (messages.length > 1) {
            hasDuplicate = true;
            messages.forEach(function (msg) {
                setMessage(msg, 'Este nivel ya existe.', 'red');
            });
        }
    });

    const sectionInputs = Array.from(
        form.querySelectorAll('input[name^="secciones-"][name$="-codigo"], textarea[name^="secciones-"][name$="-codigo"]')
    );

    const sectionMap = new Map();
    sectionInputs.forEach(function (input) {
        const msg = ensureMessageElement(input, 'section');
        setMessage(msg, '', '');

        const code = String(input.value || '').trim();
        if (!code) {
            return;
        }

        const match = /^secciones-(\d+)-\d+-codigo$/.exec(input.name || '');
        const nivelIndex = match ? match[1] : 'global';
        const key = `${nivelIndex}::${code.toUpperCase()}`;

        if (!sectionMap.has(key)) {
            sectionMap.set(key, []);
        }
        sectionMap.get(key).push(msg);
    });

    sectionMap.forEach(function (messages) {
        if (messages.length > 1) {
            hasDuplicate = true;
            messages.forEach(function (msg) {
                setMessage(msg, 'Esta seccion ya existe en este nivel.', 'red');
            });
        }
    });

    return hasDuplicate;
}

function initNivelSeccionFilter() {
    const nivelSelector = document.getElementById('nivel-selector');
    const nivelesContainer = document.getElementById('niveles-container');
    const seccionesContainers = document.querySelectorAll('.secciones-container');

    if (!nivelSelector || !nivelesContainer) {
        return;
    }

    function syncSelectedNivel() {
        const selectedId = nivelSelector.value;

        Array.from(nivelesContainer.children).forEach(function (div) {
            div.style.display = div.id === selectedId ? 'block' : 'none';
        });

        seccionesContainers.forEach(function (div) {
            div.style.display = div.id === `secciones-${selectedId}` ? 'block' : 'none';
        });
    }

    nivelSelector.addEventListener('change', syncSelectedNivel);
    syncSelectedNivel();
}

window.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('input', function (event) {
            const target = event.target;
            if (!(target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement)) {
                return;
            }

            const meta = getInputMeta(target);
            if (!meta) {
                return;
            }

            scheduleLiveValidation(target, meta);
        });

        form.addEventListener(
            'blur',
            function (event) {
                const target = event.target;
                if (!(target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement)) {
                    return;
                }

                const meta = getInputMeta(target);
                if (!meta) {
                    return;
                }

                const pending = debounceTimers.get(target);
                if (pending) {
                    clearTimeout(pending);
                }

                runLiveValidation(target, meta);
            },
            true
        );

        form.addEventListener('submit', function (event) {
            const hasDuplicate = validateDuplicateCodesOnSubmit(form);
            if (hasDuplicate) {
                event.preventDefault();
            }
        });
    }

    initNivelSeccionFilter();
});
