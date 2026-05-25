from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from db.database import get_session
from unit_of_work.uow import UnitOfWork
from services.pedido_service import PedidoService
from schemas.schemas import PedidoCreate, PedidoRead, PedidoDetailRead, HistorialEstadoRead, EstadoUpdate, DetallePedidoRead, FormaPagoRead, EstadoPedidoRead
from dependencies import get_current_user, require_role, CurrentUser
from models.models import Usuario as UsuarioModel, EstadoPedido, FormaPago

router = APIRouter(prefix="/api/v1/pedidos", tags=["Pedidos"])
SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/formas-pago", response_model=List[FormaPagoRead])
def listar_formas_pago(session: SessionDep):
    from sqlmodel import select
    formas = session.exec(select(FormaPago)).all()
    return formas


@router.get("/estados", response_model=List[EstadoPedidoRead])
def listar_estados_pedido(session: SessionDep):
    from sqlmodel import select
    estados = session.exec(select(EstadoPedido).order_by(EstadoPedido.orden)).all()
    return estados


def get_pedido_service(session: SessionDep) -> PedidoService:
    uow = UnitOfWork(session)
    return PedidoService(uow)


PedidoServiceDep = Annotated[PedidoService, Depends(get_pedido_service)]


def _detalle_to_read(detalle):
    return DetallePedidoRead(
        id=detalle.id,
        producto_id=detalle.producto_id,
        producto_nombre=detalle.producto_nombre,
        precio_unitario=detalle.precio_unitario,
        cantidad=detalle.cantidad,
        subtotal=detalle.subtotal,
    )


def _pedido_to_read(pedido, session: Session) -> PedidoRead:
    estado = session.get(EstadoPedido, pedido.estado_actual_id)
    fp = session.get(FormaPago, pedido.forma_pago_id)
    return PedidoRead(
        id=pedido.id,
        usuario_id=pedido.usuario_id,
        total=pedido.total,
        estado=estado.codigo if estado else "",
        forma_pago=fp.nombre if fp else "",
        notas=pedido.notas,
        created_at=pedido.created_at,
        detalles=[_detalle_to_read(d) for d in pedido.detalles],
    )


@router.get("/", response_model=List[PedidoRead])
def listar_pedidos(
    service: PedidoServiceDep,
    current_user: CurrentUser,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
):
    user_roles = [ur.rol.codigo for ur in current_user.roles]
    if "ADMIN" in user_roles or "PEDIDOS" in user_roles:
        pedidos = service.listar_todos(offset, limit)
    else:
        pedidos = service.listar_mis_pedidos(current_user.id, offset, limit)
    return [_pedido_to_read(p, service.uow.session) for p in pedidos]


@router.get("/{pedido_id}", response_model=PedidoDetailRead)
def obtener_pedido(
    pedido_id: int,
    service: PedidoServiceDep,
    current_user: CurrentUser,
):
    user_roles = [ur.rol.codigo for ur in current_user.roles]
    if "ADMIN" in user_roles or "PEDIDOS" in user_roles:
        pedido = service.obtener_pedido(pedido_id)
    else:
        pedido = service.obtener_pedido(pedido_id, current_user.id)

    session = service.uow.session
    estado = session.get(EstadoPedido, pedido.estado_actual_id)
    fp = session.get(FormaPago, pedido.forma_pago_id)

    historial = []
    for h in pedido.historial_estados:
        est_ant = session.get(EstadoPedido, h.estado_anterior_id) if h.estado_anterior_id else None
        est_nue = session.get(EstadoPedido, h.estado_nuevo_id)
        historial.append(HistorialEstadoRead(
            id=h.id,
            estado_anterior=est_ant.codigo if est_ant else None,
            estado_nuevo=est_nue.codigo if est_nue else "",
            cambiado_por_id=h.cambiado_por_id,
            created_at=h.created_at,
        ))

    return PedidoDetailRead(
        id=pedido.id,
        usuario_id=pedido.usuario_id,
        total=pedido.total,
        estado=estado.codigo if estado else "",
        forma_pago=fp.nombre if fp else "",
        notas=pedido.notas,
        created_at=pedido.created_at,
        detalles=[_detalle_to_read(d) for d in pedido.detalles],
        historial=historial,
    )


@router.post("/", response_model=PedidoRead, status_code=201)
def crear_pedido(
    data: PedidoCreate,
    service: PedidoServiceDep,
    current_user: CurrentUser,
):
    pedido = service.crear_pedido(data, current_user.id)
    return _pedido_to_read(pedido, service.uow.session)


@router.patch("/{pedido_id}/estado", response_model=PedidoRead)
def cambiar_estado_pedido(
    pedido_id: int,
    data: EstadoUpdate,
    service: PedidoServiceDep,
    current_user: UsuarioModel = Depends(require_role(["ADMIN", "PEDIDOS"])),
):
    pedido = service.cambiar_estado(pedido_id, data.nuevo_estado, current_user.id)
    return _pedido_to_read(pedido, service.uow.session)


@router.patch("/{pedido_id}/cancelar", response_model=PedidoRead)
def cancelar_pedido(
    pedido_id: int,
    service: PedidoServiceDep,
    current_user: CurrentUser,
):
    session = service.uow.session
    pedido = service.obtener_pedido(pedido_id, current_user.id)
    estado = session.get(EstadoPedido, pedido.estado_actual_id)
    if estado.codigo not in ["PENDIENTE", "CONFIRMADO"]:
        raise HTTPException(status_code=400, detail="No puedes cancelar este pedido en su estado actual")

    pedido = service.cambiar_estado(pedido_id, "CANCELADO", current_user.id)
    return _pedido_to_read(pedido, session)
