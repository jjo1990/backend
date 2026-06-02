"""Servicio de autenticación — encapsula hasheo de contraseñas y creación de usuarios."""
from fastapi import HTTPException
from sqlmodel import select
import bcrypt

from models.usuario import Usuario, UsuarioRol, Rol
from schemas.schemas import RegisterRequest, LoginRequest, UserResponse
from unit_of_work.uow import UnitOfWork
from dependencies import create_access_token


class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    # ── Helpers privados ──────────────────────────────────

    @staticmethod
    def _hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode(), password_hash.encode())

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

    # ── Casos de uso ──────────────────────────────────────

    def register(self, data: RegisterRequest) -> tuple[str, UserResponse]:
        """Crea un usuario + asigna rol CLIENT + genera token."""
        existing = self.uow.usuarios.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email ya registrado")

        with self.uow:
            user = Usuario(
                email=data.email,
                password_hash=self._hash_password(data.password),
                nombre=data.nombre,
                apellido=data.apellido,
                telefono=data.telefono,
            )
            self.uow.usuarios.add(user)
            self.uow.session.flush()  # obtiene ID sin commit
            self.uow.refresh(user)

            # Asignar rol CLIENT por defecto
            rol_client = self.uow.session.exec(
                select(Rol).where(Rol.codigo == "CLIENT")
            ).first()
            if rol_client:
                self.uow.session.add(UsuarioRol(usuario_id=user.id, rol_id=rol_client.id))

            # __exit__ commitea

        token = create_access_token({"sub": str(user.id)})
        return token, self._build_user_response(user)

    def login(self, data: LoginRequest) -> tuple[str, UserResponse]:
        """Valida credenciales y genera token."""
        user = self.uow.usuarios.get_by_email(data.email)
        if not user or not user.activo or user.deleted_at:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        if not self._verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        token = create_access_token({"sub": str(user.id)})
        return token, self._build_user_response(user)
