from typing import List

import pytest

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


def test_commits():
    line = models.OrderLine(sku="OMINOUS-MIRROR", quantity=10, orderid=1)
    batch = models.Batch(reference="b1", sku="OMINOUS-MIRROR", quantity=100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True


def test_returns_allocation():
    line = models.OrderLine(sku="COMPLICATED-LAMP", quantity=10, orderid=1)
    batch = models.Batch(reference="b1", sku="COMPLICATED-LAMP", quantity=100, eta=None)
    repo = FakeRepository([batch])
    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    line = models.OrderLine(sku="NONEXISTENTSKU", quantity=10, orderid=1)
    batch = models.Batch(reference="b1", sku="AREALSKU", quantity=100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())
