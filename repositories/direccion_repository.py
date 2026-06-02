from typing import List, Optional
from sqlmodel import Session, select
from models.direccion import DireccionEntrega
from .base import BaseRepository


class DireccionRepository(BaseRepository[DireccionEntrega]):
    def __init__(self, session: Session):
        super().__init__(session, DireccionEntrega)

    def get_activas_by_usuario(self, usuario_id: int) -> List[DireccionEntrega]:
        return self.session.exec(
            select(DireccionEntrega).where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.deleted_at == None,
            )
        ).all()

    def get_by_usuario(self, direccion_id: int, usuario_id: int) -> Optional[DireccionEntrega]:
        """Retorna una dirección solo si pertenece al usuario."""
        direccion = self.session.get(DireccionEntrega, direccion_id)
        if direccion and direccion.usuario_id == usuario_id:
            return direccion
        return None
