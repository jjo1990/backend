from datetime import datetime
from fastapi import HTTPException
from models.ingrediente import Ingrediente
from schemas.schemas import IngredienteCreate, IngredienteUpdate
from unit_of_work.uow import UnitOfWork

class IngredienteService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def listar_ingredientes(self, offset: int = 0, limit: int = 10, nombre: str | None = None):
        return self.uow.ingredientes.get_all(offset, limit, nombre)

    def obtener_ingrediente(self, ingrediente_id: int):
        ingrediente = self.uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        return ingrediente

    def crear_ingrediente(self, ingrediente_data: IngredienteCreate):
        with self.uow:
            nuevo = Ingrediente.model_validate(ingrediente_data)
            self.uow.ingredientes.add(nuevo)
            # __exit__ commitea

        self.uow.refresh(nuevo)
        return nuevo

    def actualizar_ingrediente(self, ingrediente_id: int, cambios: IngredienteUpdate):
        with self.uow:
            ingrediente = self.obtener_ingrediente(ingrediente_id)
            datos = cambios.model_dump(exclude_unset=True)
            for campo, valor in datos.items():
                setattr(ingrediente, campo, valor)
            ingrediente.updated_at = datetime.utcnow()
            self.uow.ingredientes.add(ingrediente)
            # __exit__ commitea

        self.uow.refresh(ingrediente)
        return ingrediente

    def eliminar_ingrediente(self, ingrediente_id: int):
        with self.uow:
            ingrediente = self.obtener_ingrediente(ingrediente_id)
            self.uow.ingredientes.delete(ingrediente)
            # __exit__ commitea
