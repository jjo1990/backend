from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlmodel import Session, select
from datetime import datetime

from db.database import get_session
from models.models import Usuario, Rol, UsuarioRol
from schemas.schemas import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from dependencies import create_access_token, get_current_user, CurrentUser
import bcrypt

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])
SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: RegisterRequest, session: SessionDep, response: Response):
    existing = session.exec(select(Usuario).where(Usuario.email == data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    password_hash = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt(12)).decode()

    user = Usuario(
        email=data.email,
        password_hash=password_hash,
        nombre=data.nombre,
        apellido=data.apellido,
        telefono=data.telefono,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    rol_client = session.exec(select(Rol).where(Rol.codigo == "CLIENT")).first()
    if rol_client:
        session.add(UsuarioRol(usuario_id=user.id, rol_id=rol_client.id))
        session.commit()

    token = create_access_token({"sub": str(user.id)})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=1800,
        samesite="lax",
    )

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            nombre=user.nombre,
            apellido=user.apellido,
            telefono=user.telefono,
            activo=user.activo,
            roles=["CLIENT"],
        )
    )


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, session: SessionDep, response: Response):
    user = session.exec(select(Usuario).where(Usuario.email == data.email)).first()
    if not user or not user.activo or user.deleted_at:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not bcrypt.checkpw(data.password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({"sub": str(user.id)})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=1800,
        samesite="lax",
    )

    roles = [ur.rol.codigo for ur in user.roles]

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            nombre=user.nombre,
            apellido=user.apellido,
            telefono=user.telefono,
            activo=user.activo,
            roles=roles,
        )
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    roles = [ur.rol.codigo for ur in current_user.roles]
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        nombre=current_user.nombre,
        apellido=current_user.apellido,
        telefono=current_user.telefono,
        activo=current_user.activo,
        roles=roles,
    )


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Sesión cerrada"}
