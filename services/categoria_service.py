from datetime import datetime
from fastapi import HTTPException
from models.models import Categoria
from schemas.schemas import CategoriaCreate, CategoriaUpdate
from unit_of_work.uow import UnitOfWork

class CategoriaService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def listar_categorias(self, offset: int = 0, limit: int = 10, nombre: str | None = None):
        return self.uow.categorias.get_all(offset, limit, nombre)

    def obtener_categoria(self, categoria_id: int):
        categoria = self.uow.categorias.get_by_id(categoria_id)
        if not categoria or categoria.deleted_at:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return categoria

    def crear_categoria(self, categoria_data: CategoriaCreate):
        with self.uow:
            nueva = Categoria.model_validate(categoria_data)
            self.uow.categorias.add(nueva)
            self.uow.commit()
            self.uow.refresh(nueva)
            return nueva

    def actualizar_categoria(self, categoria_id: int, cambios: CategoriaUpdate):
        with self.uow:
            categoria = self.obtener_categoria(categoria_id)
            datos = cambios.model_dump(exclude_unset=True)
            for campo, valor in datos.items():
                setattr(categoria, campo, valor)
            categoria.updated_at = datetime.utcnow()
            self.uow.categorias.add(categoria)
            self.uow.commit()
            self.uow.refresh(categoria)
            return categoria

    def eliminar_categoria(self, categoria_id: int):
        with self.uow:
            categoria = self.obtener_categoria(categoria_id)
            categoria.deleted_at = datetime.utcnow()
            self.uow.categorias.add(categoria)
            self.uow.commit()
