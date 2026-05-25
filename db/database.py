import os
from sqlmodel import SQLModel, create_engine, Session, select
from dotenv import load_dotenv

load_dotenv()

#confifuracion de base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:1234@localhost:5433/parcial_db"
)

# El engine es el "conector" entre Python y PostgreSQL.

engine = create_engine(DATABASE_URL, echo=True)

#creacion de tablas
def create_db_and_tables():
    """Crea todas las tablas en la DB si no existen todavía."""
    SQLModel.metadata.create_all(engine)
    seed_data()


def get_session():
    """
    Generador que crea una sesión de DB por cada request.
    FastAPI llama esto automáticamente gracias a Depends().
    El 'with' garantiza que la sesión se cierra aunque haya un error.
    """
    with Session(engine) as session:
        yield session


def seed_data():
    """Crea datos iniciales obligatorios: roles, estados de pedido, formas de pago y admin"""
    from datetime import datetime
    from models.models import Rol, EstadoPedido, FormaPago, Usuario, UsuarioRol
    import bcrypt

    with Session(engine) as session:
        roles_exist = session.exec(select(Rol).limit(1)).first()
        if not roles_exist:
            roles = [
                Rol(codigo="ADMIN", nombre="Administrador", descripcion="CRUD completo de todo el sistema"),
                Rol(codigo="STOCK", nombre="Gestor de Stock", descripcion="Leer productos, actualizar stock y disponibilidad"),
                Rol(codigo="PEDIDOS", nombre="Gestor de Pedidos", descripcion="Ver y avanzar estados de pedidos"),
                Rol(codigo="CLIENT", nombre="Cliente", descripcion="Catálogo, carrito, pedidos propios"),
            ]
            for r in roles:
                session.add(r)
            session.commit()

        estados_exist = session.exec(select(EstadoPedido).limit(1)).first()
        if not estados_exist:
            estados = [
                EstadoPedido(codigo="PENDIENTE", nombre="Pendiente", orden=1),
                EstadoPedido(codigo="CONFIRMADO", nombre="Confirmado", orden=2),
                EstadoPedido(codigo="EN_PREP", nombre="En Preparación", orden=3),
                EstadoPedido(codigo="EN_CAMINO", nombre="En Camino", orden=4),
                EstadoPedido(codigo="ENTREGADO", nombre="Entregado", orden=5),
                EstadoPedido(codigo="CANCELADO", nombre="Cancelado", orden=6),
            ]
            for e in estados:
                session.add(e)
            session.commit()

        fp_exist = session.exec(select(FormaPago).limit(1)).first()
        if not fp_exist:
            formas = [
                FormaPago(nombre="Efectivo", codigo="EFECTIVO", activo=True),
                FormaPago(nombre="Tarjeta Débito", codigo="DEBITO", activo=True),
                FormaPago(nombre="Tarjeta Crédito", codigo="CREDITO", activo=True),
                FormaPago(nombre="Transferencia", codigo="TRANSFERENCIA", activo=True),
                FormaPago(nombre="Mercado Pago", codigo="MERCADOPAGO", activo=True),
            ]
            for f in formas:
                session.add(f)
            session.commit()

        admin = session.exec(select(Usuario).where(Usuario.email == "admin@admin.com")).first()
        if not admin:
            admin = Usuario(
                email="admin@admin.com",
                password_hash=bcrypt.hashpw(b"admin123", bcrypt.gensalt(12)).decode(),
                nombre="Admin",
                apellido="Sistema",
                telefono="123456789",
            )
            session.add(admin)
            session.commit()
            session.refresh(admin)

            rol_admin = session.exec(select(Rol).where(Rol.codigo == "ADMIN")).first()
            if rol_admin:
                session.add(UsuarioRol(usuario_id=admin.id, rol_id=rol_admin.id))
                session.commit()
