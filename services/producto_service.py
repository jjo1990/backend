from datetime import datetime
from fastapi import HTTPException
from models.models import Producto
from schemas.schemas import ProductoCreate, ProductoUpdate
from unit_of_work.uow import UnitOfWork

class ProductoService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def listar_productos(self, offset: int = 0, limit: int = 20, nombre: str | None = None, categoria_id: int | None = None, disponible: bool | None = None):
        return self.uow.productos.get_all(offset, limit, nombre, categoria_id, disponible)

    def obtener_producto(self, producto_id: int):
        producto = self.uow.productos.get_by_id(producto_id)
        if not producto or producto.deleted_at:
            raise HTTPException(status_code=404, detail="Producto no encontrado o eliminado")
        return producto

    def crear_producto(self, data: ProductoCreate):
        with self.uow:
            categoria_ids = data.categoria_ids
            ingrediente_ids = data.ingrediente_ids
            
            producto_data = data.model_dump(exclude={"categoria_ids", "ingrediente_ids"})
            nuevo = Producto(**producto_data)
            self.uow.productos.add(nuevo)
            self.uow.commit()
            self.uow.refresh(nuevo)

            # Vincular categorías
            for cat_id in categoria_ids:
                if not self.uow.categorias.get_by_id(cat_id):
                    raise HTTPException(status_code=404, detail=f"Categoría {cat_id} no encontrada")
                self.uow.productos.add_producto_categoria(nuevo.id, cat_id)

            # Vincular ingredientes
            for ing_id in ingrediente_ids:
                if not self.uow.ingredientes.get_by_id(ing_id):
                    raise HTTPException(status_code=404, detail=f"Ingrediente {ing_id} no encontrado")
                self.uow.productos.add_producto_ingrediente(nuevo.id, ing_id)

            self.uow.commit()
            self.uow.refresh(nuevo)
            return nuevo

    def actualizar_producto(self, producto_id: int, cambios: ProductoUpdate):
        with self.uow:
            producto = self.obtener_producto(producto_id)

            if cambios.categoria_ids is not None:
                self.uow.productos.clear_categorias(producto_id)
                for cat_id in cambios.categoria_ids:
                    if not self.uow.categorias.get_by_id(cat_id):
                        raise HTTPException(status_code=404, detail=f"Categoría {cat_id} no encontrada")
                    self.uow.productos.add_producto_categoria(producto_id, cat_id)

            if cambios.ingrediente_ids is not None:
                self.uow.productos.clear_ingredientes(producto_id)
                for ing_id in cambios.ingrediente_ids:
                    if not self.uow.ingredientes.get_by_id(ing_id):
                        raise HTTPException(status_code=404, detail=f"Ingrediente {ing_id} no encontrado")
                    self.uow.productos.add_producto_ingrediente(producto_id, ing_id)

            datos = cambios.model_dump(exclude_unset=True, exclude={"categoria_ids", "ingrediente_ids"})
            for campo, valor in datos.items():
                setattr(producto, campo, valor)
            
            producto.updated_at = datetime.utcnow()
            self.uow.productos.add(producto)
            self.uow.commit()
            self.uow.refresh(producto)
            return producto

    def eliminar_producto(self, producto_id: int):
        with self.uow:
            producto = self.obtener_producto(producto_id)
            producto.deleted_at = datetime.utcnow()
            self.uow.productos.add(producto)
            self.uow.commit()
