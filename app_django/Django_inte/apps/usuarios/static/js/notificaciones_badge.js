(function () {
  const badge = document.getElementById("notifBadge");
  const bell = document.getElementById("notifBell");
  if (!badge || !bell) return;

  async function refresh() {
    try {
      const res = await fetch("/usuarios/notificaciones/api/unread-count/");
      const data = await res.json();
      const n = Number(data.unread || 0);
      badge.textContent = n > 99 ? "99+" : String(n);
      badge.style.display = n > 0 ? "inline-flex" : "none";
    } catch (e) {
      // silencioso
    }
  }

  bell.addEventListener("click", (e) => {
    e.preventDefault();
    window.location.href = "/usuarios/notificaciones/";
  });

  refresh();
  setInterval(refresh, 60000);
})();
