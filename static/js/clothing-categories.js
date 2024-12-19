document.addEventListener('DOMContentLoaded', function() {
    // Gestion des boutons homme/femme
    const genderButtons = document.querySelectorAll('.gender-button');
    const clothingSections = document.querySelectorAll('.clothing-section');

    genderButtons.forEach(button => {
        button.addEventListener('click', function() {
            const gender = this.dataset.gender;
            
            // Mise à jour des boutons
            genderButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Mise à jour des sections
            clothingSections.forEach(section => {
                if (section.dataset.gender === gender) {
                    section.classList.add('active');
                } else {
                    section.classList.remove('active');
                }
            });
        });
    });

    // Gestion des cartes de vêtements
    const clothCards = document.querySelectorAll('.cloth-card');
    clothCards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (!e.target.closest('.cloth-details')) {
                this.classList.toggle('expanded');
            }
        });
    });
}); 