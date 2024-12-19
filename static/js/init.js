let scene, camera, renderer, controls;
let avatarMesh, hairMesh, clothMesh, currentEyes;

function initAvatarViewer(avatarData) {
    debugLog('Initializing avatar viewer...');
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xffffff);
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / 2 / window.innerHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ antialias: true });
    
    renderer.setSize(window.innerWidth / 2, window.innerHeight);
    document.getElementById('avatar-viewer').appendChild(renderer.domElement);
    
    // Create avatar mesh with centered positioning
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(avatarData.vertices.flat(), 3));
    geometry.setIndex(avatarData.triangles.flat());
    geometry.computeVertexNormals();
    
    // Compute bounding box of avatar geometry
    geometry.computeBoundingBox();
    const avatarBbox = geometry.boundingBox;
    const avatarCenter = new THREE.Vector3();
    avatarBbox.getCenter(avatarCenter);
    
    const material = new THREE.MeshStandardMaterial({ 
        color: 0xE2B681,
        transparent: true,
        opacity: 1
    });

    avatarMesh = new THREE.Mesh(geometry, material);
    
    // Center the avatar mesh
    avatarMesh.scale.set(0.00090, 0.00090, 0.00090);
    avatarMesh.position.set(0, -avatarCenter.y * 0.00090, 0);
    scene.add(avatarMesh);

    setupCamera();
    setupLights();
}

function setupCamera() {
    camera.position.set(0, 0, 2);
    camera.lookAt(0, 0, 0);
    
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 0, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.screenSpacePanning = false;
    controls.minDistance = 1;
    controls.maxDistance = 5;
    controls.maxPolarAngle = Math.PI;
    controls.update();
}

function setupLights() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
} 