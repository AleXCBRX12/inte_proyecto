import os
from django.shortcuts import render, redirect
from datetime import datetime, timezone, timedelta
from bson.objectid import ObjectId
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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


def _enviar_correo_reset(destinatario, token, request):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("EMAIL_HOST_USER")
    sender_password = os.getenv("EMAIL_HOST_PASSWORD")
    if not sender_email or not sender_password or not destinatario:
        return False

    link = request.build_absolute_uri(f"/login/reset/{token}/")
    mensaje = MIMEMultipart("alternative")
    mensaje["From"] = sender_email
    mensaje["To"] = destinatario
    mensaje["Subject"] = "Recuperación de contraseña - Incubadora de Empresas"

    html = f"""
    <html>
    <body style="margin:0; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; background-color: #f8fafc; color: #1e293b;">
        <div style="max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);">
            <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 40px 20px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Restablecer Contraseña</h1>
            </div>
            <div style="padding: 40px 30px;">
                <p style="font-size: 18px; margin-top: 0;">Hola,</p>
                <p style="line-height: 1.6; font-size: 16px;">Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en la <strong>Incubadora de Empresas</strong>.</p>
                
                <p style="line-height: 1.6; font-size: 16px;">Para continuar con el proceso, por favor haz clic en el siguiente botón:</p>

                <div style="text-align: center; margin: 35px 0;">
                    <a href="{link}" style="display: inline-block; background-color: #1f3c88; color: #ffffff; padding: 14px 28px; border-radius: 10px; text-decoration: none; font-weight: 700; font-size: 16px; box-shadow: 0 4px 6px -1px rgba(31, 60, 136, 0.3);">Restablecer mi contraseña</a>
                </div>

                <p style="line-height: 1.6; font-size: 16px; color: #64748b;">Si tú no solicitaste este cambio, puedes ignorar este correo de forma segura. Tu contraseña actual no cambiará.</p>
                
                <p style="margin-top: 40px; font-size: 14px; text-align: center; color: #94a3b8; border-top: 1px solid #f1f5f9; padding-top: 20px;">Este enlace expirará en 24 horas por motivos de seguridad.</p>
            </div>
            <div style="background-color: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="margin: 0; font-size: 12px; color: #94a3b8;">&copy; 2026 Incubadora de Empresas. Todos los derechos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """
    mensaje.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(mensaje)
        server.quit()
        return True
    except Exception:
        return False


def _enviar_correo_confirmacion(destinatario, nombre, request):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("EMAIL_HOST_USER")
    sender_password = os.getenv("EMAIL_HOST_PASSWORD")
    if not sender_email or not sender_password or not destinatario:
        return False

    mensaje = MIMEMultipart("alternative")
    mensaje["From"] = sender_email
    mensaje["To"] = destinatario
    mensaje["Subject"] = "Contraseña actualizada con éxito - Incubadora de Empresas"

    html = f"""
    <html>
    <body style="margin:0; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; background-color: #f8fafc; color: #1e293b;">
        <div style="max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);">
            <div style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); padding: 40px 20px; text-align: center;">
                <div style="background: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px;">
                    <span style="color: #10b981; font-size: 30px; font-weight: bold;">✓</span>
                </div>
                <h1 style="color: #ffffff; margin: 0; font-size: 24px;">¡Todo listo, {nombre}!</h1>
            </div>
            <div style="padding: 40px 30px;">
                <p style="font-size: 18px; margin-top: 0;">Tu contraseña ha sido actualizada.</p>
                <p style="line-height: 1.6; font-size: 16px;">Te confirmamos que el cambio de contraseña para tu cuenta en la <strong>Incubadora de Empresas</strong> se ha realizado correctamente.</p>
                
                <p style="line-height: 1.6; font-size: 16px;">Ya puedes volver a iniciar sesión de forma segura.</p>

                <div style="text-align: center; margin: 35px 0;">
                    <a href="{request.build_absolute_uri('/login/')}" style="display: inline-block; background-color: #1f3c88; color: #ffffff; padding: 14px 28px; border-radius: 10px; text-decoration: none; font-weight: 700; font-size: 16px;">Ir al Login</a>
                </div>

                <p style="line-height: 1.6; font-size: 14px; color: #64748b; border-top: 1px solid #f1f5f9; padding-top: 20px;">Si no realizaste este cambio, por favor contacta de inmediato con soporte técnico.</p>
            </div>
            <div style="background-color: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="margin: 0; font-size: 12px; color: #94a3b8;">&copy; 2026 Incubadora de Empresas. Todos los derechos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """
    mensaje.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(mensaje)
        server.quit()
        return True
    except Exception:
        return False


def login_view(request):
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

    return render(request, "login.html")


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
            enviado = _enviar_correo_reset(correo, token, request)
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
                _enviar_correo_confirmacion(usuario.get("correo"), usuario.get("nombre"), request)

            mensaje = "Contraseña actualizada. Ya puedes iniciar sesión."
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
