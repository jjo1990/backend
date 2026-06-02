"""Servicio de direcciones de entrega."""
from datetime import datetime
from typing import List
from fastapi import HTTPException

from models.direccion import DireccionEntrega
from schemas.schemas import DireccionCreate, DireccionUpdate, DireccionRead
from unit_of_work.uow import UnitOfWork


class DireccionService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def listar(self, usuario_id: int) -> List[DireccionEntrega]:
        return self.uow.direcciones.get_activas_by_usuario(usuario_id)

    def obtener(self, direccion_id: int, usuario_id: int) -> DireccionEntrega:
        direccion = self.uow.direcciones.get_by_usuario(direccion_id, usuario_id)
        if not direccion or direccion.deleted_at:
            raise HTTPException(status_code=404, detail="Dirección no encontrada")
        return direccion

    def crear(self, data: DireccionCreate, usuario_id: int) -> DireccionEntrega:
        with self.uow:
            existentes = self.uow.direcciones.get_activas_by_usuario(usuario_id)
            es_principal = len(existentes) == 0

            direccion = DireccionEntrega(
                usuario_id=usuario_id,
                alias=data.alias,
                calle=data.calle,
                numero=data.numero,
                ciudad=data.ciudad,
                provincia=data.provincia,
                codigo_postal=data.codigo_postal,
                referencia=data.referencia,
                es_principal=es_principal,
            )
            self.uow.direcciones.add(direccion)
            # __exit__ commitea

        self.uow.refresh(direccion)
        return direccion

    def actualizar(self, direccion_id: int, cambios: DireccionUpdate, usuario_id: int) -> DireccionEntrega:
        with self.uow:
            direccion = self.obtener(direccion_id, usuario_id)

            datos = cambios.model_dump(exclude_unset=True)
            for campo, valor in datos.items():
                setattr(direccion, campo, valor)
            direccion.updated_at = datetime.utcnow()
            self.uow.direcciones.add(direccion)
            # __exit__ commitea

        self.uow.refresh(direccion)
        return direccion

    def eliminar(self, direccion_id: int, usuario_id: int) -> None:
        with self.uow:
            direccion = self.obtener(direccion_id, usuario_id)
            direccion.deleted_at = datetime.utcnow()
            self.uow.direcciones.add(direccion)
            # __exit__ commitea

    def marcar_principal(self, direccion_id: int, usuario_id: int) -> DireccionEntrega:
        with self.uow:
            direccion = self.obtener(direccion_id, usuario_id)

            # Desmarcar todas las demás
            existentes = self.uow.direcciones.get_activas_by_usuario(usuario_id)
            for d in existentes:
                d.es_principal = False

            direccion.es_principal = True
            direccion.updated_at = datetime.utcnow()
            self.uow.direcciones.add(direccion)
            # __exit__ commitea

        self.uow.refresh(direccion)
        return direccion
