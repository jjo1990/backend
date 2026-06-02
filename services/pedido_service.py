from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException
from sqlmodel import select
from models.pedido import Pedido, DetallePedido, HistorialEstadoPedido, EstadoPedido
from models.producto import Producto
from schemas.schemas import PedidoCreate
from unit_of_work.uow import UnitOfWork


TRANSICIONES = {
    "PENDIENTE": ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["EN_PREP", "CANCELADO"],
    "EN_PREP": ["EN_CAMINO"],
    "EN_CAMINO": ["ENTREGADO"],
    "ENTREGADO": [],
    "CANCELADO": [],
}


class PedidoService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def listar_mis_pedidos(self, usuario_id: int, offset: int = 0, limit: int = 20) -> list:
        return self.uow.pedidos.get_by_usuario(usuario_id, offset, limit)

    def listar_todos(self, offset: int = 0, limit: int = 20) -> list:
        return self.uow.pedidos.get_all_activos(offset, limit)

    def obtener_pedido(self, pedido_id: int, usuario_id: int | None = None):
        pedido = self.uow.pedidos.get_by_id(pedido_id)
        if not pedido or pedido.deleted_at:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        if usuario_id and pedido.usuario_id != usuario_id:
            raise HTTPException(status_code=403, detail="No puedes ver este pedido")
        return pedido

    def crear_pedido(self, data: PedidoCreate, usuario_id: int):
        with self.uow:
            total = Decimal(0)
            detalles = []

            for item in data.items:
                producto = self.uow.productos.get_by_id(item.producto_id)
                if not producto or producto.deleted_at:
                    raise HTTPException(status_code=404, detail=f"Producto {item.producto_id} no encontrado")
                if not producto.disponible:
                    raise HTTPException(status_code=400, detail=f"Producto '{producto.nombre}' no disponible")
                if producto.stock_cantidad < item.cantidad:
                    raise HTTPException(status_code=400, detail=f"Stock insuficiente para '{producto.nombre}'")

                subtotal = producto.precio_base * item.cantidad
                total += subtotal

                detalles.append(DetallePedido(
                    producto_id=producto.id,
                    producto_nombre=producto.nombre,
                    precio_unitario=producto.precio_base,
                    cantidad=item.cantidad,
                    subtotal=subtotal,
                ))

                producto.stock_cantidad -= item.cantidad
                self.uow.productos.add(producto)

            pedido = Pedido(
                usuario_id=usuario_id,
                forma_pago_id=data.forma_pago_id,
                estado_actual_id=1,
                direccion_entrega_id=data.direccion_entrega_id,
                total=total,
                notas=data.notas,
            )
            self.uow.pedidos.add(pedido)
            self.uow.session.flush()    # obtiene ID sin commit
            self.uow.refresh(pedido)

            for det in detalles:
                det.pedido_id = pedido.id
                self.uow.pedidos.add_detalle(det)

            self.uow.pedidos.add_historial(HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_anterior_id=None,
                estado_nuevo_id=1,
                cambiado_por_id=usuario_id,
            ))

            # __exit__ commitea todo

        self.uow.refresh(pedido)
        return pedido

    def cambiar_estado(self, pedido_id: int, nuevo_estado_codigo: str, cambiado_por_id: int):
        with self.uow:
            pedido = self.obtener_pedido(pedido_id)

            estado_actual = self.uow.session.get(EstadoPedido, pedido.estado_actual_id)
            estado_nuevo = self.uow.session.exec(
                select(EstadoPedido).where(EstadoPedido.codigo == nuevo_estado_codigo)
            ).first()

            if not estado_nuevo:
                raise HTTPException(status_code=400, detail=f"Estado '{nuevo_estado_codigo}' no válido")

            transiciones_validas = TRANSICIONES.get(estado_actual.codigo, [])
            if nuevo_estado_codigo not in transiciones_validas:
                raise HTTPException(
                    status_code=400,
                    detail=f"No puedes cambiar de {estado_actual.codigo} a {nuevo_estado_codigo}"
                )

            self.uow.pedidos.add_historial(HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_anterior_id=pedido.estado_actual_id,
                estado_nuevo_id=estado_nuevo.id,
                cambiado_por_id=cambiado_por_id,
            ))

            pedido.estado_actual_id = estado_nuevo.id
            pedido.updated_at = datetime.utcnow()
            self.uow.pedidos.add(pedido)
            # __exit__ commitea

        self.uow.refresh(pedido)
        return pedido

    def obtener_historial(self, pedido_id: int) -> list:
        pedido = self.obtener_pedido(pedido_id)
        self.uow.session.refresh(pedido)
        return pedido.historial_estados
