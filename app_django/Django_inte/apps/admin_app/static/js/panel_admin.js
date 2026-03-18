const avatarMenu = document.getElementById("avatarMenu");

if (avatarMenu) {
    avatarMenu.addEventListener("click", () => {
        avatarMenu.classList.toggle("active");
    });
}

window.addEventListener("click", function(e){
    if(avatarMenu && !avatarMenu.contains(e.target)){
        avatarMenu.classList.remove("active");
    }
});

function closeSidebarIfOpen() {
    const sidebar = document.querySelector(".sidebar");
    const overlay = document.querySelector(".sidebar-overlay");
    if (!sidebar || !overlay) return;

    if (sidebar.classList.contains("active")) {
        sidebar.classList.remove("active");
        overlay.classList.remove("active");
        document.body.style.overflow = "";
    }
}

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeSidebarIfOpen();
});

document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.querySelector(".sidebar");
    if (!sidebar) return;

    // En móvil, cerrar el sidebar al navegar (mejora UX).
    sidebar.querySelectorAll("a").forEach((a) => {
        a.addEventListener("click", () => {
            if (window.innerWidth <= 900) closeSidebarIfOpen();
        });
    });
});
// ===== AUTO CERRAR MENSAJES =====
document.addEventListener("DOMContentLoaded", function(){

    const alertas = document.querySelectorAll(".alerta");

    alertas.forEach((alerta) => {

        setTimeout(() => {
            alerta.style.transition = "opacity 0.4s ease, transform 0.3s ease";
            alerta.style.opacity = "0";
            alerta.style.transform = "translateX(20px)";

            setTimeout(() => {
                alerta.remove();
            }, 400);

        }, 3000); // 3 segundos

    });

});
