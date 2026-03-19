import os
from django.shortcuts import render, redirect
from datetime import datetime, timezone, timedelta
from bson.objectid import ObjectId
import uuid
import uuid
from apps.utils import email_service

from config.database.mongo import mongo_instance, db
from apps.utils.access_logic import check_team_contract_accepted


def _obtener_muro_unificado_public(request=None, es_visitante=False, solo_convocatorias=False, dividido=False):
    muro_convocatorias = []
    muro_anuncios = []
    ahora = datetime.now(timezone.utc)

    usuario_logueado = request.session.get("usuario_id") if (request and hasattr(request, 'session')) else None
    
    # Mostrar si es visitante explícito, o si no hay usuario logueado.
    # Si hay usuario logueado (Emprendedor), desaparece.
    # Excepción: Admin Panel (cuando request es None o viene de admin)
    es_admin_path = request.path.startswith('/admin') if (request and hasattr(request, 'path')) else True
    
    mostrar_convocatorias = es_visitante or not usuario_logueado or es_admin_path
    if mostrar_convocatorias:
        datos_conv = list(db.convocatorias.find().sort("_id", -1))
        for c in datos_conv:
            fecha_raw = c.get("fecha_fin")
            fecha_fin = None
            if fecha_raw:
                try:
                    if isinstance(fecha_raw, datetime):
                        fecha_fin = fecha_raw.replace(tzinfo=timezone.utc) if fecha_raw.tzinfo is None else fecha_raw.astimezone(timezone.utc)
                    elif isinstance(fecha_raw, str):
                        fecha_limpia = fecha_raw.replace('Z', '')
                        fecha_fin = datetime.fromisoformat(fecha_limpia).replace(tzinfo=timezone.utc)
                except Exception:
                    fecha_fin = None

            dias_restantes = (fecha_fin - ahora).days if fecha_fin else -1
            puede_postular = (fecha_fin > ahora) if fecha_fin else False
            
            estado_label = "Sin fecha"
            if fecha_fin:
                if dias_restantes >= 15: estado_label = "Nueva"
                elif 7 <= dias_restantes < 15: estado_label = "En proceso"
                elif 0 <= dias_restantes < 7: estado_label = "Casi termina"
                else: 
                    estado_label = "Cerrada"
                    puede_postular = False

            banner_base64 = None
            if c.get("banner_file_id"):
                try:
                    banner_base64 = mongo_instance.obtener_imagen_base64(c["banner_file_id"])
                except Exception:
                    banner_base64 = None

            muro_convocatorias.append({
                "id": str(c["_id"]),
                "tipo": "convocatoria",
                "titulo": c.get("titulo", "Sin título"),
                "contenido": c.get("descripcion", ""),
                "banner": banner_base64,
                "estado": estado_label,
                "puede_postular": puede_postular,
                "fecha": c.get("_id").generation_time.strftime("%d %b, %H:%M") if hasattr(c.get("_id"), "generation_time") else "Reciente",
                "fecha_sort": c.get("_id").generation_time if hasattr(c.get("_id"), "generation_time") else ahora
            })
    else:
        muro_convocatorias = []

    # 2. Obtener Anuncios
    if not solo_convocatorias:
        datos_anuncios = list(db.anuncios.find().sort("_id", -1))
        for a in datos_anuncios:
            # Si es visitante, filtrar los que son solo para emprendedores
            if es_visitante and a.get("solo_emprendedores", False):
                continue
            
            fecha_a = a.get("fecha")
            if isinstance(fecha_a, datetime):
                fecha_fmt = fecha_a.strftime("%d %b, %H:%M")
            else:
                fecha_fmt = str(fecha_a) if fecha_a else "Reciente"

            muro_anuncios.append({
                "id": str(a["_id"]),
                "tipo": "anuncio",
                "titulo": a.get("titulo", "Anuncio"),
                "contenido": a.get("contenido", ""),
                "fecha": fecha_fmt,
                "banner": a.get("banner"),
                "solo_emprendedores": a.get("solo_emprendedores", False),
                "fecha_sort": a.get("_id").generation_time if hasattr(a.get("_id"), "generation_time") else ahora
            })

        # 3. Obtener Publicaciones (colección separada)
        datos_publicaciones = list(db.publicaciones.find().sort("_id", -1))
        for p in datos_publicaciones:
            if es_visitante and p.get("solo_emprendedores", False):
                continue

            fecha_p = p.get("fecha_creacion") or p.get("fecha")
            if isinstance(fecha_p, datetime):
                fecha_fmt = fecha_p.strftime("%d %b, %H:%M")
            else:
                fecha_fmt = str(fecha_p) if fecha_p else "Reciente"

            fecha_sort_val = ahora
            if isinstance(fecha_p, datetime):
                fecha_sort_val = fecha_p.replace(tzinfo=timezone.utc) if fecha_p.tzinfo is None else fecha_p
            elif hasattr(p.get("_id"), "generation_time"):
                fecha_sort_val = p["_id"].generation_time

            muro_anuncios.append({
                "id": str(p["_id"]),
                "tipo": "anuncio",
                "titulo": p.get("titulo", "Publicación"),
                "contenido": p.get("contenido", ""),
                "fecha": fecha_fmt,
                "banner": p.get("banner"),
                "solo_emprendedores": p.get("solo_emprendedores", False),
                "fecha_sort": fecha_sort_val
            })

    # Ordenar por fecha_sort descendente
    muro_convocatorias.sort(key=lambda x: x["fecha_sort"], reverse=True)
    muro_anuncios.sort(key=lambda x: x["fecha_sort"], reverse=True)

    if solo_convocatorias:
        return muro_convocatorias
        
    if dividido:
        return {
            "convocatorias": muro_convocatorias,
            "anuncios": muro_anuncios
        }

    muro_unificado = muro_convocatorias + muro_anuncios
    muro_unificado.sort(key=lambda x: x["fecha_sort"], reverse=True)
    return muro_unificado


