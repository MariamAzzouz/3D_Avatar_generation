let avatarMesh, hairMesh, currentEyes;

function initAvatar(avatarData) {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(avatarData.vertices.flat(), 3));
    geometry.setIndex(avatarData.triangles.flat());
    geometry.computeVertexNormals();
    
    const material = new THREE.MeshStandardMaterial({ 
        color: 0xE2B681,
        transparent: true,
        opacity: 1
    });

    avatarMesh = new THREE.Mesh(geometry, material);
    avatarMesh.scale.set(0.00090, 0.00090, 0.00090);
    scene.add(avatarMesh);
}

function updateAvatarSkinColor(color) {
    if (avatarMesh && avatarMesh.material) {
        avatarMesh.material.color.setStyle(color);
    }
}

// Fonctions pour les cheveux et les yeux... 