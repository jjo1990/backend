from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from db.database import get_session
from models.usuario import Usuario, Rol, UsuarioRol
from models.usuario import Usuario as UsuarioModel
from schemas.schemas import UserResponse
from dependencies import require_role
from services.admin_service import AdminService
from unit_of_work.uow import UnitOfWork

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])
SessionDep = Annotated[Session, Depends(get_session)]


def get_admin_service(session: SessionDep) -> AdminService:
    uow = UnitOfWork(session)
    return AdminService(uow)


AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]


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
    service: AdminServiceDep,
    current_user: UsuarioModel = Depends(require_role(["ADMIN"])),
):
    return service.asignar_roles(usuario_id, roles_data)


@router.patch("/usuarios/{usuario_id}/deactivate")
def deactivate_user(
    usuario_id: int,
    service: AdminServiceDep,
    current_user: UsuarioModel = Depends(require_role(["ADMIN"])),
):
    return service.deactivate_user(usuario_id)
