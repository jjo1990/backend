from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from db.database import get_session
from unit_of_work.uow import UnitOfWork
from services.ingrediente_service import IngredienteService
from schemas.schemas import IngredienteCreate, IngredienteRead, IngredienteUpdate

router = APIRouter(prefix="/api/v1/ingredientes", tags=["Ingredientes"])
SessionDep = Annotated[Session, Depends(get_session)]

def get_ingrediente_service(session: SessionDep) -> IngredienteService:
    uow = UnitOfWork(session)
    return IngredienteService(uow)

IngredienteServiceDep = Annotated[IngredienteService, Depends(get_ingrediente_service)]

@router.get("/", response_model=List[IngredienteRead])
def listar_ingredientes(
    service: IngredienteServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    nombre: Annotated[str | None, Query()] = None,
):
    return service.listar_ingredientes(offset, limit, nombre)

@router.get("/{ingrediente_id}", response_model=IngredienteRead)
def obtener_ingrediente(ingrediente_id: int, service: IngredienteServiceDep):
    return service.obtener_ingrediente(ingrediente_id)

@router.post("/", response_model=IngredienteRead, status_code=201)
def crear_ingrediente(data: IngredienteCreate, service: IngredienteServiceDep):
    return service.crear_ingrediente(data)

@router.patch("/{ingrediente_id}", response_model=IngredienteRead)
def actualizar_ingrediente(ingrediente_id: int, cambios: IngredienteUpdate, service: IngredienteServiceDep):
    return service.actualizar_ingrediente(ingrediente_id, cambios)

@router.delete("/{ingrediente_id}", status_code=204)
def eliminar_ingrediente(ingrediente_id: int, service: IngredienteServiceDep):
    service.eliminar_ingrediente(ingrediente_id)
