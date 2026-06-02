"""Modelo de Dirección de Entrega."""
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class DireccionEntrega(SQLModel, table=True):
    """Direcciones de entrega asociadas a un usuario."""
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    alias: str = Field(default="Principal", max_length=50)
    calle: str = Field(max_length=200)
    numero: str = Field(max_length=20)
    ciudad: str = Field(max_length=100)
    provincia: str = Field(max_length=100)
    codigo_postal: Optional[str] = Field(default=None, max_length=20)
    referencia: Optional[str] = Field(default=None)
    es_principal: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)
