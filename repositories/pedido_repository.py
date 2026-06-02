from typing import Optional, List
from sqlmodel import Session, select
from models.pedido import Pedido, DetallePedido, HistorialEstadoPedido
from .base import BaseRepository


class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: Session):
        super().__init__(session, Pedido)

    def get_by_usuario(self, usuario_id: int, offset: int = 0, limit: int = 20) -> List[Pedido]:
        query = select(Pedido).where(Pedido.usuario_id == usuario_id, Pedido.deleted_at == None)
        return self.session.exec(query.offset(offset).limit(limit)).all()

    def get_all_activos(self, offset: int = 0, limit: int = 20) -> List[Pedido]:
        query = select(Pedido).where(Pedido.deleted_at == None)
        return self.session.exec(query.offset(offset).limit(limit)).all()

    def add_detalle(self, detalle: DetallePedido):
        self.session.add(detalle)

    def add_historial(self, historial: HistorialEstadoPedido):
        self.session.add(historial)
