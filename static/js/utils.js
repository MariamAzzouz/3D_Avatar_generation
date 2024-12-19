function debugLog(message) {
    console.log(message);
    const debugDiv = document.getElementById('debug-info');
    if (debugDiv) {
        debugDiv.innerHTML += message + '<br>';
        const lines = debugDiv.innerHTML.split('<br>');
        if (lines.length > 5) {
            debugDiv.innerHTML = lines.slice(-5).join('<br>');
        }
    }
}

function resetAvatar() {
    debugLog('Starting avatar reset...');

    // Réinitialiser les vêtements
    if (clothMesh) {
        debugLog('Removing cloth mesh');
        scene.remove(clothMesh);
        if (clothMesh.geometry) clothMesh.geometry.dispose();
        if (clothMesh.material) {
            if (Array.isArray(clothMesh.material)) {
                clothMesh.material.forEach(material => material.dispose());
            } else {
                clothMesh.material.dispose();
            }
        }
        clothMesh = null;
    }

    // Réinitialiser les cheveux
    if (hairMesh) {
        debugLog('Removing hair mesh');
        scene.remove(hairMesh);
        if (hairMesh.geometry) hairMesh.geometry.dispose();
        if (hairMesh.material) {
            if (Array.isArray(hairMesh.material)) {
                hairMesh.material.forEach(material => material.dispose());
            } else {
                hairMesh.material.dispose();
            }
        }
        hairMesh = null;
    }

    // Réinitialiser les yeux
    if (currentEyes) {
        debugLog('Removing eyes');
        scene.remove(currentEyes);
        if (currentEyes.geometry) currentEyes.geometry.dispose();
        if (currentEyes.material) currentEyes.material.dispose();
        currentEyes = null;
    }

    // Réinitialiser les sélections actives dans l'interface
    document.querySelectorAll('.cloth-option.active, .hair-option.active, .eye-option.active').forEach(element => {
        element.classList.remove('active');
    });

    // Masquer toutes les personnalisations
    document.querySelectorAll('.cloth-customization').forEach(element => {
        element.style.display = 'none';
    });

    // Forcer le rendu de la scène
    if (renderer && scene && camera) {
        renderer.render(scene, camera);
    }

    debugLog('Avatar reset completed');
} 