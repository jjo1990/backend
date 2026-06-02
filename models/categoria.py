"""Modelo de Categoría."""
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from models.tablas_intermedias import ProductoCategoria


class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    nombre: str = Field(unique=True, index=True, max_length=100)
    descripcion: Optional[str] = Field(default=None)
    imagen_url: Optional[str] = Field(default=None)

    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    productos: List["Producto"] = Relationship(
        back_populates="categorias", link_model=ProductoCategoria
    )
    # Self-reference for hierarchy
    subcategorias: List["Categoria"] = Relationship(
        back_populates="parent_categoria",
        sa_relationship_kwargs={"remote_side": "Categoria.id"}
    )
    parent_categoria: Optional["Categoria"] = Relationship(
        back_populates="subcategorias"
    )
