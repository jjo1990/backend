from typing import TypeVar, Generic, Type, Optional, List
from sqlmodel import Session, select
from models.models import SQLModel

T = TypeVar("T", bound=SQLModel)

class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def get_by_id(self, id: int) -> Optional[T]:
        return self.session.get(self.model, id)

    def get_all(self, offset: int = 0, limit: int = 100) -> List[T]:
        return self.session.exec(select(self.model).offset(offset).limit(limit)).all()

    def add(self, entity: T):
        self.session.add(entity)

    def delete(self, entity: T):
        self.session.delete(entity)
