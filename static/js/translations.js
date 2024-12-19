const translations = {
    en: {
        title: "Customize Avatar",
        skinColor: "Skin Color",
        hair: "Hair",
        search: "Search for clothing...",
        reset: "Reset",
        size: "Size",
        apply: "Apply",
        colors: {
            light: "Light",
            medium: "Medium",
            olive: "Olive",
            brown: "Brown",
            dark: "Dark"
        },
        clothingTypes: {
            dress: "Dress",
            skirt: "Skirt",
            pull: "Sweater"
        },
        clothingColors: {
            blue: "Blue",
            red: "Red",
            green: "Green",
            black: "Black",
            purple: "Purple"
        }
    },
    fr: {
        title: "Personnaliser l'avatar",
        skinColor: "Couleur de peau",
        hair: "Cheveux",
        search: "Rechercher un vêtement...",
        reset: "Réinitialiser",
        size: "Taille",
        apply: "Appliquer",
        colors: {
            light: "Claire",
            medium: "Moyenne",
            olive: "Olive",
            brown: "Brune",
            dark: "Foncée"
        },
        clothingTypes: {
            dress: "Robe",
            skirt: "Jupe",
            pull: "Pull"
        },
        clothingColors: {
            blue: "Bleu",
            red: "Rouge",
            green: "Vert",
            black: "Noir",
            purple: "Violet"
        }
    }
};

function updateLanguage(lang) {
    document.querySelector('h1').textContent = translations[lang].title;
    
    document.querySelector('.skin-section h3').textContent = translations[lang].skinColor;
    document.querySelector('.hair-section h3').textContent = translations[lang].hair;
    
    document.querySelectorAll('.skin-color').forEach(color => {
        const colorKey = color.title.toLowerCase();
        color.title = translations[lang].colors[colorKey];
    });
    
    document.querySelectorAll('.cloth-color').forEach(color => {
        const colorKey = color.title.toLowerCase();
        color.title = translations[lang].clothingColors[colorKey];
    });
    
    document.querySelectorAll('.size-input option').forEach(option => {
        if (option.value === "") {
            option.textContent = translations[lang].size;
        }
    });
    
    document.querySelectorAll('.apply-size').forEach(button => {
        button.textContent = translations[lang].apply;
    });
    
    document.querySelectorAll('.cloth-option').forEach(cloth => {
        const clothKey = cloth.alt;
        cloth.title = translations[lang].clothingTypes[clothKey];
    });
    
    document.getElementById('search-input').placeholder = translations[lang].search;
    
    const resetButton = document.getElementById('reset-button');
    resetButton.innerHTML = `<i class="fas fa-undo"></i> ${translations[lang].reset}`;
}
