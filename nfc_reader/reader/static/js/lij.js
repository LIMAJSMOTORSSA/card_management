document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const menuTextElements = document.querySelectorAll('.menu-text');
    const mainContent = document.querySelector('.main-content');
    const navbar = document.querySelector('.navbar');
    const navigationLink = document.querySelector('[data-bs-target="#navigationSubmenu"]');
    const submenu = document.getElementById('navigationSubmenu');

    // Function to toggle sidebar
    function toggleSidebar() {
        sidebar.classList.toggle('collapsed');
        menuTextElements.forEach(text => {
            text.classList.toggle('hidden');
        });
        mainContent.classList.toggle('expanded');
        navbar.classList.toggle('expanded');

        // Close submenu when sidebar is collapsed
        if (sidebar.classList.contains('collapsed')) {
            closeSubmenu();
        }
    }

    // Function to toggle submenu
    function toggleSubmenu(e) {
        e.preventDefault();
        if (sidebar.classList.contains('collapsed')) {
            toggleSidebar();
            setTimeout(() => {
                openSubmenu();
            }, 300); // Wait for sidebar animation to complete
        } else {
            submenu.classList.contains('show') ? closeSubmenu() : openSubmenu();
        }
    }

    // Function to open submenu with animation
    function openSubmenu() {
        submenu.style.display = 'block';
        submenu.style.height = '0px';
        submenu.style.overflow = 'hidden';
        submenu.style.transition = 'height 0.3s ease';
        
        setTimeout(() => {
            submenu.style.height = submenu.scrollHeight + 'px';
        }, 0);

        setTimeout(() => {
            submenu.style.height = '';
            submenu.style.overflow = '';
            submenu.classList.add('show');
            navigationLink.setAttribute('aria-expanded', 'true');
        }, 300);
    }

    // Function to close submenu with animation
    function closeSubmenu() {
        submenu.style.height = submenu.scrollHeight + 'px';
        submenu.style.overflow = 'hidden';
        submenu.style.transition = 'height 0.3s ease';

        setTimeout(() => {
            submenu.style.height = '0px';
        }, 0);

        setTimeout(() => {
            submenu.style.display = '';
            submenu.style.height = '';
            submenu.style.overflow = '';
            submenu.classList.remove('show');
            navigationLink.setAttribute('aria-expanded', 'false');
        }, 300);
    }

    // Event listeners
    menuToggle.addEventListener('click', toggleSidebar);
    navigationLink.addEventListener('click', toggleSubmenu);

    // Adjust submenu visibility when window is resized
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 768 && !sidebar.classList.contains('collapsed')) {
            toggleSidebar();
        }
    });

    // Observer for sidebar class changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const isCollapsed = sidebar.classList.contains('collapsed');
                if (isCollapsed && submenu.classList.contains('show')) {
                    closeSubmenu();
                }
            }
        });
    });

    observer.observe(sidebar, { attributes: true });

    // QR Code Modal
    const qrCodeButton = document.getElementById('qrCodeButton');
    const qrCodeModal = new bootstrap.Modal(document.getElementById('qrCodeModal'));

    qrCodeButton.addEventListener('click', function() {
        qrCodeModal.show();
    });

    // Virtual Card Modal
    const virtualCard = document.getElementById('virtualCard');
    const ticketApprovedModal = new bootstrap.Modal(document.getElementById('ticketApprovedModal'));

    virtualCard.addEventListener('click', function() {
        ticketApprovedModal.show();
    });
});