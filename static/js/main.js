document.addEventListener('DOMContentLoaded', function() {
    initAvatarViewer(window.avatarData);
    initUI();
    
    const initialLang = document.getElementById('language-select').value;
    updateLanguage(initialLang);
    
    // Event listeners
    document.getElementById('language-select').addEventListener('change', function(e) {
        updateLanguage(e.target.value);
    });
    
    document.getElementById('reset-button').addEventListener('click', resetAvatar);
    
    window.addEventListener('beforeunload', clearCurrentHair);
}); 