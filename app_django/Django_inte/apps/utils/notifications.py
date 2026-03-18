from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId

from config.database.mongo import db


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Notification:
    id: str
    tipo: str
    titulo: str
    mensaje: str
    url: Optional[str]
    created_at: Optional[str]
    read: bool


def create_notification(
    *,
    usuario_id: str,
    tipo: str,
    titulo: str,
    mensaje: str,
    url: Optional[str] = None,
    clave: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    send_email: bool = False,
    email_to: Optional[str] = None,
) -> Optional[str]:
    if not usuario_id:
        return None

    doc: Dict[str, Any] = {
        "usuario_id": str(usuario_id),
        "tipo": (tipo or "info").strip() or "info",
        "titulo": (titulo or "").strip() or "Notificación",
        "mensaje": (mensaje or "").strip(),
        "url": (url or "").strip() or None,
        "clave": (clave or "").strip() or None,
        "metadata": metadata or {},
        "created_at": _now(),
        "read_at": None,
    }

    res = db.notificaciones.insert_one(doc)
    notif_id = str(res.inserted_id)

    if send_email and email_to:
        try:
            from django.conf import settings
            from apps.utils.mailer import send_email as _send_email

            subject = f"[INTE] {doc['titulo']}"
            text_body = doc["mensaje"] or doc["titulo"]
            _send_email(
                subject=subject,
                text_body=text_body,
                html_body=None,
                to=[email_to],
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            )
        except Exception:
            # Nunca romper el flujo por un fallo de correo
            pass

    return notif_id


def ensure_notification(
    *,
    usuario_id: str,
    clave: str,
    tipo: str,
    titulo: str,
    mensaje: str,
    url: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    if not usuario_id or not clave:
        return None

    exists = db.notificaciones.find_one({"usuario_id": str(usuario_id), "clave": str(clave)})
    if exists:
        return None

    return create_notification(
        usuario_id=str(usuario_id),
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        url=url,
        clave=clave,
        metadata=metadata,
    )


def unread_count(usuario_id: str) -> int:
    if not usuario_id:
        return 0
    return int(db.notificaciones.count_documents({"usuario_id": str(usuario_id), "read_at": None}))


def list_notifications(usuario_id: str, *, limit: int = 30) -> List[Notification]:
    if not usuario_id:
        return []

    cursor = db.notificaciones.find({"usuario_id": str(usuario_id)}).sort("created_at", -1).limit(int(limit or 30))
    items: List[Notification] = []
    for n in cursor:
        created_at = n.get("created_at")
        created_str = None
        if isinstance(created_at, datetime):
            try:
                created_str = created_at.astimezone(timezone.utc).strftime("%d/%m/%Y %H:%M")
            except Exception:
                created_str = created_at.strftime("%d/%m/%Y %H:%M")

        items.append(
            Notification(
                id=str(n.get("_id")),
                tipo=n.get("tipo") or "info",
                titulo=n.get("titulo") or "Notificación",
                mensaje=n.get("mensaje") or "",
                url=n.get("url") or None,
                created_at=created_str,
                read=bool(n.get("read_at")),
            )
        )
    return items


def mark_read(usuario_id: str, notif_id: str) -> bool:
    if not usuario_id or not notif_id:
        return False
    try:
        oid = ObjectId(str(notif_id))
    except Exception:
        return False

    res = db.notificaciones.update_one(
        {"_id": oid, "usuario_id": str(usuario_id), "read_at": None},
        {"$set": {"read_at": _now()}},
    )
    return bool(res.modified_count)


def mark_all_read(usuario_id: str) -> int:
    if not usuario_id:
        return 0
    res = db.notificaciones.update_many(
        {"usuario_id": str(usuario_id), "read_at": None},
        {"$set": {"read_at": _now()}},
    )
    return int(res.modified_count or 0)
