from typing import Optional, List
from sqlmodel import Session, select
from models.producto import Producto
from models.tablas_intermedias import ProductoCategoria, ProductoIngrediente
from .base import BaseRepository

class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session):
        super().__init__(session, Producto)

    def get_all(
        self, 
        offset: int = 0, 
        limit: int = 20, 
        nombre: Optional[str] = None,
        categoria_id: Optional[int] = None,
        disponible: Optional[bool] = None
    ) -> List[Producto]:
        query = select(Producto)
        if nombre:
            query = query.where(Producto.nombre.ilike(f"%{nombre}%"))
        if categoria_id:
            query = query.join(ProductoCategoria).where(ProductoCategoria.categoria_id == categoria_id)
        if disponible is not None:
            query = query.where(Producto.disponible == disponible)
        
        query = query.where(Producto.deleted_at == None)
        return self.session.exec(query.offset(offset).limit(limit)).all()
        
    def add_producto_categoria(self, producto_id: int, categoria_id: int):
        self.session.add(ProductoCategoria(producto_id=producto_id, categoria_id=categoria_id))
        
    def add_producto_ingrediente(self, producto_id: int, ingrediente_id: int):
        self.session.add(ProductoIngrediente(producto_id=producto_id, ingrediente_id=ingrediente_id))
        
    def clear_categorias(self, producto_id: int):
        viejos = self.session.exec(select(ProductoCategoria).where(ProductoCategoria.producto_id == producto_id)).all()
        for v in viejos:
            self.session.delete(v)
            
    def clear_ingredientes(self, producto_id: int):
        viejos = self.session.exec(select(ProductoIngrediente).where(ProductoIngrediente.producto_id == producto_id)).all()
        for v in viejos:
            self.session.delete(v)
