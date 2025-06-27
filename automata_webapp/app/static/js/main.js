function toggleMenu(header) {
    const submenu = header.nextElementSibling;
    const chevron = header.querySelector('.chevron');
    
    // Close other menus
    const allHeaders = document.querySelectorAll('.menu-header');
    allHeaders.forEach(h => {
        if (h !== header) {
            h.classList.remove('active');
            const otherSubmenu = h.nextElementSibling;
            const otherChevron = h.querySelector('.chevron');
            otherSubmenu.classList.remove('expanded');
            otherChevron.classList.remove('rotated');
        }
    });
    
    // Toggle current menu
    header.classList.toggle('active');
    submenu.classList.toggle('expanded');
    chevron.classList.toggle('rotated');
}

function toggleSubmenu(item) {
    const submenu = item.nextElementSibling;
    const chevron = item.querySelector('.chevron');
    
    if (submenu && submenu.classList.contains('submenu')) {
        submenu.classList.toggle('expanded');
        chevron.classList.toggle('rotated');
    }
}

// Initialize first menu as open
document.addEventListener('DOMContentLoaded', function() {
    const firstMenu = document.querySelector('.menu-header');
    if (firstMenu) {
        toggleMenu(firstMenu);
    }
});

// Handle logout
document.querySelector('.logout-btn').addEventListener('click', function() {
    if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
        // Implement logout logic here
        console.log('Déconnexion...');
    }
});

// Handle submenu clicks
document.querySelectorAll('.submenu-item').forEach(item => {
    item.addEventListener('click', function(e) {
        // Prevent bubbling if this is a submenu toggle
        if (this.querySelector('.chevron')) {
            e.stopPropagation();
            return;
        }
        
        // Remove active class from all items
        document.querySelectorAll('.submenu-item').forEach(i => i.classList.remove('active'));
        
        // Add active class to clicked item
        this.classList.add('active');
        
        console.log('Navigation vers:', this.textContent.trim());
    });
});
