let isScanning = false;
let currentCameraId = null;
let cameras = [];
const html5QrCode = new Html5Qrcode("reader");

const startBtn = document.getElementById("startBtn");
const txtBtn = document.getElementsByClassName('txt_scan')[0];
const txtCam = document.getElementsByClassName('txt_cam')[0];
const toggleBtn = document.getElementById("toggleBtn");
const toast = document.getElementById("toast");
const toastText = document.getElementById("toastText");
const toastIcon = document.getElementById("toastIcon");
const instruction = document.getElementById("scannerInstruction");

function showToast(message, type = "success") {
    if (!toast) return;
    toastText.textContent = message;
    toast.className = "toast show " + type;
    toastIcon.innerHTML = type === "success" ? "<i class=\"bi bi-check-circle-fill\"></i>" : type === "error" ? "<i class=\"bi bi-x-circle-fill\"></i>" : "<i class=\"bi bi-info-circle\"></i>";

    clearTimeout(toast._hideTimeout);
    toast._hideTimeout = setTimeout(() => {
        toast.classList.remove("show");
    }, 3200);
}

function setButtonsState(scanning) {
    isScanning = scanning;
    txtBtn.textContent = scanning ? "Stop scanning" : "Start scanning";
    startBtn.style.backgroundColor = scanning ? "var(--red)" : "var(--green)";
    instruction.textContent = scanning
        ? "Point your camera at a QR code inside the frame."
        : "Tap Start to open the camera and scan a QR code.";
}

function stopScanning() {
    if (!isScanning) return;
    html5QrCode.stop().catch(() => {});
    setButtonsState(false);
}

function onScanSuccess(decodedText) {
    if (!isScanning) return;

    let payload;
    try {
        payload = JSON.parse(decodedText);
    } catch (error) {
        showToast("Invalid QR code", "error");
        return;
    }

    // Stop scanning while we validate the result
    stopScanning();

    fetch("/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                showToast("Scan validated", "success");
            } else {
                showToast("Scan rejected. Try again.", "error");
            }
        })
        .catch(() => {
            showToast("Server error. Try again.", "error");
        });
}

function pickCamera(preferredLabel) {
    if (!cameras.length) return null;
    const match = cameras.find(cam => cam.label.toLowerCase().includes(preferredLabel));
    return match || cameras[0];
}

function refreshCameraList() {
    return Html5Qrcode.getCameras().then(found => {
        cameras = found || [];
        if (cameras.length) {
            const chosen = pickCamera("back");
            currentCameraId = chosen.id;
            toggleBtn.disabled = cameras.length < 2;
            txtCam.textContent = cameras.length > 1 ? "Switch camera" : "No other camera";
            toggleBtn.style.backgroundColor = cameras.length > 1 ? "var(--blue)" : "var(--gray)";
        } else {
            currentCameraId = null;
            toggleBtn.disabled = true;
            txtCam.textContent = "No camera";
            toggleBtn.style.backgroundColor = "var(--gray)";
        }
    });
}

function cycleCamera() {
    if (!cameras.length) return;
    const currentIndex = cameras.findIndex(cam => cam.id === currentCameraId);
    const nextIndex = (currentIndex + 1) % cameras.length;
    currentCameraId = cameras[nextIndex].id;
    if (isScanning) {
        stopScanning();
        startScanning();
    }
}

function startScanning() {
    if (!currentCameraId) {
        showToast("No camera found", "error");
        return;
    }

    html5QrCode
        .start(
            currentCameraId,
            { fps: 10, qrbox: { width: 280, height: 280 } },
            onScanSuccess
        )
        .then(() => {
            setButtonsState(true);
        })
        .catch(err => {
            console.error("Camera start failed", err);
            showToast("Unable to access camera", "error");
        });
}

startBtn.addEventListener("click", () => {
    if (isScanning) {
        stopScanning();
        return;
    }

    refreshCameraList().then(() => startScanning());
});

toggleBtn.addEventListener("click", () => {
    if (!cameras.length) {
        showToast("No camera available", "warning");
        return;
    }
    cycleCamera();
});

// Preload camera list so buttons are correct on load
refreshCameraList();
