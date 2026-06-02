from typing import Annotated
from fastapi import APIRouter, Depends, Response
from sqlmodel import Session

from db.database import get_session
from services.auth_service import AuthService
from schemas.schemas import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from dependencies import CurrentUser
from unit_of_work.uow import UnitOfWork

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])
SessionDep = Annotated[Session, Depends(get_session)]


def get_auth_service(session: SessionDep) -> AuthService:
    uow = UnitOfWork(session)
    return AuthService(uow)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: RegisterRequest, response: Response, service: AuthServiceDep):
    token, user = service.register(data)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=1800,
        samesite="lax",
    )

    return TokenResponse(access_token=token, user=user)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, response: Response, service: AuthServiceDep):
    token, user = service.login(data)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=1800,
        samesite="lax",
    )

    return TokenResponse(access_token=token, user=user)


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
