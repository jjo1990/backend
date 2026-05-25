from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from datetime import datetime

from db.database import get_session
from models.models import Usuario, Rol, UsuarioRol
from schemas.schemas import UserResponse
from dependencies import get_current_user, require_role, CurrentUser
from models.models import Usuario as UsuarioModel

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])
SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/usuarios", response_model=List[UserResponse])
def listar_usuarios(
    session: SessionDep,
    current_user: UsuarioModel = Depends(require_role(["ADMIN"])),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    rol: str | None = Query(None),
):
    query = select(Usuario).where(Usuario.deleted_at == None)
    if rol:
        query = query.join(UsuarioRol).join(Rol).where(Rol.codigo == rol)
    usuarios = session.exec(query.offset(offset).limit(limit)).all()

    result = []
    for u in usuarios:
        roles = [ur.rol.codigo for ur in u.roles]
        result.append(UserResponse(
            id=u.id, email=u.email, nombre=u.nombre,
            apellido=u.apellido, telefono=u.telefono,
            activo=u.activo, roles=roles,
        ))
    return result


@router.patch("/usuarios/{usuario_id}/roles", response_model=UserResponse)
def asignar_roles(
    usuario_id: int,
    roles_data: dict,
    session: SessionDep,
    current_user: UsuarioModel = Depends(require_role(["ADMIN"])),
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario or usuario.deleted_at:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    viejos = session.exec(select(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)).all()
    for v in viejos:
        session.delete(v)

    for codigo in roles_data.get("roles", []):
        rol = session.exec(select(Rol).where(Rol.codigo == codigo)).first()
        if rol:
            session.add(UsuarioRol(usuario_id=usuario_id, rol_id=rol.id))

    session.commit()
    session.refresh(usuario)

    roles = [ur.rol.codigo for ur in usuario.roles]
    return UserResponse(
        id=usuario.id, email=usuario.email, nombre=usuario.nombre,
        apellido=usuario.apellido, telefono=usuario.telefono,
        activo=usuario.activo, roles=roles,
    )


@router.patch("/usuarios/{usuario_id}/deactivate")
def deactivate_user(
    usuario_id: int,
    session: SessionDep,
    current_user: UsuarioModel = Depends(require_role(["ADMIN"])),
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.deleted_at = datetime.utcnow()
    session.add(usuario)
    session.commit()
    return {"message": "Usuario desactivado"}
