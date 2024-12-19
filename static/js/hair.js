let currentHairMesh = null;

function clearCurrentHair() {
    debugLog('Clearing current hair model');
    if (currentHairMesh) {
        scene.remove(currentHairMesh);
        if (currentHairMesh.geometry) {
            currentHairMesh.geometry.dispose();
        }
        if (currentHairMesh.material) {
            currentHairMesh.material.dispose();
        }
        currentHairMesh = null;
        renderer.render(scene, camera);
    }
}

function loadLongHairModel() {
    debugLog('Starting long hair model loading...');
    clearCurrentHair();
    
    if (!scene) {
        debugLog('Error: Scene not initialized');
        return;
    }

    const objLoader = new THREE.OBJLoader();
    objLoader.load(
        '/static/models/hair/long.obj',
        function(object) {
            try {
                debugLog('Model loaded, processing...');
                
                object.traverse(function(child) {
                    if (child instanceof THREE.Mesh) {
                        const hairMaterial = new THREE.MeshPhongMaterial({
                            color: 0x3d2314,
                            shininess: 30,
                            specular: 0x444444,
                            side: THREE.DoubleSide,
                            transparent: false,
                            opacity: 1.0,
                            flatShading: true
                        });

                        const geometry = child.geometry;
                        geometry.computeVertexNormals();
                        geometry.computeBoundingBox();

                        currentHairMesh = new THREE.Mesh(geometry, hairMaterial);

                        const scale = 3.0;
                        currentHairMesh.scale.set(scale, scale, scale);
                        currentHairMesh.position.set(0, -0.23, 0);
                        currentHairMesh.rotation.set(0, 0, 0);

                        scene.add(currentHairMesh);
                        debugLog('New hair mesh added to scene');

                        renderer.render(scene, camera);
                    }
                });
            } catch (error) {
                debugLog(`Error processing model: ${error.message}`);
                console.error('Processing error:', error);
            }
        },
        function(xhr) {
            const percentComplete = xhr.loaded / xhr.total * 100;
            debugLog(`Loading progress: ${percentComplete.toFixed(2)}%`);
        },
        function(error) {
            debugLog(`Error loading model: ${error.message}`);
            console.error('Loading error:', error);
        }
    );
}

function loadHairModel(hairType) {
    debugLog(`Loading hair model: ${hairType}`);
    
    // Nettoyer l'ancien modèle d'abord
    clearCurrentHair();
    
    if (!scene) {
        debugLog('Error: Scene not initialized');
        return;
    }

    // Add a point light to better illuminate the model
    const pointLight = new THREE.PointLight(0xffffff, 1);
    pointLight.position.set(0, 1, 1);
    //scene.add(pointLight);

    const objLoader = new THREE.OBJLoader();
    const modelUrl = `/static/models/hair/${hairType}.obj`;
    debugLog(`Loading model from: ${modelUrl}`);

    objLoader.load(
        modelUrl,
        function(object) {
            debugLog('Model loaded successfully');
            
            object.traverse(function(child) {
                if (child instanceof THREE.Mesh) {
                    const hairMaterial = new THREE.MeshPhongMaterial({
                        color: 0x3d2314,
                        shininess: 10,
                        specular: 0x444444,
                        side: THREE.DoubleSide,
                        wireframe: false, // Disabled wireframe
                        transparent: true,
                        opacity: 1.0
                    });

                    // Compute bounding box
                    child.geometry.computeBoundingBox();
                    const bbox = child.geometry.boundingBox;
                    
                    // Center geometry
                    const center = new THREE.Vector3();
                    bbox.getCenter(center);
                    child.geometry.translate(-center.x, -center.y, -center.z);
                    
                    currentHairMesh = new THREE.Mesh(child.geometry, hairMaterial);
                    
                    // Position relative to avatar center
                    currentHairMesh.scale.set(0.009, 0.009, 0.009);
                    currentHairMesh.position.copy(avatarMesh.position);
                    currentHairMesh.position.y += 1.32;
                    currentHairMesh.position.x += 0.0032;
                    currentHairMesh.position.z -= 0.009; // Offset up from avatar center
                    currentHairMesh.rotation.set(0, 0, 0);
                    
                    scene.add(currentHairMesh);
                    debugLog('Hair mesh added');
                    
                    // Keep camera focused on scene center
                    camera.position.set(0, 0, 2);
                    camera.lookAt(0, 0, 0);
                    controls.target.set(0, 0, 0);
                    controls.update();
                }
            });
        },
        function(xhr) {
            debugLog(`Loading progress: ${(xhr.loaded / xhr.total * 100).toFixed(2)}%`);
        },
        function(error) {
            debugLog(`Error loading hair model: ${error.message}`);
            console.error('Detailed error:', error);
        }
    );
}

// Modifier le gestionnaire d'événements
document.querySelectorAll('.hair-option').forEach(image => {
    image.addEventListener('click', function() {
        const hairType = this.alt;
        debugLog(`Hair option clicked: ${hairType}`);
        
        // Supprimer la classe active de toutes les options
        document.querySelectorAll('.hair-option').forEach(img => {
            img.classList.remove('active');
        });
        
        // Ajouter la classe active à l'option cliquée
        this.classList.add('active');
        
        // Nettoyer l'ancien modèle avant d'en charger un nouveau
        clearCurrentHair();
        
        if (hairType === 'long') {
            loadLongHairModel();
        } else {
            loadHairModel(hairType);
        }
    });
});
