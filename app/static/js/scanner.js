let isScanning = false;
let html5QrCode = new Html5Qrcode("reader");

function onScanSuccess(result) {
    if (!isScanning) return;
    isScanning = false;

    let payload;
    try {
        payload = JSON.parse(result);
    } catch (error) {
        alert("QR code invalide !");
        isScanning = true;
        return;
    }

    fetch("/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            html5QrCode.stop();
            document.getElementById("alert").style.display = "block";

            setTimeout(() => {
                const alertBox = document.getElementById("alert");
                if (alertBox) {
                    alertBox.classList.add("fade-out");
                    setTimeout(() => alertBox.style.display = "none", 500);
                }
            }, 5000);

        } else {
            html5QrCode.stop();
            document.getElementById("alert2").style.display = "block";
            setTimeout(() => {
                const alertBox = document.getElementById("alert2");
                if (alertBox) {
                    alertBox.classList.add("fade-out");
                    setTimeout(() => alertBox.style.display = "none", 500);
                }
            }, 5000);
        }
    })
    .catch(() => {
        alert("Erreur de connexion au serveur.");
        isScanning = true;
    });
}

document.getElementById("startBtn").addEventListener("click", () => {
    Html5Qrcode.getCameras().then(cameras => {
        if (cameras && cameras.length) {
            let backCamera = cameras.find(cam => cam.label.toLowerCase().includes("back")) || cameras[0];
            html5QrCode.start(
                backCamera.id,
                { fps: 10, qrbox: 300 },
                onScanSuccess
            ).then(() => {
                isScanning = true;
            });
        } else {
            alert("Aucune caméra trouvée");
        }
    }).catch(err => {
        console.error("Erreur d'accès caméra", err);
    });
});