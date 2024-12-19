function initClothColorPicker() {
    const clothColorOptions = document.querySelectorAll('.cloth-color');
    
    clothColorOptions.forEach(option => {
        option.addEventListener('click', function() {
            const parentClothItem = this.closest('.cloth-item');
            const colorOptions = parentClothItem.querySelectorAll('.cloth-color');
            
            // Remove active class from all cloth color options in this cloth item
            colorOptions.forEach(opt => opt.classList.remove('active'));
            
            // Add active class to selected option
            this.classList.add('active');
            
            // Update cloth color
            if (clothMesh) {
                clothMesh.material.color.setStyle(this.dataset.color);
            }
        });
    });
}

// Modifier la fonction loadClothModel pour prendre en compte la couleur sélectionnée
function loadClothModel(clothType, size) {
    if (clothMesh) {
        scene.remove(clothMesh);
    }

    const selectedColorElement = document.querySelector('.cloth-color.active');
    const clothColor = selectedColorElement ? selectedColorElement.dataset.color : '#6e88a5'; // couleur par défaut

    fetch('/update_cloth', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cloth: clothType, size: size }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const clothGeometry = new THREE.BufferGeometry();
            clothGeometry.setAttribute('position', new THREE.Float32BufferAttribute(data.cloth_vertices.flat(), 3));
            clothGeometry.setIndex(data.cloth_triangles.flat());
            clothGeometry.computeVertexNormals();

            const clothMaterial = new THREE.MeshStandardMaterial({ 
                color: clothColor,
                side: THREE.DoubleSide
            });

            clothMesh = new THREE.Mesh(clothGeometry, clothMaterial);
            clothMesh.position.y = -0.9;
            clothMesh.position.z = -0.0049;
            clothMesh.scale.set(0.98, 0.98, 0.98);
            scene.add(clothMesh);
            debugLog('Cloth mesh added successfully with color: ' + clothColor);
        }
    })
    .catch(error => debugLog('Error loading cloth: ' + error));
}

// Initialize clothing selection
document.querySelectorAll('.cloth-option').forEach(clothOption => {
    clothOption.addEventListener('click', function() {
        // Reset all cloth options and size selectors
        document.querySelectorAll('.cloth-option').forEach(opt => {
            opt.classList.remove('active');
            opt.nextElementSibling.style.display = 'none';
        });

        // Activate selected cloth and show size selector
        this.classList.add('active');
        this.nextElementSibling.style.display = 'block';
    });
});

// Nouvelle fonction pour charger spécifiquement le modèle "pull"
function loadPullModel(size) {
    debugLog('Loading pull model...');
    
    if (!scene) {
        debugLog('Error: Scene not initialized');
        return;
    }

    const objLoader = new THREE.OBJLoader();
    const modelUrl = `/static/3D_CLOTHING/pull_S.obj`;

    objLoader.load(
        modelUrl,
        function(object) {
            debugLog('Pull model loaded successfully');
            
            // Supprimer l'ancien pull s'il existe
            if (clothMesh) {
                scene.remove(clothMesh);
            }

            object.traverse(function(child) {
                if (child instanceof THREE.Mesh) {
                    // Récupérer la couleur sélectionnée
                    const selectedColorElement = document.querySelector('.cloth-color.active');
                    const pullColor = selectedColorElement ? selectedColorElement.dataset.color : '#6e88a5';

                    const pullMaterial = new THREE.MeshPhongMaterial({
                        color: pullColor,
                        shininess: 30,
                        specular: 0x444444,
                        side: THREE.DoubleSide,
                        transparent: true,
                        opacity: 1.0
                    });

                    // Centrer la géométrie
                    child.geometry.computeBoundingBox();
                    const bbox = child.geometry.boundingBox;
                    const center = new THREE.Vector3();
                    bbox.getCenter(center);
                    child.geometry.translate(-center.x, -center.y, -center.z);

                    clothMesh = new THREE.Mesh(child.geometry, pullMaterial);

                    // Ajuster l'échelle en fonction de la taille
                    let scale = 0.0009;
                    switch(size) {
                        case 'XS': scale *= 0.9; break;
                        case 'S': scale *= 0.95; break;
                        case 'L': scale *= 1.05; break;
                        case 'XL': scale *= 1.1; break;
                    }

                    clothMesh.scale.set(scale, scale, scale);
                    clothMesh.position.set(0, 0.22, 0.0039);
                    clothMesh.rotation.set(0, 0, 0);

                    scene.add(clothMesh);
                    debugLog('Pull mesh added with color: ' + pullColor);
                }
            });
        },
        function(xhr) {
            debugLog(`Loading progress: ${(xhr.loaded / xhr.total * 100).toFixed(2)}%`);
        },
        function(error) {
            debugLog(`Error loading pull model: ${error.message}`);
            console.error('Detailed error:', error);
        }
    );
}

