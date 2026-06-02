"""Modelos del módulo de pedidos."""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship


class FormaPago(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=50)
    codigo: str = Field(unique=True, max_length=20)
    activo: bool = Field(default=True)


class EstadoPedido(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, max_length=20)
    nombre: str = Field(max_length=50)
    orden: int = Field(default=0)


class Pedido(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    forma_pago_id: int = Field(foreign_key="formapago.id")
    estado_actual_id: int = Field(foreign_key="estadopedido.id")
    direccion_entrega_id: Optional[int] = Field(default=None, foreign_key="direccionentrega.id")
    total: Decimal = Field(default=0, decimal_places=2)
    notas: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    detalles: List["DetallePedido"] = Relationship(back_populates="pedido")
    estado_actual: Optional["EstadoPedido"] = Relationship()
    forma_pago: Optional["FormaPago"] = Relationship()
    historial_estados: List["HistorialEstadoPedido"] = Relationship(back_populates="pedido")


class DetallePedido(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id")
    producto_id: int = Field(foreign_key="producto.id")
    producto_nombre: str = Field(max_length=150)
    precio_unitario: Decimal = Field(decimal_places=2)
    cantidad: int = Field(default=1, ge=1)
    subtotal: Decimal = Field(decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    pedido: Optional["Pedido"] = Relationship(back_populates="detalles")
    producto: Optional["Producto"] = Relationship()


class HistorialEstadoPedido(SQLModel, table=True):
    """Audit Trail append-only - solo INSERTs, nunca UPDATE/DELETE"""
    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id")
    estado_anterior_id: Optional[int] = Field(default=None, foreign_key="estadopedido.id")
    estado_nuevo_id: int = Field(foreign_key="estadopedido.id")
    cambiado_por_id: int = Field(foreign_key="usuario.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    pedido: Optional["Pedido"] = Relationship(back_populates="historial_estados")
    estado_nuevo: Optional["EstadoPedido"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "HistorialEstadoPedido.estado_nuevo_id"}
    )
    estado_anterior: Optional["EstadoPedido"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "HistorialEstadoPedido.estado_anterior_id"}
    )
