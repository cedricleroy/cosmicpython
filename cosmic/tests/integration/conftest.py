import time

import pytest
import requests
from requests.exceptions import ConnectionError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cosmic import db, ROOT_PATH
from cosmic.config import get_settings


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    db.Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    yield sessionmaker(bind=in_memory_db)()


@pytest.fixture
def add_stock(session):
    batches_added = set()
    skus_added = set()

    def _add_stock(lines):
        for ref, sku, qty, eta in lines:
            session.execute(
                "INSERT INTO batches (reference, sku, quantity, eta)"
                " VALUES (:ref, :sku, :qty, :eta)",
                dict(ref=ref, sku=sku, qty=qty, eta=eta),
            )
            [[batch_id]] = session.execute(
                "SELECT id FROM batches WHERE reference=:ref AND sku=:sku",
                dict(ref=ref, sku=sku),
            )
            batches_added.add(batch_id)
            skus_added.add(sku)
        session.commit()

    yield _add_stock

    for batch_id in batches_added:
        # session.execute(
        #    "DELETE FROM allocations WHERE batch_id=:batch_id", dict(batch_id=batch_id),
        # )
        session.execute(
            "DELETE FROM batches WHERE id=:batch_id", dict(batch_id=batch_id),
        )
    for sku in skus_added:
        session.execute(
            "DELETE FROM orderlines WHERE sku=:sku", dict(sku=sku),
        )
        session.commit()


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = get_settings().get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture
def restart_api():
    ROOT_PATH.touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
