import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';

const canvasHost = document.getElementById('warehouse3dCanvas');
const dataScript = document.getElementById('warehouse-3d-data');
const emptyEl = document.getElementById('warehouse3dEmpty');
const selectedItem = document.getElementById('selectedItem');
const selectedLocation = document.getElementById('selectedLocation');
const selectedPallet = document.getElementById('selectedPallet');

const rackCountEl = document.getElementById('rackCount');
const sectionCountEl = document.getElementById('sectionCount');
const palletCountEl = document.getElementById('palletCount');

let visualizationData = dataScript ? JSON.parse(dataScript.textContent || '{}') : {};
let racks = Array.isArray(visualizationData.racks) ? visualizationData.racks : [];

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xeef3f5);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
canvasHost.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(48, 1, 0.1, 1000);
camera.position.set(12, 10, 15);

const cameraTarget = new THREE.Vector3(0, 1.5, 0);
const orbit = {
    radius: 22,
    theta: Math.PI * 0.24,
    phi: Math.PI * 0.32,
    dragging: false,
    lastX: 0,
    lastY: 0,
};

function updateCamera() {
    const x = cameraTarget.x + orbit.radius * Math.sin(orbit.phi) * Math.sin(orbit.theta);
    const y = cameraTarget.y + orbit.radius * Math.cos(orbit.phi);
    const z = cameraTarget.z + orbit.radius * Math.sin(orbit.phi) * Math.cos(orbit.theta);
    camera.position.set(x, y, z);
    camera.lookAt(cameraTarget);
}

const ambient = new THREE.HemisphereLight(0xffffff, 0xaeb9bf, 2.2);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xffffff, 2.2);
sun.position.set(8, 16, 10);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
scene.add(sun);

const sceneRoot = new THREE.Group();
scene.add(sceneRoot);

const floorMaterial = new THREE.MeshStandardMaterial({ color: 0xdfe7eb, roughness: 0.85 });
const rackMaterial = new THREE.MeshStandardMaterial({ color: 0x2f6f73, roughness: 0.58, metalness: 0.08 });
const shelfMaterial = new THREE.MeshStandardMaterial({ color: 0x213c40, roughness: 0.5, metalness: 0.12 });
const palletWoodMaterial = new THREE.MeshStandardMaterial({ color: 0xc89b63, roughness: 0.82 });
const palletWoodDarkMaterial = new THREE.MeshStandardMaterial({ color: 0x8f6337, roughness: 0.86 });
const productMaterial = new THREE.MeshStandardMaterial({ color: 0xffce00, roughness: 0.72 });
const highlightMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffce00, emissiveIntensity: 0.45 });

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const pickables = [];
let selectedMesh = null;

function makeBox(width, height, depth, material, position, castShadow = true) {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), material);
    mesh.position.set(position.x, position.y, position.z);
    mesh.castShadow = castShadow;
    mesh.receiveShadow = true;
    sceneRoot.add(mesh);
    return mesh;
}

function disposeObject(object) {
    object.traverse((child) => {
        if (!child.isMesh && !child.isSprite) {
            return;
        }
        if (child.geometry) {
            child.geometry.dispose();
        }
        if (child.material && child.userData.disposeMaterial) {
            if (child.material.map) {
                child.material.map.dispose();
            }
            child.material.dispose();
        }
    });
}

function roundRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
}

function fitText(ctx, text, maxWidth, initialSize, minSize) {
    let size = initialSize;
    do {
        ctx.font = `800 ${size}px Inter, Arial, sans-serif`;
        if (ctx.measureText(text).width <= maxWidth) {
            return size;
        }
        size -= 2;
    } while (size >= minSize);
    return minSize;
}

