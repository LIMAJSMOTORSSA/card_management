// nfc_dashboard/static/nfc_dashboard/js/home.js

document.addEventListener('DOMContentLoaded', function() {
    initializeSidebarToggle();
    initializeProfileDropdown();
    initializeNFCStatusChecker();
});

function initializeSidebarToggle() {
    const toggleSidebar = document.querySelector('nav .toggle-sidebar');
    const sidebar = document.getElementById('sidebar');

    toggleSidebar.addEventListener('click', function () {
        sidebar.classList.toggle('hide');
    });
}

function initializeProfileDropdown() {
    const profile = document.querySelector('nav .profile');
    const imgProfile = profile.querySelector('img');
    const dropdownProfile = profile.querySelector('.profile-link');

    imgProfile.addEventListener('click', function () {
        dropdownProfile.classList.toggle('show');
    });

    window.addEventListener('click', function (e) {
        if (!profile.contains(e.target)) {
            dropdownProfile.classList.remove('show');
        }
    });
}

function initializeNFCStatusChecker() {
    const statusCards = document.querySelectorAll('.status-card');
    if (!statusCards.length) return;

    function checkNFCReaderStatus() {
        // Appeler la vue AJAX pour obtenir les nouvelles informations
        fetch("/ajax/home/")
            .then(response => response.json())
            .then(data => {
                data.reader_info.forEach((reader, index) => {
                    const card = statusCards[index];
                    if (!card) return;

                    if (reader.card_present) {
                        card.classList.add('connected');
                        card.classList.remove('disconnected');
                        // Changer l'icône en flèche verte
                        const icon = card.querySelector('.icon');
                        icon.classList.remove('bxs-x-circle');
                        icon.classList.add('bxs-right-arrow-alt');
                        icon.style.color = 'var(--green)';
                        card.querySelector('#nfcStatus').textContent = 'Présente';
                        const details = card.querySelector('#nfcDetails');
                        if (details) details.style.display = 'block';
                    } else {
                        card.classList.add('disconnected');
                        card.classList.remove('connected');
                        // Changer l'icône en croix grise
                        const icon = card.querySelector('.icon');
                        icon.classList.remove('bxs-right-arrow-alt');
                        icon.classList.add('bxs-x-circle');
                        icon.style.color = 'var(--dark-grey)';
                        card.querySelector('#nfcStatus').textContent = 'Absente';
                        const details = card.querySelector('#nfcDetails');
                        if (details) details.style.display = 'none';
                    }

                    if (reader.error) {
                        const errorParagraph = card.querySelector('.error');
                        if (errorParagraph) {
                            errorParagraph.textContent = `Erreur: ${reader.error}`;
                            errorParagraph.style.display = 'block';
                        }
                    } else {
                        const errorParagraph = card.querySelector('.error');
                        if (errorParagraph) {
                            errorParagraph.textContent = '';
                            errorParagraph.style.display = 'none';
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Erreur lors de la mise à jour des statuts NFC:', error);
            });
    }

    setInterval(checkNFCReaderStatus, 5000); // Toutes les 5 secondes
    checkNFCReaderStatus(); // Appel initial
}
