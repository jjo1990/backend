from typing import Optional, List
from sqlmodel import Session, select
from models.models import Categoria
from .base import BaseRepository

class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self, session: Session):
        super().__init__(session, Categoria)

    def get_all(self, offset: int = 0, limit: int = 10, nombre: Optional[str] = None) -> List[Categoria]:
        query = select(Categoria).where(Categoria.deleted_at == None)
        if nombre:
            query = query.where(Categoria.nombre.ilike(f"%{nombre}%"))
        query = query.offset(offset).limit(limit)
        return self.session.exec(query).all()