def _emprendedor_tiene_contrato_aceptado(usuario_id):
    return check_team_contract_accepted(usuario_id)


def _bloquear_emprendedor_sin_contrato(request):
    # Relajamos el bloqueo: si ya inició sesión no forzamos regresar a documentación.
    return None




def login_view(request):
    login_mensaje = None
    if request.method != "POST":
        login_mensaje = request.session.pop("login_mensaje", None)

    if request.method == "POST":
        correo = request.POST.get("email")
        contrasena = request.POST.get("password")

        usuario = db.usuarios.find_one({
            "correo": (correo or "").strip(),
            "contrasena": (contrasena or "").strip(),
            "activo": True
        })
        if not usuario:
            return render(request, "login.html", {"error": "Correo o contraseña incorrectos"})

        rol = db.roles.find_one({"_id": ObjectId(usuario["rol_id"])})
        if not rol:
            return render(request, "login.html", {"error": "Rol no encontrado"})

        request.session["usuario_id"] = str(usuario["_id"])
        request.session["nombre"] = (usuario.get("nombre") or "").strip()
        request.session["apellido_paterno"] = (usuario.get("apellido_paterno") or "").strip()
        request.session["apellido_materno"] = (usuario.get("apellido_materno") or "").strip()
        request.session["correo"] = (usuario.get("correo") or "").strip()
        request.session["rol"] = (rol.get("nombre") or "").strip()

        nombre_rol = (rol.get("nombre") or "").strip()
        if nombre_rol == "Administrador":
            return redirect("panel_admin")
        if nombre_rol == "Emprendedor":
            if _emprendedor_tiene_contrato_aceptado(str(usuario["_id"])):
                return redirect("portal_publico")
            return redirect("documentacion")

        return render(request, "login.html", {"error": "Rol no autorizado"})

    ctx = {}
    if login_mensaje:
        ctx["mensaje"] = login_mensaje
    return render(request, "login.html", ctx)


def solicitar_reset(request):
    mensaje = None
    error = None
    if request.method == "POST":
        correo = (request.POST.get("email") or "").strip()
        usuario = db.usuarios.find_one({"correo": correo, "activo": True})
        if not usuario:
            error = "No encontramos un usuario activo con ese correo."
        else:
            token = str(uuid.uuid4())
            db.password_resets.insert_one({
                "usuario_id": str(usuario["_id"]),
                "token": token,
                "expira": datetime.now(timezone.utc) + timedelta(hours=1),
                "usado": False
            })
            enviado = email_service.enviar_correo_reset(correo, token, request)
            mensaje = "Te enviamos un enlace a tu correo." if enviado else "No pudimos enviar el correo, intenta mas tarde."
    return render(request, "reset_request.html", {"mensaje": mensaje, "error": error})


def reset_password(request, token):
    registro = db.password_resets.find_one({"token": token})
    ahora = datetime.now(timezone.utc)
    
    expira = registro.get("expira") if registro else None
    if expira and expira.tzinfo is None:
        expira = expira.replace(tzinfo=timezone.utc)
        
    token_valido = bool(registro and not registro.get("usado") and expira and expira > ahora)
    error = None
    mensaje = None

    if request.method == "POST" and token_valido:
        pwd1 = (request.POST.get("password") or "").strip()
        pwd2 = (request.POST.get("password2") or "").strip()
        if pwd1 != pwd2:
            error = "Las contraseñas no coinciden."
        elif len(pwd1) < 8:
            error = "Minimo 8 caracteres."
        else:
            db.usuarios.update_one(
                {"_id": ObjectId(registro["usuario_id"])},
                {"$set": {"contrasena": pwd1}}
            )
            db.password_resets.update_one({"_id": registro["_id"]}, {"$set": {"usado": True}})
            
            # Enviar correo de confirmación
            usuario = db.usuarios.find_one({"_id": ObjectId(registro["usuario_id"])})
            if usuario:
                email_service.enviar_confirmacion_password(usuario.get("correo"), usuario.get("nombre"), request)

            mensaje = "Contraseña actualizada. Ya puedes iniciar sesión."
            request.session["login_mensaje"] = mensaje
            token_valido = False

    if not token_valido and not mensaje and not error:
        error = "El enlace no es válido o ya expiró."

    return render(request, "reset_password.html", {"token_valido": token_valido, "error": error, "mensaje": mensaje})


def ver_convocatorias(request):
    bloqueo = _bloquear_emprendedor_sin_contrato(request)
    if bloqueo:
        return bloqueo
    return render(request, "ver_convocatorias.html", {"muro": _obtener_muro_unificado_public()})


def portal_publico(request):
    bloqueo = _bloquear_emprendedor_sin_contrato(request)
    if bloqueo:
        return bloqueo
    return render(request, "portal_publico.html", {"muro": _obtener_muro_unificado_public()})


def portal_visitante(request):
    # Visitantes VEN ÚNICAMENTE convocatorias (según petición del usuario)
    return render(request, "portal_visitante.html", {"muro": _obtener_muro_unificado_public(es_visitante=True, solo_convocatorias=True)})


def aviso_privacidad(request):
    return render(request, "aviso_privacidad.html")

def portal_contacto(request):
    return render(request, 'contacto.html')

def portal_desarrolladores(request):
    return render(request, 'desarrolladores.html')
