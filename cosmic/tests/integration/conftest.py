import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cosmic import db


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    db.Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    yield sessionmaker(bind=in_memory_db)()