function addRackLabel(rack, x, y, z) {
    const canvas = document.createElement('canvas');
    canvas.width = 768;
    canvas.height = 224;
    const ctx = canvas.getContext('2d');

    const title = String(rack.nombre || 'Rack').replace(/^rack\s+/i, '').slice(0, 28);
    const subtitle = String(rack.codigo || '').slice(0, 18);

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.shadowColor = 'rgba(0, 0, 0, 0.35)';
    ctx.shadowBlur = 18;
    ctx.shadowOffsetY = 10;
    ctx.fillStyle = 'rgba(17, 24, 31, 0.92)';
    roundRect(ctx, 24, 22, canvas.width - 48, canvas.height - 44, 28);
    ctx.fill();

    ctx.shadowColor = 'transparent';
    ctx.fillStyle = '#ffce00';
    roundRect(ctx, 24, 22, canvas.width - 48, 24, 18);
    ctx.fill();

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.45)';
    ctx.lineWidth = 4;
    roundRect(ctx, 24, 22, canvas.width - 48, canvas.height - 44, 28);
    ctx.stroke();

    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#ffffff';
    const titleSize = fitText(ctx, title, canvas.width - 110, 62, 34);
    ctx.font = `800 ${titleSize}px Inter, Arial, sans-serif`;
    ctx.fillText(title, canvas.width / 2, 104);

    if (subtitle) {
        ctx.fillStyle = '#d8e1e6';
        ctx.font = '700 30px Inter, Arial, sans-serif';
        ctx.fillText(subtitle, canvas.width / 2, 154);
    }

    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    const material = new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthTest: false,
        depthWrite: false,
    });
    const sprite = new THREE.Sprite(material);
    sprite.position.set(x, y, z);
    sprite.scale.set(3.4, 1, 1);
    sprite.renderOrder = 999;
    sprite.userData.disposeMaterial = true;
    sceneRoot.add(sprite);
}

function addPalletLoad(x, y, z, slotWidth, rack, nivel, seccion) {
    const baseWidth = slotWidth * 0.72;
    const baseDepth = 0.98;
    const baseHeight = 0.14;
    const plankHeight = 0.05;
    const runnerWidth = baseWidth * 0.18;

    const group = new THREE.Group();
    group.position.set(x, y, z);

    const base = new THREE.Mesh(new THREE.BoxGeometry(baseWidth, baseHeight, baseDepth), palletWoodMaterial);
    base.position.y = baseHeight / 2;
    base.castShadow = true;
    base.receiveShadow = true;
    group.add(base);

    [-0.32, 0, 0.32].forEach((offsetZ) => {
        const plank = new THREE.Mesh(new THREE.BoxGeometry(baseWidth, plankHeight, 0.13), palletWoodDarkMaterial);
        plank.position.set(0, baseHeight + plankHeight / 2, offsetZ);
        plank.castShadow = true;
        plank.receiveShadow = true;
        group.add(plank);
    });

    [-0.28, 0.28].forEach((offsetX) => {
        const runner = new THREE.Mesh(new THREE.BoxGeometry(runnerWidth, 0.12, baseDepth), palletWoodDarkMaterial);
        runner.position.set(offsetX * baseWidth, -0.06, 0);
        runner.castShadow = true;
        runner.receiveShadow = true;
        group.add(runner);
    });

    const product = new THREE.Mesh(new THREE.BoxGeometry(baseWidth * 0.7, 0.46, baseDepth * 0.72), productMaterial);
    product.position.y = baseHeight + plankHeight + 0.23;
    product.castShadow = true;
    product.receiveShadow = true;
    group.add(product);

    group.userData = {
        label: `Pallet ${seccion.pallet_codigo || ''}`.trim(),
        location: `${rack.nombre} / Nivel ${nivel.posicion} / Seccion ${seccion.codigo}`,
        pallet: seccion.pallet_codigo || '-',
    };

    group.traverse((child) => {
        if (child.isMesh) {
            child.userData = group.userData;
            pickables.push(child);
        }
    });

    sceneRoot.add(group);
}

