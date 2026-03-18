from __future__ import annotations

from datetime import datetime, timedelta, timezone

from django.core.management.base import BaseCommand

from config.database.mongo import db


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _norm_doc(name: str) -> str:
    import re

    return re.sub(r"\\s+", " ", (name or "").strip().lower())


class Command(BaseCommand):
    help = "Send scheduled notifications (deadlines/expiration) to entrepreneurs. Run with a cron."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=3, help="Days before close to remind (default: 3)")
        parser.add_argument("--dry-run", action="store_true", help="Do not write notifications; only print counts")

    def handle(self, *args, **options):
        days = int(options.get("days") or 3)
        dry_run = bool(options.get("dry_run"))

        now = _now()
        soon = now + timedelta(days=days)
        expired_cutoff = now - timedelta(days=1)

        from apps.utils.notifications import ensure_notification

        rol_emp = db.roles.find_one({"nombre": {"$regex": "^Emprendedor$", "$options": "i"}})
        rol_emp_id = str(rol_emp["_id"]) if rol_emp else None

        user_query = {"activo": True}
        if rol_emp_id:
            user_query["rol_id"] = rol_emp_id

        users = list(db.usuarios.find(user_query, {"correo": 1}))
        convs = list(db.convocatorias.find())

        self.stdout.write(self.style.SUCCESS(f"users={len(users)} convocatorias={len(convs)} dry_run={dry_run}"))
        if not users or not convs:
            return

        created = 0
        scanned = 0

        for c in convs:
            fecha_fin = c.get("fecha_fin")
            if isinstance(fecha_fin, str):
                try:
                    fecha_fin = datetime.fromisoformat(fecha_fin.replace("Z", "")).replace(tzinfo=timezone.utc)
                except Exception:
                    fecha_fin = None
            if isinstance(fecha_fin, datetime) and fecha_fin.tzinfo is None:
                fecha_fin = fecha_fin.replace(tzinfo=timezone.utc)
            if not isinstance(fecha_fin, datetime):
                continue

            cid = str(c.get("_id"))
            titulo = (c.get("titulo") or "Convocatoria").strip()
            docs_req = c.get("docs_requeridos") or []
            docs_req_norm = [_norm_doc(x) for x in docs_req if isinstance(x, str) and x.strip()]

            # 1) Deadline reminder
            if now <= fecha_fin <= soon:
                dias_restantes = max(0, (fecha_fin - now).days)
                for u in users:
                    scanned += 1
                    uid = str(u.get("_id"))
                    if dry_run:
                        continue
                    nid = ensure_notification(
                        usuario_id=uid,
                        clave=f"conv_deadline_{days}d:{cid}",
                        tipo="warn",
                        titulo=f"Deadline: {titulo}",
                        mensaje=f"Quedan {dias_restantes} dia(s) para el cierre de la convocatoria.",
                        url="/usuarios/ver-convocatorias/",
                        metadata={"convocatoria_id": cid, "fecha_fin": fecha_fin.isoformat()},
                    )
                    created += 1 if nid else 0

                    # 2) Optional critical docs per convocatoria
                    if not docs_req_norm:
                        continue
                    try:
                        correo = (u.get("correo") or "").strip().lower()
                        proyecto = db.proyectos.find_one(
                            {
                                "$or": [
                                    {"usuario_id": uid},
                                    {"usuario_lider_id": uid},
                                    {"correo_usuario": correo},
                                    {"resumen.correo": correo},
                                    {"integrantes.correo": correo},
                                ]
                            },
                            {"_id": 1},
                        )
                        if not proyecto:
                            continue

                        pid = str(proyecto.get("_id"))
                        disponibles = set(
                            db.expediente_documentos.distinct("documento_clave", {"proyecto_id": pid})
                        )
                        missing = [d for d in docs_req_norm if d not in disponibles]
                        if not missing:
                            continue

                        nid2 = ensure_notification(
                            usuario_id=uid,
                            clave=f"conv_missing_docs_{days}d:{cid}:{pid}",
                            tipo="warn",
                            titulo="Documentacion pendiente",
                            mensaje=f"Faltan documento(s) critico(s): {', '.join(missing[:5])}.",
                            url="/usuarios/expediente/",
                            metadata={"convocatoria_id": cid, "proyecto_id": pid, "missing": missing},
                        )
                        created += 1 if nid2 else 0
                    except Exception:
                        continue

            # 3) Expiration notice (only if closed in last 24h)
            if expired_cutoff <= fecha_fin < now:
                for u in users:
                    scanned += 1
                    uid = str(u.get("_id"))
                    if dry_run:
                        continue
                    nid = ensure_notification(
                        usuario_id=uid,
                        clave=f"conv_expired:{cid}",
                        tipo="info",
                        titulo=f"Convocatoria cerrada: {titulo}",
                        mensaje="La convocatoria ya finalizo.",
                        url="/usuarios/ver-convocatorias/",
                        metadata={"convocatoria_id": cid, "fecha_fin": fecha_fin.isoformat()},
                    )
                    created += 1 if nid else 0

        if dry_run:
            return
        self.stdout.write(self.style.SUCCESS(f"created={created} scanned={scanned}"))