// Nouvelle fonction pour charger spécifiquement le modèle "skirt"
function loadSkirtModel(size) {
    debugLog('Loading skirt model...');
    
    if (!scene) {
        debugLog('Error: Scene not initialized');
        return;
    }

    const objLoader = new THREE.OBJLoader();
    const modelUrl = `/static/3D_CLOTHING/skirt_${size}.obj`;
    debugLog(`Attempting to load skirt from: ${modelUrl}`);

    objLoader.load(
        modelUrl,
        function(object) {
            debugLog('Skirt model loaded successfully');
            
            // Supprimer l'ancien vtement s'il existe
            if (clothMesh) {
                scene.remove(clothMesh);
            }

            object.traverse(function(child) {
                if (child instanceof THREE.Mesh) {
                    // Récupérer la couleur sélectionnée
                    const selectedColorElement = document.querySelector('.cloth-color.active');
                    const skirtColor = selectedColorElement ? selectedColorElement.dataset.color : '#6e88a5';

                    const skirtMaterial = new THREE.MeshPhongMaterial({
                        color: skirtColor,
                        shininess: 30,
                        specular: 0x444444,
                        side: THREE.DoubleSide,
                        transparent: true,
                        opacity: 1.0
                    });

                    // Centrer la géométrie
                    child.geometry.computeBoundingBox();
                    const bbox = child.geometry.boundingBox;
                    const center = new THREE.Vector3();
                    bbox.getCenter(center);
                    child.geometry.translate(-center.x, -center.y, -center.z);

                    clothMesh = new THREE.Mesh(child.geometry, skirtMaterial);

                    // Échelle fixe car la taille est déjà dans le modèle
                    const scale = 0.011;
                    clothMesh.scale.set(scale, scale, scale);
                    clothMesh.position.set(0, -0.03, -0.0049); // Position ajustée pour la jupe
                    clothMesh.rotation.set(Math.PI + Math.PI/2, 0, 0);

                    scene.add(clothMesh);
                    debugLog(`Skirt mesh added with color: ${skirtColor}`);
                }
            });
        },
        function(xhr) {
            debugLog(`Loading progress: ${(xhr.loaded / xhr.total * 100).toFixed(2)}%`);
        },
        function(error) {
            debugLog(`Error loading skirt model: ${error.message}`);
            console.error('Detailed error:', error);
        }
    );
}

// Modifier le gestionnaire d'événements existant
document.querySelectorAll('.apply-size').forEach(button => {
    button.addEventListener('click', function() {
        const clothItem = this.closest('.cloth-item');
        const clothType = clothItem.querySelector('.cloth-option').alt;
        const size = clothItem.querySelector('.size-input').value;

        if (size) {
            switch(clothType) {
                case 'pull':
                    loadPullModel(size);
                    break;
                case 'skirt':
                    loadSkirtModel(size);
                    break;
                default:
                    loadClothModel(clothType, size); // Pour les autres types de vêtements
            }
            debugLog(`Applying ${clothType} in size ${size}`);
        } else {
            debugLog('Please select a size');
        }
    });
});

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
animate();

// Handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / 2 / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth / 2, window.innerHeight);
});

// Gestionnaire pour les couleurs de peau
function initSkinColorPicker() {
    const skinColorOptions = document.querySelectorAll('.skin-color');
    
    skinColorOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove active class from all skin options
            skinColorOptions.forEach(opt => opt.classList.remove('active'));
            
            // Add active class to selected option
            this.classList.add('active');
            
            // Update avatar skin color
            if (avatarMesh) {
                avatarMesh.material.color.setStyle(this.dataset.color);
            }
        });
    });
}

// Add this call to your initAvatarViewer function
initSkinColorPicker();
initClothColorPicker();
