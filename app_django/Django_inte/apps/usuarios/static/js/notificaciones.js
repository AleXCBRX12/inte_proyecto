(function () {
  const listEl = document.getElementById("notifList");
  const emptyEl = document.getElementById("notifEmpty");
  const btnAll = document.getElementById("btnMarcarTodoLeido");

  if (!listEl) return;

  const fetchJSON = async (url, opts) => {
    const res = await fetch(url, opts || {});
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || "Request failed");
    return data;
  };

  const render = (items) => {
    if (!items || !items.length) {
      emptyEl.style.display = "block";
      listEl.innerHTML = "";
      return;
    }

    emptyEl.style.display = "none";
    listEl.innerHTML = items
      .map((n) => {
        const badge =
          n.tipo === "warn"
            ? "background:#fff7ed;color:#9a3412;border:1px solid #fed7aa;"
            : n.tipo === "ok"
            ? "background:#ecfdf5;color:#065f46;border:1px solid #a7f3d0;"
            : "background:#eff6ff;color:#1e40af;border:1px solid #bfdbfe;";

        const titleStyle = n.read ? "color:#64748b;" : "color:#0f172a;";
        const containerStyle = n.read
          ? "border:1px solid #e2e8f0;background:#ffffff;opacity:0.85;"
          : "border:1px solid #cbd5e1;background:#ffffff;";

        const link = n.url ? `<a href="${n.url}" style="text-decoration:none;font-weight:700;color:#1f3c88;">Ver</a>` : "";
        const btnRead = n.read
          ? ""
          : `<button data-id="${n.id}" class="btnRead" style="border:1px solid #e2e8f0;background:#f8fafc;border-radius:10px;padding:8px 10px;cursor:pointer;font-weight:700;">Leído</button>`;

        return `
          <div style="${containerStyle} border-radius:14px;padding:14px 14px;display:flex;gap:12px;align-items:flex-start;">
            <div style="${badge} padding:6px 10px;border-radius:999px;font-size:12px;font-weight:800;text-transform:uppercase;">${(n.tipo || "info")}</div>
            <div style="flex:1;">
              <div style="display:flex;justify-content:space-between;gap:12px;align-items:baseline;">
                <div style="font-weight:800;${titleStyle}">${escapeHtml(n.titulo || "Notificación")}</div>
                <div style="font-size:12px;color:#94a3b8;white-space:nowrap;">${n.created_at || ""}</div>
              </div>
              <div style="margin-top:6px;color:#475569;line-height:1.45;">${escapeHtml(n.mensaje || "")}</div>
              <div style="margin-top:10px;display:flex;gap:10px;align-items:center;">
                ${link}
                ${btnRead}
              </div>
            </div>
          </div>
        `;
      })
      .join("");

    listEl.querySelectorAll(".btnRead").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = btn.getAttribute("data-id");
        if (!id) return;
        btn.disabled = true;
        try {
          await fetchJSON(`/usuarios/notificaciones/api/${id}/read/`, { method: "POST" });
          await refresh();
        } catch (e) {
          btn.disabled = false;
          console.error(e);
          alert("No se pudo marcar como leído.");
        }
      });
    });
  };

  const escapeHtml = (s) =>
    String(s ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  async function refresh() {
    const data = await fetchJSON("/usuarios/notificaciones/api/");
    render(data.notificaciones || []);
  }

  if (btnAll) {
    btnAll.addEventListener("click", async () => {
      btnAll.disabled = true;
      try {
        await fetchJSON("/usuarios/notificaciones/api/read-all/", { method: "POST" });
        await refresh();
      } catch (e) {
        console.error(e);
        alert("No se pudo marcar todo como leído.");
      } finally {
        btnAll.disabled = false;
      }
    });
  }

  refresh().catch((e) => {
    console.error(e);
    alert("No se pudieron cargar tus notificaciones.");
  });
})();
