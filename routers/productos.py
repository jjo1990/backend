from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from db.database import get_session
from unit_of_work.uow import UnitOfWork
from services.producto_service import ProductoService
from schemas.schemas import ProductoCreate, ProductoRead, ProductoUpdate

router = APIRouter(prefix="/api/v1/productos", tags=["Productos"])
SessionDep = Annotated[Session, Depends(get_session)]

def get_producto_service(session: SessionDep) -> ProductoService:
    uow = UnitOfWork(session)
    return ProductoService(uow)

ProductoServiceDep = Annotated[ProductoService, Depends(get_producto_service)]

@router.get("/", response_model=List[ProductoRead])
def listar_productos(
    service: ProductoServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=100)] = 20,
    nombre: Annotated[str | None, Query()] = None,
    categoria_id: Annotated[int | None, Query()] = None,
    disponible: Annotated[bool | None, Query()] = None,
):
    return service.listar_productos(offset, limit, nombre, categoria_id, disponible)

@router.get("/{producto_id}", response_model=ProductoRead)
def obtener_producto(producto_id: int, service: ProductoServiceDep):
    return service.obtener_producto(producto_id)

@router.post("/", response_model=ProductoRead, status_code=201)
def crear_producto(data: ProductoCreate, service: ProductoServiceDep):
    return service.crear_producto(data)

@router.patch("/{producto_id}", response_model=ProductoRead)
def actualizar_producto(producto_id: int, cambios: ProductoUpdate, service: ProductoServiceDep):
    return service.actualizar_producto(producto_id, cambios)

@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(producto_id: int, service: ProductoServiceDep):
    service.eliminar_producto(producto_id)
