"""Modelos de autenticación y roles."""
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class Rol(SQLModel, table=True):
    """Roles del sistema: ADMIN, STOCK, PEDIDOS, CLIENT"""
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, max_length=20)
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    usuarios: List["UsuarioRol"] = Relationship(back_populates="rol")


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    nombre: str = Field(max_length=100)
    apellido: str = Field(max_length=100)
    telefono: Optional[str] = Field(default=None, max_length=20)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)
    roles: List["UsuarioRol"] = Relationship(back_populates="usuario")


class UsuarioRol(SQLModel, table=True):
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id", primary_key=True)
    rol_id: Optional[int] = Field(default=None, foreign_key="rol.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    usuario: Optional["Usuario"] = Relationship(back_populates="roles")
    rol: Optional["Rol"] = Relationship(back_populates="usuarios")
