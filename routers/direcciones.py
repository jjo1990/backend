from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime

from db.database import get_session
from models.models import DireccionEntrega
from schemas.schemas import DireccionCreate, DireccionRead, DireccionUpdate
from dependencies import get_current_user, CurrentUser

router = APIRouter(prefix="/api/v1/direcciones", tags=["Direcciones"])
SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/", response_model=List[DireccionRead])
def listar_direcciones(session: SessionDep, current_user: CurrentUser):
    query = select(DireccionEntrega).where(
        DireccionEntrega.usuario_id == current_user.id,
        DireccionEntrega.deleted_at == None,
    )
    return session.exec(query).all()


@router.post("/", response_model=DireccionRead, status_code=201)
def crear_direccion(data: DireccionCreate, session: SessionDep, current_user: CurrentUser):
    existentes = session.exec(
        select(DireccionEntrega).where(
            DireccionEntrega.usuario_id == current_user.id,
            DireccionEntrega.deleted_at == None,
        )
    ).all()

    es_principal = len(existentes) == 0

    direccion = DireccionEntrega(
        usuario_id=current_user.id,
        alias=data.alias,
        calle=data.calle,
        numero=data.numero,
        ciudad=data.ciudad,
        provincia=data.provincia,
        codigo_postal=data.codigo_postal,
        referencia=data.referencia,
        es_principal=es_principal,
    )
    session.add(direccion)
    session.commit()
    session.refresh(direccion)
    return direccion


@router.get("/{direccion_id}", response_model=DireccionRead)
def obtener_direccion(direccion_id: int, session: SessionDep, current_user: CurrentUser):
    direccion = session.get(DireccionEntrega, direccion_id)
    if not direccion or direccion.deleted_at or direccion.usuario_id != current_user.id:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    return direccion


@router.patch("/{direccion_id}", response_model=DireccionRead)
def actualizar_direccion(direccion_id: int, cambios: DireccionUpdate, session: SessionDep, current_user: CurrentUser):
    direccion = session.get(DireccionEntrega, direccion_id)
    if not direccion or direccion.deleted_at or direccion.usuario_id != current_user.id:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")

    datos = cambios.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(direccion, campo, valor)
    direccion.updated_at = datetime.utcnow()
    session.add(direccion)
    session.commit()
    session.refresh(direccion)
    return direccion


@router.delete("/{direccion_id}", status_code=204)
def eliminar_direccion(direccion_id: int, session: SessionDep, current_user: CurrentUser):
    direccion = session.get(DireccionEntrega, direccion_id)
    if not direccion or direccion.deleted_at or direccion.usuario_id != current_user.id:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    direccion.deleted_at = datetime.utcnow()
    session.add(direccion)
    session.commit()


@router.patch("/{direccion_id}/principal", response_model=DireccionRead)
def marcar_principal(direccion_id: int, session: SessionDep, current_user: CurrentUser):
    direccion = session.get(DireccionEntrega, direccion_id)
    if not direccion or direccion.deleted_at or direccion.usuario_id != current_user.id:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")

    existentes = session.exec(
        select(DireccionEntrega).where(
            DireccionEntrega.usuario_id == current_user.id,
            DireccionEntrega.deleted_at == None,
        )
    ).all()
    for d in existentes:
        d.es_principal = False

    direccion.es_principal = True
    direccion.updated_at = datetime.utcnow()
    session.add(direccion)
    session.commit()
    session.refresh(direccion)
    return direccion
