from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel


# ══════════════════════════════════════
# SCHEMAS DE CATEGORÍA
# ══════════════════════════════════════

class CategoriaBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaRead(CategoriaBase):
    id: int
    created_at: datetime
    updated_at: datetime


class CategoriaUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = None


# ══════════════════════════════════════
# SCHEMAS DE INGREDIENTE
# ══════════════════════════════════════

class IngredienteBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    es_alergeno: bool = False


class IngredienteCreate(IngredienteBase):
    pass


class IngredienteRead(IngredienteBase):
    id: int
    created_at: datetime
    updated_at: datetime


class IngredienteUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None


# ══════════════════════════════════════
# SCHEMAS DE PRODUCTO
# ══════════════════════════════════════

class ProductoBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_base: Decimal
    imagenes_url: List[str] = []
    stock_cantidad: int = 0
    disponible: bool = True


class ProductoCreate(ProductoBase):
    categoria_ids: List[int] = []     # Lista de IDs de categorías
    ingrediente_ids: List[int] = []   # Lista de IDs de ingredientes


class ProductoRead(ProductoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    categorias: List[CategoriaRead] = []
    ingredientes: List[IngredienteRead] = []


class ProductoUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[Decimal] = None
    imagenes_url: Optional[List[str]] = None
    stock_cantidad: Optional[int] = None
    disponible: Optional[bool] = None
    categoria_ids: Optional[List[int]] = None
    ingrediente_ids: Optional[List[int]] = None


# ══════════════════════════════════════
# SCHEMAS DE PEDIDOS
# ══════════════════════════════════════

class DetallePedidoCreate(SQLModel):
    producto_id: int
    cantidad: int = 1


class PedidoCreate(SQLModel):
    direccion_entrega_id: Optional[int] = None
    forma_pago_id: int = 1
    notas: Optional[str] = None
    items: List[DetallePedidoCreate]


class DetallePedidoRead(SQLModel):
    id: int
    producto_id: int
    producto_nombre: str
    precio_unitario: Decimal
    cantidad: int
    subtotal: Decimal


class PedidoRead(SQLModel):
    id: int
    usuario_id: int
    total: Decimal
    estado: str
    forma_pago: str
    notas: Optional[str] = None
    created_at: datetime
    detalles: List[DetallePedidoRead] = []


class HistorialEstadoRead(SQLModel):
    id: int
    estado_anterior: Optional[str] = None
    estado_nuevo: str
    cambiado_por_id: int
    created_at: datetime


class PedidoDetailRead(PedidoRead):
    historial: List[HistorialEstadoRead] = []


class EstadoUpdate(SQLModel):
    nuevo_estado: str


# ══════════════════════════════════════
# SCHEMAS DE AUTENTICACIÓN
# ══════════════════════════════════════

class RegisterRequest(SQLModel):
    email: str
    password: str
    nombre: str
    apellido: str
    telefono: Optional[str] = None


class LoginRequest(SQLModel):
    email: str
    password: str


class UserResponse(SQLModel):
    id: int
    email: str
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    activo: bool
    roles: List[str] = []


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ══════════════════════════════════════
# SCHEMAS DE PEDIDO (estados / formas de pago)
# ══════════════════════════════════════

class EstadoPedidoRead(SQLModel):
    id: int
    codigo: str
    nombre: str
    orden: int


class FormaPagoRead(SQLModel):
    id: int
    nombre: str
    codigo: str


# ══════════════════════════════════════
# SCHEMAS DE DIRECCIÓN DE ENTREGA
# ══════════════════════════════════════

class DireccionBase(SQLModel):
    alias: str = "Principal"
    calle: str
    numero: str
    ciudad: str
    provincia: str
    codigo_postal: Optional[str] = None
    referencia: Optional[str] = None


class DireccionCreate(DireccionBase):
    pass


class DireccionRead(DireccionBase):
    id: int
    es_principal: bool
    created_at: datetime


class DireccionUpdate(SQLModel):
    alias: Optional[str] = None
    calle: Optional[str] = None
    numero: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    referencia: Optional[str] = None

