from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from db.database import get_session
from models.models import Usuario, Rol
import jwt
import os

SessionDep = Annotated[Session, Depends(get_session)]
security = HTTPBearer(auto_error=False)
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
ALGORITHM = "HS256"


def create_access_token(data: dict) -> str:
    from datetime import datetime, timedelta
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
) -> Usuario:
    """Obtiene el usuario actual desde el token JWT (desde cookie o header)"""
    token = None
    if credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = session.get(Usuario, user_id)
    if not user or user.deleted_at or not user.activo:
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")
    return user


CurrentUser = Annotated[Usuario, Depends(get_current_user)]


def require_role(codigos_rol: List[str]):
    """Factory que retorna un dependency para verificar roles"""
    def role_checker(current_user: CurrentUser) -> Usuario:
        user_roles = current_user.roles
        has_role = any(ur.rol.codigo in codigos_rol for ur in user_roles)
        if not has_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para esta acción")
        return current_user
    return role_checker
