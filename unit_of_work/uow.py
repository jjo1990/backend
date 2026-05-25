from sqlmodel import Session
from repositories.producto_repository import ProductoRepository
from repositories.categoria_repository import CategoriaRepository
from repositories.ingrediente_repository import IngredienteRepository
from repositories.pedido_repository import PedidoRepository

class UnitOfWork:
    def __init__(self, session: Session):
        self.session = session
        self.productos = ProductoRepository(session)
        self.categorias = CategoriaRepository(session)
        self.ingredientes = IngredienteRepository(session)
        self.pedidos = PedidoRepository(session)

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
        
    def refresh(self, instance):
        self.session.refresh(instance)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        if exc_type is not None:
            self.rollback()
