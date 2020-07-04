import abc
from typing import List

from cosmic import models, db


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: models.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference: str) -> models.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch: models.Batch):
        self.session.add(db.Batch(**batch.dict()))

    def get(self, reference: str) -> models.Batch:
        batch = self.session.query(db.Batch).filter_by(reference=reference).one()
        return models.Batch.from_orm(batch)

    def list(self) -> List[models.Batch]:
        return self.session.query(db.Batch).all()
