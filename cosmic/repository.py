from typing import List, Protocol

from sqlalchemy.orm.session import Session

from cosmic import models, db


class BatchRepository(Protocol):
    def add(self, batch: models.Batch) -> None:
        ...

    def get(self, reference: str) -> models.Batch:
        ...

    def list(self) -> List[models.Batch]:
        ...


class SqlAlchemyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, batch: models.Batch) -> None:
        self.session.add(db.Batch(**batch.dict()))

    def get(self, reference: str) -> models.Batch:
        batch = self.session.query(db.Batch).filter_by(reference=reference).one()
        return models.Batch.from_orm(batch)

    def list(self) -> List[models.Batch]:
        return self.session.query(db.Batch).all()
