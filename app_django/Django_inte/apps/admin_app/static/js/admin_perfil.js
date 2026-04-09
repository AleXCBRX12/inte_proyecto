    function cerrarPerfil() {
        const card = document.getElementById('card');
        const overlay = document.getElementById('overlay');
        
        card.classList.add('closing');
        overlay.style.transition = 'opacity 0.3s ease';
        overlay.style.opacity = '0';

        setTimeout(() => {
            window.history.back();
        }, 300);
    }

    // 🔹 Cerrar al hacer clic fuera
    function cerrarDesdeOverlay(event) {
        const card = document.getElementById('card');

        if (!card.contains(event.target)) {
            cerrarPerfil();
        }
    }