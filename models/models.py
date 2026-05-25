from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, String
from sqlalchemy.dialects.postgresql import ARRAY


# ─────────────────────────────────────────────
# TABLAS INTERMEDIAS (relación N a N)
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# CATEGORÍA
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# INGREDIENTE
# ─────────────────────────────────────────────
class Ingrediente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, max_length=100)
    descripcion: Optional[str] = Field(default=None)
    es_alergeno: bool = Field(default=False)
    
    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    productos: List["Producto"] = Relationship(
        back_populates="ingredientes", link_model=ProductoIngrediente
    )


# ─────────────────────────────────────────────
# PRODUCTO
# ─────────────────────────────────────────────
class Producto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=150)
    descripcion: Optional[str] = Field(default=None)
    precio_base: Decimal = Field(default=0, decimal_places=2)
    # Usamos ARRAY de PostgreSQL para las URLs de imágenes
    imagenes_url: List[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    stock_cantidad: int = Field(default=0, ge=0)
    disponible: bool = Field(default=True)
    
    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    categorias: List["Categoria"] = Relationship(
        back_populates="productos", link_model=ProductoCategoria
    )
    ingredientes: List["Ingrediente"] = Relationship(
        back_populates="productos", link_model=ProductoIngrediente
    )


# ─────────────────────────────────────────────
# AUTENTICACIÓN Y ROLES
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# DIRECCIÓN DE ENTREGA
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# PEDIDOS
# ─────────────────────────────────────────────

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

