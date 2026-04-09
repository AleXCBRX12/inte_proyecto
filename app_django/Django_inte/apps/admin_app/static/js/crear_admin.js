/* Función para alternar visibilidad de contraseña en la tabla */
function togglePasswordRow(id, realPassword) {
    const span = document.getElementById(`pwd-${id}`);
    const icon = document.getElementById(`icon-${id}`);
    
    if (span.textContent === "••••••••") {
        span.textContent = realPassword;
        icon.classList.replace('bi-eye', 'bi-eye-slash');
        span.style.background = "#fff"; // Resaltar cuando es visible
    } else {
        span.textContent = "••••••••";
        icon.classList.replace('bi-eye-slash', 'bi-eye');
        span.style.background = "#f1f5f9";
    }
}

/* --- Tus funciones lógicas se mantienen igual --- */
function toggleMenu(btn){
    const menu = btn.nextElementSibling;
    document.querySelectorAll(".menu-acciones").forEach(m => {
        if(m !== menu) m.style.display = "none";
    });
    menu.style.display = menu.style.display === "flex" ? "none" : "flex";
}

document.addEventListener("click", function(e){
    if(!e.target.closest(".acciones")){
        document.querySelectorAll(".menu-acciones").forEach(m => { m.style.display = "none"; });
    }
});

let adminIdActual = null; // Guarda el id del admin seleccionado

/* Abrir y cerrar modales de contraseña */
function abrirModalPassword(id){
    adminIdActual = id;
    document.getElementById("modalPassword").style.display = "flex";
    document.body.classList.add("modal-activo");
    document.getElementById("nuevaPassword").value = "";
}
function cerrarModalPassword(){
    document.getElementById("modalPassword").style.display = "none";
    document.body.classList.remove("modal-activo");
    adminIdActual = null;
}

/* Abrir y cerrar modal de eliminación */
function abrirModalEliminar(id){
    adminIdActual = id;
    document.getElementById("modalEliminar").style.display = "flex";
    document.body.classList.add("modal-activo");
}
function cerrarModalEliminar(){
    document.getElementById("modalEliminar").style.display = "none";
    document.body.classList.remove("modal-activo");
    adminIdActual = null;
}

/* Confirmar cambio de contraseña */
async function confirmarCambioPassword(){
    const nueva = document.getElementById("nuevaPassword").value.trim();
    if(!nueva || nueva.length < 8){
        window.Toast.show("La contraseña debe tener mínimo 8 caracteres", "warning");
        return;
    }
    try {
        const resp = await fetch("{% url 'actualizar_password_admin' 'TEMP' %}".replace("TEMP", adminIdActual), {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
                "X-CSRFToken":"{{ csrf_token }}"
            },
            body: JSON.stringify({password:nueva})
        });
        const data = await resp.json();
        if(data.success){
            cerrarModalPassword();
            location.reload(); // recarga para reflejar el cambio
        }
    } catch(err){
        console.error(err);
        window.Toast.show("Error al actualizar la contraseña", "danger");
    }
}

/* Confirmar eliminación */
async function confirmarEliminar(){
    try {
        const resp = await fetch("{% url 'eliminar_admin' 'TEMP' %}".replace("TEMP", adminIdActual), {
            method:"POST",
            headers:{ "Content-Type":"application/json", "X-CSRFToken":"{{ csrf_token }}" }
        });
        const data = await resp.json();
        if(data.success){
            document.querySelector(`tr[data-id='${adminIdActual}']`).remove();
            cerrarModalEliminar();
        }
    } catch(err){
        console.error(err);
        window.Toast.show("Error al eliminar el administrador", "danger");
    }
}

/* Reemplaza los antiguos onclick de contraseña y eliminar */
function cambiarPasswordAdmin(id){
    abrirModalPassword(id);
}
function eliminarAdmin(id){
    abrirModalEliminar(id);
}

