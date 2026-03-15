from bson.objectid import ObjectId
from config.database.mongo import db

def check_team_contract_accepted(usuario_id):
    """
    Verifica si el contrato del equipo al que pertenece el usuario ha sido aceptado.
    """
    try:
        usuario_id_str = str(usuario_id)
        usuario_obj = db.usuarios.find_one({"_id": ObjectId(usuario_id_str)})
        if not usuario_obj:
            return False
            
        correo_usuario = (usuario_obj.get("correo") or "").strip().lower()

        # 1. Buscar proyecto donde sea líder o integrante
        proyecto = db.proyectos.find_one({
            "$or": [
                {"usuario_id": usuario_id_str},
                {"usuario_lider_id": usuario_id_str},
                {"resumen.correo": correo_usuario},
                {"integrantes.correo": correo_usuario}
            ]
        })

        if not proyecto:
            # Si no hay proyecto, verificar contrato individual (fallback para solicitantes solitarios)
            return _check_contrato_individual_base(usuario_id_str)

        # 2. El acceso depende del LÍDER del proyecto
        lider_id = proyecto.get("usuario_lider_id") or proyecto.get("usuario_id")
        if not lider_id:
            # Si por algún motivo no hay ID de líder pero hay correo, intentar buscar por correo del resumen
            lider_correo = proyecto.get("resumen", {}).get("correo")
            if lider_correo:
                lider_user = db.usuarios.find_one({"correo": lider_correo.strip().lower()})
                if lider_user:
                    lider_id = str(lider_user["_id"])
            
        if not lider_id:
            return _check_contrato_individual_base(usuario_id_str)

        return _check_contrato_individual_base(lider_id)
    except Exception as e:
        print(f"Error en check_team_contract_accepted: {e}")
        return False

def get_team_contract_status(usuario_id):
    """
    Obtiene el estado del contrato del equipo (Sin enviar, En revision, Aceptado, Rechazado).
    """
    try:
        usuario_id_str = str(usuario_id)
        usuario_obj = db.usuarios.find_one({"_id": ObjectId(usuario_id_str)})
        if not usuario_obj:
            return "Sin enviar", None
            
        correo_usuario = (usuario_obj.get("correo") or "").strip().lower()

        proyecto = db.proyectos.find_one({
            "$or": [
                {"usuario_id": usuario_id_str},
                {"usuario_lider_id": usuario_id_str},
                {"resumen.correo": correo_usuario},
                {"integrantes.correo": correo_usuario}
            ]
        })

        lider_id = usuario_id_str
        if proyecto:
            lider_id = proyecto.get("usuario_lider_id") or proyecto.get("usuario_id") or usuario_id_str

        # Obtener contrato vigente
        contrato_vigente = db.contrato_vigente.find_one(sort=[("fecha_actualizacion", -1), ("_id", -1)])
        vigente_id = str(contrato_vigente["_id"]) if contrato_vigente else None

        filtro = {"usuario_id": str(lider_id)}
        if vigente_id:
            filtro["contrato_vigente_id"] = vigente_id

        ultimo = db.contrato_proyecto.find_one(filtro, sort=[("fecha_subida", -1), ("_id", -1)])
        
        if not ultimo:
            return "Sin enviar", None

        estado = (ultimo.get("estado") or "enviado").lower()
        if estado == "aceptado": return "Aceptado", ultimo
        if estado == "rechazado": return "Rechazado", ultimo
        return "En revision", ultimo
        
    except Exception as e:
        print(f"Error en get_team_contract_status: {e}")
        return "Error", None

def _check_contrato_individual_base(uid):
    """Lógica base para verificar si un usuario específico tiene un contrato aceptado."""
    uid_str = str(uid)
    
    # Verificar contrato del periodo vigente
    contrato_vigente = db.contrato_vigente.find_one(sort=[("fecha_actualizacion", -1), ("_id", -1)])
    vigente_id = str(contrato_vigente["_id"]) if contrato_vigente else None

    filtro = {"usuario_id": uid_str}
    if vigente_id:
        filtro["contrato_vigente_id"] = vigente_id

    # Primero el más reciente del periodo actual
    ultimo = db.contrato_proyecto.find_one(filtro, sort=[("fecha_subida", -1), ("_id", -1)])
    if ultimo and (ultimo.get("estado") or "").lower() == "aceptado":
        return True

    # Como fallback, buscar cualquier contrato aceptado históricamente
    ultimo_aceptado = db.contrato_proyecto.find_one(
        {"usuario_id": uid_str, "estado": {"$regex": "^aceptado$", "$options": "i"}},
        sort=[("fecha_subida", -1), ("_id", -1)]
    )
    return bool(ultimo_aceptado)
