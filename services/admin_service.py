"""Servicio de administración — operaciones que requieren rol ADMIN."""
from datetime import datetime
from fastapi import HTTPException
from sqlmodel import select

from models.usuario import Usuario, Rol, UsuarioRol
from schemas.schemas import UserResponse
from unit_of_work.uow import UnitOfWork


class AdminService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def _build_user_response(self, usuario: Usuario) -> UserResponse:
        roles = [ur.rol.codigo for ur in usuario.roles]
        return UserResponse(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            telefono=usuario.telefono,
            activo=usuario.activo,
            roles=roles,
        )

    def asignar_roles(self, usuario_id: int, roles_data: dict) -> UserResponse:
        with self.uow:
            usuario = self.uow.usuarios.get_by_id(usuario_id)
            if not usuario or usuario.deleted_at:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            # Eliminar roles anteriores
            viejos = self.uow.session.exec(
                select(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)
            ).all()
            for v in viejos:
                self.uow.session.delete(v)

            # Asignar nuevos roles
            for codigo in roles_data.get("roles", []):
                rol = self.uow.session.exec(
                    select(Rol).where(Rol.codigo == codigo)
                ).first()
                if rol:
                    self.uow.session.add(UsuarioRol(usuario_id=usuario_id, rol_id=rol.id))

            # __exit__ commitea

        self.uow.refresh(usuario)
        return self._build_user_response(usuario)

    def deactivate_user(self, usuario_id: int) -> dict:
        with self.uow:
            usuario = self.uow.usuarios.get_by_id(usuario_id)
            if not usuario:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            usuario.deleted_at = datetime.utcnow()
            self.uow.usuarios.add(usuario)
            # __exit__ commitea

        return {"message": "Usuario desactivado"}
