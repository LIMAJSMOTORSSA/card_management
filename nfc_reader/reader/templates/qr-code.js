document.addEventListener('DOMContentLoaded', function() {
    const startScanButton = document.getElementById('startScan');
    const qrScannerModal = new bootstrap.Modal(document.getElementById('qrScannerModal'));
    const userInfoModal = new bootstrap.Modal(document.getElementById('userInfoModal'));
    const qrScanner = document.getElementById('qrScanner');
    
    let html5QrCode;

    startScanButton.addEventListener('click', () => {
        qrScannerModal.show();
        startQRScanner();
    });

    function startQRScanner() {
        html5QrCode = new Html5Qrcode("qrScanner");
        html5QrCode.start(
            { facingMode: "environment" },
            {
                fps: 10,
                qrbox: { width: 250, height: 250 }
            },
            onScanSuccess,
            onScanFailure
        );
    }

    function onScanSuccess(decodedText, decodedResult) {
        html5QrCode.stop();
        qrScannerModal.hide();
        
        // Simulate API call to get user data
        setTimeout(() => {
            const userData = {
                name: "John",
                surname: "Doe",
                profilePic: "https://example.com/profile.jpg"
            };
            showUserInfo(userData);
        }, 1000);
    }

    function onScanFailure(error) {
        console.warn(`QR Code scanning failed: ${error}`);
    }

    function showUserInfo(userData) {
        document.getElementById('userName').textContent = userData.name;
        document.getElementById('userSurname').textContent = userData.surname;
        document.getElementById('userProfilePic').src = userData.profilePic;
        userInfoModal.show();
    }

    // Stop scanning when the modal is closed
    document.getElementById('qrScannerModal').addEventListener('hidden.bs.modal', () => {
        if (html5QrCode) {
            html5QrCode.stop();
        }
    });
});