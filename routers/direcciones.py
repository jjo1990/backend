from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlmodel import Session

from db.database import get_session
from schemas.schemas import DireccionCreate, DireccionRead, DireccionUpdate
from dependencies import CurrentUser
from services.direccion_service import DireccionService
from unit_of_work.uow import UnitOfWork

router = APIRouter(prefix="/api/v1/direcciones", tags=["Direcciones"])
SessionDep = Annotated[Session, Depends(get_session)]


def get_direccion_service(session: SessionDep) -> DireccionService:
    uow = UnitOfWork(session)
    return DireccionService(uow)


DireccionServiceDep = Annotated[DireccionService, Depends(get_direccion_service)]


@router.get("/", response_model=List[DireccionRead])
def listar_direcciones(service: DireccionServiceDep, current_user: CurrentUser):
    return service.listar(current_user.id)


@router.post("/", response_model=DireccionRead, status_code=201)
def crear_direccion(data: DireccionCreate, service: DireccionServiceDep, current_user: CurrentUser):
    return service.crear(data, current_user.id)


@router.get("/{direccion_id}", response_model=DireccionRead)
def obtener_direccion(direccion_id: int, service: DireccionServiceDep, current_user: CurrentUser):
    return service.obtener(direccion_id, current_user.id)


@router.patch("/{direccion_id}", response_model=DireccionRead)
def actualizar_direccion(direccion_id: int, cambios: DireccionUpdate, service: DireccionServiceDep, current_user: CurrentUser):
    return service.actualizar(direccion_id, cambios, current_user.id)


@router.delete("/{direccion_id}", status_code=204)
def eliminar_direccion(direccion_id: int, service: DireccionServiceDep, current_user: CurrentUser):
    service.eliminar(direccion_id, current_user.id)


@router.patch("/{direccion_id}/principal", response_model=DireccionRead)
def marcar_principal(direccion_id: int, service: DireccionServiceDep, current_user: CurrentUser):
    return service.marcar_principal(direccion_id, current_user.id)
