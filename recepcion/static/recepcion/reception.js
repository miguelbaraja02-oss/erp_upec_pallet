(function () {
    const scannerEl = document.getElementById('scanner');
    if (!scannerEl) return;
    const pageEl = document.querySelector('.reception-page');

    const startBtn = document.getElementById('startScanner');
    const stopBtn = document.getElementById('stopScanner');
    const manualCodeInput = document.getElementById('manualCode');
    const searchManualBtn = document.getElementById('searchManual');
    const statusEl = document.getElementById('scanStatus');
    const infoEl = document.getElementById('palletInfo');
    const selectedPalletCode = document.getElementById('selectedPalletCode');

    const warehouseSelect = document.getElementById('warehouseSelect');
    const rackSelect = document.getElementById('rackSelect');
    const levelSelect = document.getElementById('levelSelect');
    const sectionSelect = document.getElementById('sectionSelect');
    const capacityInfo = document.getElementById('capacityInfo');
    const assignForm = document.getElementById('assignForm');
    const assignButton = document.getElementById('assignButton');

    const documentSummary = document.getElementById('documentSummary');
    const documentLink = document.getElementById('documentLink');
    const scanUrl = pageEl ? pageEl.dataset.scanUrl : '';
    const assignUrl = pageEl ? pageEl.dataset.assignUrl : '';
    const documentBaseUrl = pageEl ? pageEl.dataset.documentBaseUrl : '/documentos/';

    const locationsScript = document.getElementById('locations-data');
    let locations = [];
    let locationIndex = { warehouses: {}, racks: {}, levels: {}, sections: {} };

    if (locationsScript && locationsScript.textContent) {
        try {
            locations = JSON.parse(locationsScript.textContent);
        } catch (err) {
            locations = [];
        }
    }

    let scanner = null;
    let cameraRunning = false;
    let lastScan = '';

    function setStatus(message, isError) {
        statusEl.textContent = message;
        statusEl.classList.toggle('error', Boolean(isError));
    }

    function fmtDate(rawValue) {
        if (!rawValue) return '-';
        const date = new Date(rawValue);
        if (Number.isNaN(date.getTime())) return rawValue;
        return date.toLocaleString();
    }

    function updateInfo(pallet) {
        const entries = [
            pallet.codigo || '-',
            pallet.contenido || '-',
            pallet.proveedor || '-',
            fmtDate(pallet.fecha_ingreso),
            pallet.estado_label || pallet.estado || '-',
            pallet.ubicacion || '-',
        ];
        infoEl.classList.remove('empty');
        infoEl.querySelectorAll('dd').forEach((dd, idx) => {
            dd.textContent = entries[idx] || '-';
        });
        selectedPalletCode.value = pallet.codigo || '';
    }

    function updateDocumentCard(documento, pallet) {
        if (!documento) {
            documentSummary.innerHTML = '<p>Sin documento asociado.</p>';
            documentLink.classList.add('disabled');
            documentLink.setAttribute('aria-disabled', 'true');
            documentLink.setAttribute('href', '#');
            return;
        }

        const movements = Array.isArray(documento.movimientos) ? documento.movimientos.slice(0, 4) : [];
        const items = movements
            .map((m) => `<li><strong>${m.tipo}</strong> - ${new Date(m.fecha).toLocaleString()}<br>${m.ubicacion}</li>`)
            .join('');

        documentSummary.classList.remove('empty');
        documentSummary.innerHTML = [
            `<p><strong>Documento:</strong> ${documento.numero_documento}</p>`,
            `<p><strong>Codigo vinculado:</strong> ${documento.pallet_codigo || (pallet ? pallet.codigo : '-')}</p>`,
            `<p><strong>Registro recepcion:</strong> ${documento.registro_recepcion || '-'}</p>`,
            movements.length ? `<ul>${items}</ul>` : '<p>Sin movimientos todavia.</p>',
        ].join('');

        if (pallet && pallet.id) {
            documentLink.href = `${documentBaseUrl}${pallet.id}/`;
            documentLink.classList.remove('disabled');
            documentLink.removeAttribute('aria-disabled');
        }
    }

    function rebuildIndex() {
        locationIndex = { warehouses: {}, racks: {}, levels: {}, sections: {} };
        locations.forEach((warehouse) => {
            locationIndex.warehouses[warehouse.id] = warehouse;
            (warehouse.racks || []).forEach((rack) => {
                locationIndex.racks[rack.id] = { ...rack, warehouse_id: warehouse.id };
                (rack.niveles || []).forEach((level) => {
                    locationIndex.levels[level.id] = { ...level, rack_id: rack.id, warehouse_id: warehouse.id };
                    (level.secciones || []).forEach((section) => {
                        locationIndex.sections[section.id] = {
                            ...section,
                            level_id: level.id,
                            rack_id: rack.id,
                            warehouse_id: warehouse.id,
                        };
                    });
                });
            });
        });
    }

    function option(label, value, disabled) {
        const el = document.createElement('option');
        el.value = value;
        el.textContent = label;
        if (disabled) el.disabled = true;
        return el;
    }

    function populateWarehouses() {
        warehouseSelect.innerHTML = '';
        warehouseSelect.appendChild(option('Selecciona un almacen', '', true));
        locations.forEach((warehouse) => {
            warehouseSelect.appendChild(option(`${warehouse.nombre} (${warehouse.codigo})`, String(warehouse.id)));
        });
    }

    function resetLevelsAndSections() {
        levelSelect.innerHTML = '';
        levelSelect.appendChild(option('Selecciona un nivel', '', true));
        levelSelect.disabled = true;

        sectionSelect.innerHTML = '';
        sectionSelect.appendChild(option('Selecciona una seccion', '', true));
        sectionSelect.disabled = true;

        capacityInfo.textContent = 'Capacidad: -';
    }

    function resetRackAndBelow() {
        rackSelect.innerHTML = '';
        rackSelect.appendChild(option('Selecciona un rack', '', true));
        rackSelect.disabled = true;
        resetLevelsAndSections();
        updateAssignButtonState();
    }

    function populateRacks(warehouseId) {
        resetRackAndBelow();
        const warehouse = locationIndex.warehouses[warehouseId];
        if (!warehouse) return;

        rackSelect.disabled = false;
        if (!(warehouse.racks || []).length) {
            setStatus('El almacen seleccionado no tiene racks configurados.', true);
            return;
        }
        (warehouse.racks || []).forEach((rack) => {
            rackSelect.appendChild(option(`${rack.nombre} (${rack.codigo})`, String(rack.id)));
        });
        setStatus('Selecciona un rack para continuar.', false);
    }

    function populateLevels(rackId) {
        resetLevelsAndSections();
        const rack = locationIndex.racks[rackId];
        if (!rack) return;

        levelSelect.disabled = false;
        if (!(rack.niveles || []).length) {
            setStatus('El rack seleccionado no tiene niveles configurados.', true);
            return;
        }
        (rack.niveles || []).forEach((level) => {
            levelSelect.appendChild(option(`Nivel ${level.posicion} (${level.codigo})`, String(level.id)));
        });
        setStatus('Selecciona un nivel para continuar.', false);
    }

    function populateSections(levelId) {
        sectionSelect.innerHTML = '';
        sectionSelect.appendChild(option('Selecciona una seccion', '', true));
        sectionSelect.disabled = true;

        const level = locationIndex.levels[levelId];
        if (!level) return;

        sectionSelect.disabled = false;
        if (!(level.secciones || []).length) {
            setStatus('El nivel seleccionado no tiene secciones configuradas.', true);
            return;
        }
        (level.secciones || []).forEach((section) => {
            const occupancyText = section.capacidad > 0 ? `${section.ocupacion}/${section.capacidad}` : `${section.ocupacion}/inf`;
            const el = option(`${section.codigo} (${occupancyText})`, String(section.id));
            el.disabled = !section.disponible;
            sectionSelect.appendChild(el);
        });
        updateAssignButtonState();
    }

    function updateCapacityInfo(sectionId) {
        const section = locationIndex.sections[sectionId];
        if (!section) {
            capacityInfo.textContent = 'Capacidad: -';
            return;
        }
        const cap = section.capacidad > 0 ? section.capacidad : 'Ilimitada';
        capacityInfo.textContent = `Capacidad: ${section.ocupacion}/${cap}`;
    }

    function updateAssignButtonState() {
        assignButton.disabled = !(selectedPalletCode.value && sectionSelect.value);
    }

    async function fetchScan(code) {
        setStatus('Consultando pallet...', false);
        const response = await fetch(`${scanUrl}?code=${encodeURIComponent(code)}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        });
        const data = await response.json();
        if (!response.ok || !data.ok) throw new Error(data.message || 'No se pudo consultar el pallet.');
        updateInfo(data.pallet);
        updateDocumentCard(data.documento, data.pallet);
        setStatus(`Pallet ${data.pallet.codigo} listo para asignacion.`, false);
        updateAssignButtonState();
        return data;
    }

    async function assignPallet() {
        const csrfInput = assignForm.querySelector('input[name="csrfmiddlewaretoken"]');
        const response = await fetch(assignUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfInput ? csrfInput.value : '',
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({
                pallet_code: selectedPalletCode.value,
                seccion_id: Number(sectionSelect.value),
            }),
        });
        const data = await response.json();
        if (!response.ok || !data.ok) throw new Error(data.message || 'No fue posible asignar el pallet.');

        if (Array.isArray(data.locations)) {
            locations = data.locations;
            rebuildIndex();
            populateWarehouses();
        }

        updateInfo(data.pallet);
        updateDocumentCard(data.documento, data.pallet);
        setStatus(data.message || 'Asignacion completada.', false);

        warehouseSelect.value = '';
        resetRackAndBelow();
    }

    function onScanSuccess(decodedText) {
        const code = String(decodedText || '').trim();
        if (!code || code === lastScan) return;
        lastScan = code;
        manualCodeInput.value = code;
        fetchScan(code).catch((err) => setStatus(err.message, true));
        setTimeout(() => {
            if (lastScan === code) lastScan = '';
        }, 1200);
    }

    async function startScanner() {
        if (cameraRunning) return;
        if (!window.Html5Qrcode) {
            setStatus('No se pudo cargar el motor de escaneo.', true);
            return;
        }

        scanner = scanner || new Html5Qrcode('scanner');
        try {
            await scanner.start(
                { facingMode: 'environment' },
                {
                    fps: 10,
                    qrbox: { width: 260, height: 260 },
                    supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA],
                    formatsToSupport: [
                        Html5QrcodeSupportedFormats.QR_CODE,
                        Html5QrcodeSupportedFormats.CODE_128,
                        Html5QrcodeSupportedFormats.CODE_39,
                        Html5QrcodeSupportedFormats.EAN_13,
                        Html5QrcodeSupportedFormats.EAN_8,
                        Html5QrcodeSupportedFormats.UPC_A,
                        Html5QrcodeSupportedFormats.UPC_E,
                    ],
                },
                onScanSuccess,
                function () {}
            );
            cameraRunning = true;
            startBtn.disabled = true;
            stopBtn.disabled = false;
            setStatus('Camara activa. Apunta al codigo.', false);
        } catch (err) {
            setStatus('No fue posible acceder a la camara.', true);
        }
    }

    async function stopScanner() {
        if (!scanner || !cameraRunning) return;
        try {
            await scanner.stop();
            await scanner.clear();
        } catch (err) {
            // No-op
        }
        cameraRunning = false;
        startBtn.disabled = false;
        stopBtn.disabled = true;
        setStatus('Camara detenida.', false);
    }

    startBtn.addEventListener('click', startScanner);
    stopBtn.addEventListener('click', stopScanner);

    searchManualBtn.addEventListener('click', function () {
        const code = manualCodeInput.value.trim();
        if (!code) {
            setStatus('Ingresa un codigo para consultar.', true);
            return;
        }
        fetchScan(code).catch((err) => setStatus(err.message, true));
    });

    manualCodeInput.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            searchManualBtn.click();
        }
    });

    warehouseSelect.addEventListener('change', function () {
        populateRacks(Number(warehouseSelect.value));
        updateAssignButtonState();
    });

    rackSelect.addEventListener('change', function () {
        populateLevels(Number(rackSelect.value));
        updateAssignButtonState();
    });

    levelSelect.addEventListener('change', function () {
        populateSections(Number(levelSelect.value));
        updateAssignButtonState();
    });

    sectionSelect.addEventListener('change', function () {
        updateCapacityInfo(Number(sectionSelect.value));
        updateAssignButtonState();
    });

    assignForm.addEventListener('submit', function (event) {
        event.preventDefault();
        if (!selectedPalletCode.value) {
            setStatus('Primero escanea un pallet.', true);
            return;
        }
        if (!sectionSelect.value) {
            setStatus('Selecciona una seccion valida.', true);
            return;
        }
        assignPallet().catch((err) => setStatus(err.message, true));
    });

    rebuildIndex();
    populateWarehouses();
    resetRackAndBelow();
})();
