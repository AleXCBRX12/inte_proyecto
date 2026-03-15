
    const tabla = document.getElementById('tablaSolicitudes');
    const solicitudesPorId = new Map();
    let openDropdown = null;
    let solicitudActual = null;
    let todasSolicitudes = [];

    /* ================================
       CARGAR SOLICITUDES
    ================================ */

    document.addEventListener("DOMContentLoaded", function () {
        cargarSolicitudes();
        const filtroEstado = document.getElementById("filtroEstadoSolicitudes");
        const filtroTexto = document.getElementById("filtroTextoSolicitudes");
        if(filtroEstado) filtroEstado.addEventListener("change", renderSolicitudes);
        if(filtroTexto) filtroTexto.addEventListener("input", renderSolicitudes);
    });

    function cargarSolicitudes() {
        tabla.innerHTML = "<tr><td colspan='5'><div class='skeleton-table'><div class='skeleton-row'></div><div class='skeleton-row'></div><div class='skeleton-row'></div></div></td></tr>";
        fetch("/admin/obtener_solicitudes/")
            .then(response => response.json())
            .then(data => {
                todasSolicitudes = data || [];
                solicitudesPorId.clear();
                todasSolicitudes.forEach(s => solicitudesPorId.set(String(s._id || `${Date.now()}-${Math.random()}`), s));
                renderSolicitudes();
            })
            .catch(error => {
                console.error("Error cargando solicitudes:", error);
                tabla.innerHTML = "<tr><td colspan='5'>No se pudieron cargar las solicitudes</td></tr>";
                Toast?.show?.("No se pudieron cargar solicitudes", "warn");
            });
    }

    function renderSolicitudes(){
        tabla.innerHTML = "";
        const estadoSel = (document.getElementById("filtroEstadoSolicitudes")?.value || "todos").toLowerCase();
        const texto = (document.getElementById("filtroTextoSolicitudes")?.value || "").toLowerCase().trim();

        const filtradas = todasSolicitudes.filter(s => {
            const est = (s.estado || "EN PROCESO").toLowerCase();
            const matchEstado = estadoSel === "todos" || est.includes(estadoSel.toLowerCase());
            const matchTexto = !texto || (s.nombre_completo || "").toLowerCase().includes(texto) || (s.nombre_proyecto || "").toLowerCase().includes(texto);
            return matchEstado && matchTexto;
        });

        filtradas.forEach(s => agregarFila(s));
    }

    function agregarFila(s) {
    const estado = s.estado || "Pendiente";
    
    
    let claseColor = "estado-proceso"; 
    const estLower = estado.toLowerCase();
    
    if (estLower.includes("acept")) claseColor = "estado-aceptado";
    else if (estLower.includes("rechaz")) claseColor = "estado-rechazado";


    const fila = document.createElement('tr');
    
   
    const solicitudId = s._id || `${Date.now()}-${Math.random()}`;
    solicitudesPorId.set(String(solicitudId), s);

   
    fila.innerHTML = `
    <td data-label="Nombre">${s.nombre_completo || ''}</td>
    <td data-label="Proyecto">${s.nombre_proyecto || ''}</td>
    <td data-label="Fecha">${s.fecha_creacion || ''}</td>
    <td data-label="Estado"><span class="status ${claseColor}">${estado}</span></td>
    
    <td class="acciones">
        <button class="btn-ver-solicitud" data-solicitud-id="${solicitudId}">
            <i class="bi bi-eye"></i> Ver
        </button>
    </td>
`;

    const btnVer = fila.querySelector(".btn-ver-solicitud");
    btnVer.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        const id = this.dataset.solicitudId;
        const solicitud = solicitudesPorId.get(String(id));
        if (solicitud) {
            abrirModalDetalleCompleto(solicitud);
        }
    });

    
    tabla.appendChild(fila);
}
    /* ================================
       MODAL DETALLE COMPLETO
    ================================ */

    function abrirModalDetalleCompleto(s) {

        solicitudActual = s._id;

        // INFORMACIÓN PERSONAL
        document.getElementById("modalNombre").textContent = s.nombre_completo || '';
        document.getElementById("modalCorreo").textContent = s.correo || '';
        document.getElementById("modalEdad").textContent = s.edad || '';
        document.getElementById("modalCarrera").textContent = s.carrera || '';
        document.getElementById("modalNivel").textContent = s.nivel || '';
        document.getElementById("modalMatricula").textContent = s.matricula || '';
        document.getElementById("modalAsesor").textContent = s.asesor_academico || '';
        document.getElementById("modalTutor").textContent = s.tutor || '';
        document.getElementById("modalTelefono").textContent = s.telefono || '';
        document.getElementById("modalDireccion").textContent = s.direccion || '';
        document.getElementById("modalIntegrantes").textContent = s.integrantes_equipo || '';

        // INFORMACIÓN PROYECTO
        document.getElementById("modalProyecto").textContent = s.nombre_proyecto || '';
        document.getElementById("modalDescripcion").textContent = s.descripcion_negocio || '';
        document.getElementById("modalUbicacion").textContent = s.ubicacion_emprendimiento || '';
        document.getElementById("modalInicio").textContent = s.inicio_emprendimiento || '';
        document.getElementById("modalClientes").textContent = s.clientes_clave || '';
        document.getElementById("modalProblema").textContent = s.problema_resuelve || '';
        document.getElementById("modalProducto").textContent = s.producto_servicio || '';
        document.getElementById("modalInnovacion").textContent = s.innovacion || '';
        document.getElementById("modalValor").textContent = s.valor_cliente || '';
        document.getElementById("modalIdea").textContent = s.idea_7_palabras || '';
        document.getElementById("modalSat").textContent = s.alta_sat || '';
        document.getElementById("modalPersonasTrabajan").textContent = s.personas_trabajan || '';
        document.getElementById("modalMiembrosIncubacion").textContent = s.miembros_incubacion || '';
        document.getElementById("modalProgramasPrevios").textContent = s.programas_previos || '';

        // LÍDER
        document.getElementById("modalDescripcionLider").textContent = s.descripcion_lider || '';
        document.getElementById("modalRol").textContent = s.rol_lider || '';
        document.getElementById("modalHabilidades").textContent = s.habilidades || '';
        document.getElementById("modalLogro").textContent = s.logro_asombroso || '';

        // ESTADO Y FECHA
        const estado = s.estado || "Pendiente";
        const estadoEl = document.getElementById("modalEstado");

        estadoEl.textContent = estado;
        document.getElementById("modalFecha").textContent = s.fecha_creacion || '';

        estadoEl.classList.remove("estado-aceptado", "estado-rechazado", "estado-proceso");

        if (estado.toLowerCase().includes("acept")) {
            estadoEl.classList.add("estado-aceptado");
        }
        else if (estado.toLowerCase().includes("rechaz")) {
            estadoEl.classList.add("estado-rechazado");
        }
        else {
            estadoEl.classList.add("estado-proceso");
        }

        // INTEGRANTES DEL EQUIPO (DINÁMICOS)
        const seccionIntegrantes = document.getElementById("seccionIntegrantes");
        const bodyIntegrantes = document.getElementById("modalIntegrantesBody");
        
        if (s.integrantes && s.integrantes.length > 0) {
            seccionIntegrantes.style.display = "block";
            bodyIntegrantes.innerHTML = s.integrantes.map(m => `
                <tr>
                    <td>${m.nombre || '-'}</td>
                    <td>${m.matricula || '-'}</td>
                    <td>${m.correo || '-'}</td>
                    <td>${m.telefono || '-'}</td>
                    <td>${m.carrera || '-'}</td>
                    <td>${m.nivel || '-'}</td>
                    <td>${m.cuatri || '-'}</td>
                </tr>
            `).join('');
        } else {
            seccionIntegrantes.style.display = "none";
            bodyIntegrantes.innerHTML = "";
        }

        mostrarModal('modalDetalle');
    }

    /* ================================
       ACTUALIZAR ESTADO
    ================================ */

    function actualizarEstado(id, nuevoEstado, password = null, motivo = null) {
        const payload = { estado: nuevoEstado };
        if (password) payload.password = password;
        if (motivo) payload.motivo = motivo;

        fetch(`/admin/actualizar_estado/${id}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify(payload)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    cerrarModal('modalDetalle');
                    cerrarModal('modalAceptar');
                    cerrarModal('modalRechazar');
                    cerrarModal('modalCredenciales');
                    document.getElementById("nuevaPassword").value = "";
                    document.getElementById("errorPassword").textContent = "";
                    cargarSolicitudes();
                    if (!data.mail_enviado) {
                        alert("Estado actualizado, pero no se pudo enviar el correo.");
                    }
                } else if (data.error) {
                    alert(data.error);
                }
            })
            .catch(() => {
                alert("Error al actualizar la solicitud.");
            });
    }

    /* ================================
       ACEPTAR / RECHAZAR
    ================================ */
    function aceptarDesdeDetalle() {
        cerrarModal('modalDetalle');

        setTimeout(() => {
            mostrarModal('modalCredenciales');
        }, 150);
    }

    function rechazarDesdeDetalle() {
        cerrarModal('modalDetalle');
        setTimeout(() => {
            mostrarModal('modalRechazar');
            document.getElementById("motivoRechazo").value = "";
            document.getElementById("errorMotivo").style.display = "none";
        }, 150);
    }

    function confirmarRechazo() {
        const motivoEl = document.getElementById("motivoRechazo");
        const errorEl = document.getElementById("errorMotivo");
        const motivo = (motivoEl.value || "").trim();

        if (!motivo) {
            errorEl.style.display = "block";
            motivoEl.classList.add("input-error");
            return;
        }

        motivoEl.classList.remove("input-error");
        errorEl.style.display = "none";
        actualizarEstado(solicitudActual, "Rechazado", null, motivo);
    }

    function generarPassword() {
        const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789@#$%&*!?";
        let pass = "";
        for (let i = 0; i < 12; i++) {
            pass += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        document.getElementById("nuevaPassword").value = pass;
        document.getElementById("errorPassword").textContent = "";
    }

    function guardarCredenciales() {
        const inputPassword = document.getElementById("nuevaPassword");
        const errorPassword = document.getElementById("errorPassword");
        const password = (inputPassword.value || "").trim();

        if (password.length < 8) {
            errorPassword.textContent = "La contraseña debe tener al menos 8 caracteres.";
            inputPassword.classList.add("input-error");
            return;
        }

        inputPassword.classList.remove("input-error");
        errorPassword.textContent = "";
        actualizarEstado(solicitudActual, "Aceptado", password);
    }

    document.addEventListener("DOMContentLoaded", function () {

        const btnConfirmar = document.getElementById('btnConfirmarRechazar');

        if (btnConfirmar) {
            btnConfirmar.addEventListener("click", function () {
                actualizarEstado(solicitudActual, "Rechazado");
                cerrarModal('modalRechazar');
            });
        }

    });

    /* ================================
       DROPDOWN
    ================================ */

    function toggleDropdown(btn) {
        const dropdown = btn.nextElementSibling;

        if (openDropdown && openDropdown !== dropdown) {
            openDropdown.classList.remove('show-dropdown');
        }

        dropdown.classList.toggle('show-dropdown');
        openDropdown = dropdown.classList.contains('show-dropdown') ? dropdown : null;
    }

    document.addEventListener('click', function (e) {
        if (openDropdown && !e.target.closest('.acciones')) {
            openDropdown.classList.remove('show-dropdown');
            openDropdown = null;
        }
    });

    function cerrarDropdownAbierto() {
        if (openDropdown) {
            openDropdown.classList.remove('show-dropdown');
            openDropdown = null;
        }
    }

    /* ================================
       CONTROL MODALES
    ================================ */

    function mostrarModal(id) {
        document.body.classList.add('modal-open');
        document.getElementById(id).style.display = 'flex';
    }

    function cerrarModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.style.display = 'none';
        }

        const hayModalAbierto = Array.from(document.querySelectorAll('.solicitud-modal'))
            .some(m => m.style.display === 'flex');

        if (!hayModalAbierto) {
            document.body.classList.remove('modal-open');
        }
    }

    /* ================================
       CSRF TOKEN
    ================================ */

    function getCSRFToken() {
        const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenInput ? tokenInput.value : '';
    }
