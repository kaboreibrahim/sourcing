// Gestion du menu mobile
document.addEventListener('DOMContentLoaded', function() {
    // Éléments du DOM
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileLocalisationMenu = document.getElementById('mobile-localisation-menu');
    const mobileLocalisationDropdown = document.getElementById('mobile-localisation-dropdown');
    
    // Toggle menu mobile
    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // Toggle sous-menu localisation sur mobile
    if (mobileLocalisationMenu) {
        mobileLocalisationMenu.addEventListener('click', function(e) {
            e.preventDefault();
            mobileLocalisationDropdown.classList.toggle('hidden');
            const icon = mobileLocalisationMenu.querySelector('i:last-child');
            icon.classList.toggle('ri-arrow-down-s-line');
            icon.classList.toggle('ri-arrow-up-s-line');
        });
    }
    
    // Fermer le menu au clic en dehors
    document.addEventListener('click', function(e) {
        if (mobileMenu && !mobileMenu.contains(e.target) && e.target !== mobileMenuButton) {
            mobileMenu.classList.add('hidden');
        }
    });
    
    // Gestion du menu utilisateur
    const userMenuButton = document.getElementById('userMenuButton');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenuButton && userDropdown) {
        userMenuButton.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('hidden');
        });
        
        // Fermer le menu utilisateur en cliquant ailleurs
        document.addEventListener('click', function() {
            userDropdown.classList.add('hidden');
        });
        
        userDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
    
    // Fermer les menus déroulants en scrollant
    window.addEventListener('scroll', function() {
        if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
            mobileMenu.classList.add('hidden');
        }
        if (userDropdown && !userDropdown.classList.contains('hidden')) {
            userDropdown.classList.add('hidden');
        }
    });
});