function addRack(rack, index, columns) {
    const col = index % columns;
    const row = Math.floor(index / columns);
    const spacingX = 7.5;
    const spacingZ = 6.6;
    const baseX = (col - (columns - 1) / 2) * spacingX;
    const baseZ = row * spacingZ;

    const levels = rack.niveles && rack.niveles.length ? rack.niveles : [{ posicion: 1, codigo: 'N1', secciones: [] }];
    const maxSections = Math.max(1, ...levels.map((nivel) => Math.max(1, (nivel.secciones || []).length)));
    const rackWidth = Math.max(3.6, maxSections * 1.15 + 0.7);
    const levelHeight = 0.9;
    const rackHeight = levels.length * levelHeight + 0.8;
    const rackDepth = 1.8;

    makeBox(0.12, rackHeight, 0.14, rackMaterial, { x: baseX - rackWidth / 2, y: rackHeight / 2, z: baseZ - rackDepth / 2 });
    makeBox(0.12, rackHeight, 0.14, rackMaterial, { x: baseX + rackWidth / 2, y: rackHeight / 2, z: baseZ - rackDepth / 2 });
    makeBox(0.12, rackHeight, 0.14, rackMaterial, { x: baseX - rackWidth / 2, y: rackHeight / 2, z: baseZ + rackDepth / 2 });
    makeBox(0.12, rackHeight, 0.14, rackMaterial, { x: baseX + rackWidth / 2, y: rackHeight / 2, z: baseZ + rackDepth / 2 });

    levels.forEach((nivel, levelIndex) => {
        const y = 0.45 + levelIndex * levelHeight;
        makeBox(rackWidth + 0.24, 0.08, rackDepth + 0.18, shelfMaterial, { x: baseX, y, z: baseZ }, false);

        const secciones = nivel.secciones && nivel.secciones.length ? nivel.secciones : [{ codigo: 'Libre', ocupado: false }];
        const slotWidth = Math.min(0.95, (rackWidth - 0.5) / secciones.length);
        const startX = baseX - ((secciones.length - 1) * slotWidth) / 2;

        secciones.forEach((seccion, sectionIndex) => {
            const x = startX + sectionIndex * slotWidth;
            if (seccion.ocupado) {
                addPalletLoad(x, y + 0.12, baseZ, slotWidth, rack, nivel, seccion);
            }
        });
    });

    makeBox(rackWidth + 0.5, 0.08, rackDepth + 0.5, rackMaterial, { x: baseX, y: rackHeight + 0.12, z: baseZ }, false);
    addRackLabel(rack, baseX, rackHeight + 1.05, baseZ);
}

function buildScene() {
    while (sceneRoot.children.length) {
        const child = sceneRoot.children.pop();
        disposeObject(child);
    }
    pickables.length = 0;
    updateSelection(null);

    const columns = Math.max(1, Math.ceil(Math.sqrt(racks.length || 1)));
    const rows = Math.max(1, Math.ceil((racks.length || 1) / columns));
    const floorWidth = Math.max(14, columns * 8.2);
    const floorDepth = Math.max(12, rows * 7.2);

    const floor = new THREE.Mesh(new THREE.PlaneGeometry(floorWidth, floorDepth), floorMaterial);
    floor.rotation.x = -Math.PI / 2;
    floor.position.z = ((rows - 1) * 6.6) / 2;
    floor.receiveShadow = true;
    sceneRoot.add(floor);

    const grid = new THREE.GridHelper(Math.max(floorWidth, floorDepth), 24, 0x9aa8ae, 0xc8d0d4);
    grid.position.y = 0.01;
    grid.position.z = floor.position.z;
    sceneRoot.add(grid);

    racks.forEach((rack, index) => addRack(rack, index, columns));

    cameraTarget.set(0, 1.6, ((rows - 1) * 6.6) / 2);
    orbit.radius = Math.max(14, 12 + rows * 4.3 + columns * 2.4);
    orbit.theta = Math.PI * 0.22;
    orbit.phi = Math.PI * 0.32;
    updateCamera();
}

