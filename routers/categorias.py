from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from db.database import get_session
from unit_of_work.uow import UnitOfWork
from services.categoria_service import CategoriaService
from schemas.schemas import CategoriaCreate, CategoriaRead, CategoriaUpdate

router = APIRouter(prefix="/api/v1/categorias", tags=["Categorías"])
SessionDep = Annotated[Session, Depends(get_session)]

def get_categoria_service(session: SessionDep) -> CategoriaService:
    uow = UnitOfWork(session)
    return CategoriaService(uow)

CategoriaServiceDep = Annotated[CategoriaService, Depends(get_categoria_service)]

@router.get("/", response_model=List[CategoriaRead])
def listar_categorias(
    service: CategoriaServiceDep,
    offset: Annotated[int, Query(ge=0, description="Cuántos registros saltear")] = 0,
    limit: Annotated[int, Query(le=100, description="Máximo de resultados")] = 10,
    nombre: Annotated[str | None, Query(description="Filtrar por nombre")] = None,
):
    return service.listar_categorias(offset, limit, nombre)

@router.get("/{categoria_id}", response_model=CategoriaRead)
def obtener_categoria(categoria_id: int, service: CategoriaServiceDep):
    return service.obtener_categoria(categoria_id)

@router.post("/", response_model=CategoriaRead, status_code=201)
def crear_categoria(categoria_data: CategoriaCreate, service: CategoriaServiceDep):
    return service.crear_categoria(categoria_data)

@router.patch("/{categoria_id}", response_model=CategoriaRead)
def actualizar_categoria(categoria_id: int, cambios: CategoriaUpdate, service: CategoriaServiceDep):
    return service.actualizar_categoria(categoria_id, cambios)

@router.delete("/{categoria_id}", status_code=204)
def eliminar_categoria(categoria_id: int, service: CategoriaServiceDep):
    service.eliminar_categoria(categoria_id)
