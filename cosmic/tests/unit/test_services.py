from typing import List

from cosmic import models, services


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


class FakeRepository:
    def __init__(self, batches: List[models.Batch]) -> None:
        self._batches = set(batches)

    def add(self, batch: models.Batch):
        self._batches.add(batch)

    def get(self, reference: str) -> models.Batch:
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> List[models.Batch]:
        return list(self._batches)


def test_returns_allocation():
    line = models.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = models.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"