function updateMetrics() {
    let sectionCount = 0;
    let palletCount = 0;

    racks.forEach((rack) => {
        (rack.niveles || []).forEach((nivel) => {
            (nivel.secciones || []).forEach((seccion) => {
                sectionCount += 1;
                if (seccion.ocupado) palletCount += 1;
            });
        });
    });

    rackCountEl.textContent = String(racks.length);
    sectionCountEl.textContent = String(sectionCount);
    palletCountEl.textContent = String(palletCount);
}

function renderWarehouseData(nextData) {
    visualizationData = nextData || {};
    racks = Array.isArray(visualizationData.racks) ? visualizationData.racks : [];
    updateMetrics();

    if (emptyEl) {
        emptyEl.hidden = racks.length > 0;
    }

    if (!racks.length) {
        while (sceneRoot.children.length) {
            const child = sceneRoot.children.pop();
            disposeObject(child);
        }
        pickables.length = 0;
        updateSelection(null);
        renderer.render(scene, camera);
        return;
    }

    buildScene();
    resize();
}

function updateSelection(mesh) {
    if (selectedMesh && selectedMesh.userData.originalMaterial) {
        selectedMesh.material = selectedMesh.userData.originalMaterial;
    }

    selectedMesh = mesh;
    if (selectedMesh) {
        selectedMesh.userData.originalMaterial = selectedMesh.material;
        selectedMesh.material = highlightMaterial;
        selectedItem.textContent = selectedMesh.userData.label || 'Elemento';
        selectedLocation.textContent = selectedMesh.userData.location || '-';
        selectedPallet.textContent = selectedMesh.userData.pallet || '-';
        return;
    }

    selectedItem.textContent = 'Ninguna';
    selectedLocation.textContent = '-';
    selectedPallet.textContent = '-';
}

function onPointerDown(event) {
    orbit.dragging = true;
    orbit.lastX = event.clientX;
    orbit.lastY = event.clientY;

    const rect = renderer.domElement.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects(pickables, false)[0];
    updateSelection(hit ? hit.object : null);
}

function onPointerMove(event) {
    if (!orbit.dragging) {
        return;
    }

    const dx = event.clientX - orbit.lastX;
    const dy = event.clientY - orbit.lastY;
    orbit.lastX = event.clientX;
    orbit.lastY = event.clientY;
    orbit.theta -= dx * 0.008;
    orbit.phi = Math.min(Math.PI * 0.48, Math.max(Math.PI * 0.16, orbit.phi + dy * 0.006));
    updateCamera();
}

function onPointerUp() {
    orbit.dragging = false;
}

function onWheel(event) {
    event.preventDefault();
    orbit.radius = Math.min(60, Math.max(8, orbit.radius + event.deltaY * 0.018));
    updateCamera();
}

function resize() {
    const width = Math.max(320, canvasHost.clientWidth);
    const height = Math.max(320, canvasHost.clientHeight);
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
}

function animate() {
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
}

function connectRealtime() {
    const rawPath = canvasHost.dataset.wsUrl;
    if (!rawPath || !window.WebSocket) {
        return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(`${protocol}://${window.location.host}${rawPath}`);

    socket.addEventListener('message', (event) => {
        let message = null;
        try {
            message = JSON.parse(event.data);
        } catch (error) {
            return;
        }

        if (message && message.type === 'warehouse_3d_update') {
            renderWarehouseData(message.payload);
        }
    });

    socket.addEventListener('close', () => {
        setTimeout(connectRealtime, 2500);
    });
}

renderWarehouseData(visualizationData);
animate();
renderer.domElement.addEventListener('pointerdown', onPointerDown);
renderer.domElement.addEventListener('pointermove', onPointerMove);
renderer.domElement.addEventListener('pointerup', onPointerUp);
renderer.domElement.addEventListener('pointerleave', onPointerUp);
renderer.domElement.addEventListener('wheel', onWheel, { passive: false });
window.addEventListener('resize', resize);
connectRealtime();