/* Abrir y cerrar modal Crear Admin */
function abrirModal(){
    document.getElementById("modalAdmin").style.display="flex"
    document.body.classList.add("modal-activo")
}
function cerrarModal(){
    document.getElementById("modalAdmin").style.display="none"
    document.body.classList.remove("modal-activo")
}

/* Crear Administrador */
async function crearAdministrador() {
    const nombre = document.querySelector('input[name="nombre"]').value;
    const correo = document.querySelector('input[name="correo"]').value;
    const pwd = document.getElementById("password").value;

    if (!nombre || !correo || !pwd) {
        window.Toast.show("Por favor, rellena todos los campos", "warning");
        return;
    }

    const response = await fetch("{% url 'crear_admin_api' %}", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": "{{ csrf_token }}"
        },
        body: JSON.stringify({ nombre, correo, password: pwd })
    });

    const data = await response.json();
    if (data.status === "success") {
        window.Toast.show("Administrador creado con éxito", "success");
        cerrarModal();
        setTimeout(() => location.reload(), 1000); 
    } else {
        window.Toast.show("Error: " + data.message, "danger");
    }
}

/* Cambiar Estado Activo/Bloqueado */
async function cambiarEstadoAdmin(id, bloquear, btn){
    const url = bloquear ? "{% url 'bloquear_usuario' 'TEMP' %}".replace("TEMP", id) 
                         : "{% url 'desbloquear_usuario' 'TEMP' %}".replace("TEMP", id);
    const resp = await fetch(url, {
        method:"POST",
        headers:{ "Content-Type":"application/json", "X-CSRFToken":"{{ csrf_token }}" }
    });
    const data = await resp.json();
    if(data.success){
        const tr = btn.closest("tr");
        const estadoSpan = tr.querySelector(".estado-col .estado-cuenta");

        if(bloquear){
            estadoSpan.textContent = "Bloqueado";
            estadoSpan.classList.remove("estado-activo");
            estadoSpan.classList.add("estado-bloqueado");

            // Solo mostrar Desbloquear y Eliminar
            const menu = tr.querySelector(".menu-acciones");
            menu.innerHTML = `
                <button class="opcion-desbloquear" onclick="cambiarEstadoAdmin('${id}', false, this)">
                    <i class="bi bi-unlock"></i> Desbloquear
                </button>
                <button class="opcion-eliminar" onclick="eliminarAdmin('${id}')">
                    <i class="bi bi-trash"></i> Eliminar
                </button>
            `;
        } else {
            estadoSpan.textContent = "Activo";
            estadoSpan.classList.remove("estado-bloqueado");
            estadoSpan.classList.add("estado-activo");

            // Restaurar todas las opciones
            const menu = tr.querySelector(".menu-acciones");
            menu.innerHTML = `
                <button class="opcion-bloquear" onclick="cambiarEstadoAdmin('${id}', true, this)">
                    <i class="bi bi-lock"></i> Bloquear
                </button>
                <button class="opcion-password" onclick="cambiarPasswordAdmin('${id}')">
                    <i class="bi bi-key"></i> Cambiar contraseña
                </button>
                <button class="opcion-eliminar" onclick="eliminarAdmin('${id}')">
                    <i class="bi bi-trash"></i> Eliminar
                </button>
            `;
        }
    } else {
        window.Toast.show("No se pudo cambiar el estado", "danger");
    }
}

/* abrir y cerrar menu */
function toggleMenu(btn){
    const menu = btn.nextElementSibling;
    document.querySelectorAll(".menu-acciones").forEach(m=>{
        if(m!==menu) m.style.display="none";
    });
    menu.style.display = menu.style.display==="flex" ? "none" : "flex";
}

/* cerrar si se da click fuera */
document.addEventListener("click", function(e){
    if(!e.target.closest(".acciones")){
        document.querySelectorAll(".menu-acciones").forEach(m=>{ m.style.display="none"; });
    }
});