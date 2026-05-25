from typing import Optional, List
from sqlmodel import Session, select
from models.models import Ingrediente
from .base import BaseRepository

class IngredienteRepository(BaseRepository[Ingrediente]):
    def __init__(self, session: Session):
        super().__init__(session, Ingrediente)

    def get_all(self, offset: int = 0, limit: int = 10, nombre: Optional[str] = None) -> List[Ingrediente]:
        query = select(Ingrediente)
        if nombre:
            query = query.where(Ingrediente.nombre.ilike(f"%{nombre}%"))
        return self.session.exec(query.offset(offset).limit(limit)).all()
