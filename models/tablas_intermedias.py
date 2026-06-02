"""Tablas intermedias para relaciones N a N."""
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime


class ProductoIngrediente(SQLModel, table=True):
    """Conecta Producto con Ingrediente."""
    producto_id: Optional[int] = Field(
        default=None, foreign_key="producto.id", primary_key=True
    )
    ingrediente_id: Optional[int] = Field(
        default=None, foreign_key="ingrediente.id", primary_key=True
    )
    es_removible: bool = Field(default=False)


class ProductoCategoria(SQLModel, table=True):
    """Conecta Producto con Categoria (M:M según UML)."""
    producto_id: Optional[int] = Field(
        default=None, foreign_key="producto.id", primary_key=True
    )
    categoria_id: Optional[int] = Field(
        default=None, foreign_key="categoria.id", primary_key=True
    )
    es_principal: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
