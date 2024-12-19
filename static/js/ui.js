function initUI() {
    initClothColorPicker();
    initSearchBar();
    initResetButton();
    initLanguageSelector();
    initHairOptions();
    initClothOptions();
}

function initClothColorPicker() {
    const clothColorOptions = document.querySelectorAll('.cloth-color');
    
    clothColorOptions.forEach(option => {
        option.addEventListener('click', function() {
            const parentClothItem = this.closest('.cloth-item');
            const colorOptions = parentClothItem.querySelectorAll('.cloth-color');
            
            colorOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            
            if (clothMesh) {
                clothMesh.material.color.setStyle(this.dataset.color);
            }
        });
    });
}

function initSearchBar() {
    document.getElementById('search-input').addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        filterClothingItems(searchTerm);
    });
}

function initResetButton() {
    document.getElementById('reset-button').addEventListener('click', resetAvatar);
}

function initLanguageSelector() {
    // Code de sélection de langue existant
}

function initHairOptions() {
    // Code de sélection d'options de cheveux existant
}

function initClothOptions() {
    // Code de sélection d'options de vêtements existant
}

function filterClothingItems(searchTerm) {
    const clothItems = document.querySelectorAll('.cloth-item');
    
    clothItems.forEach(item => {
        const title = item.querySelector('.cloth-option').title.toLowerCase();
        const matchesSearch = title.includes(searchTerm);
        
        if (matchesSearch) {
            item.style.display = '';
            const subcategory = item.closest('.subcategory');
            if (subcategory) subcategory.style.display = '';
            const category = item.closest('.category-section');
            if (category) category.style.display = '';
        } else {
            item.style.display = 'none';
            updateCategoryVisibility(item);
        }
    });
}

function updateCategoryVisibility(item) {
    const subcategory = item.closest('.subcategory');
    if (subcategory) {
        const visibleItems = subcategory.querySelectorAll('.cloth-item[style=""]').length;
        subcategory.style.display = visibleItems === 0 ? 'none' : '';
    }
    
    const category = item.closest('.category-section');
    if (category) {
        const visibleSubcategories = category.querySelectorAll('.subcategory[style=""]').length;
        category.style.display = visibleSubcategories === 0 ? 'none' : '';
    }
} 