// ===== Refrescar imagen del ESP32-CAM =====
function refreshImage() {
    const img = document.getElementById('streamImage');
    if (img) {
        const timestamp = new Date().getTime();
        img.src = 'http://192.168.243.10/capture?_=' + timestamp;
    }
}
setInterval(refreshImage, 1000);

// ===== Modal =====
const streamImage = document.getElementById('streamImage');
const modal = document.getElementById('imageModal');
const modalImg = document.getElementById('modalImg');
const closeModal = document.getElementById('closeModal');

if (streamImage && modal && modalImg && closeModal) {
    streamImage.onclick = function() {
        modal.style.display = 'flex';
        modalImg.src = this.src;
    }

    closeModal.onclick = function() {
        modal.style.display = 'none';
    }

    modal.onclick = function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    }
}

// ===== Apagar servidor =====
document.getElementById("shutdown-btn").addEventListener("click", async () => {
    const confirmShutdown = confirm("¿Deseas apagar la interfaz y cerrar el servidor?");
    if (!confirmShutdown) return;

    try {
        console.log("[Cliente] Enviando solicitud de cierre...");
        const response = await fetch("/cerrar");
        if (response.ok) {
            console.log("[Cliente] Servidor cerrado correctamente.");
            window.location.href = "exit.html";
        } else {
            alert("No se pudo apagar el servidor correctamente.");
        }
    } catch (err) {
        console.error("[Cliente] Error al enviar la solicitud de apagado:", err);
        alert("Error de comunicación con el servidor.");
    }
});
