""" Database models

NOTE: Rational for not using `Table` and mapper: The SQLAlchemy mapping is
adding an `_sa_instance_state` to the model instance. It fails when strictly
immutable (e.g. @dataclass(frozen=True)), and leads to weird behavior with
Pydantic. Pydantic also offer options to plug to ORMs, so using SQLAlchemy
"declarative" syntax is not that bad as long as independant from the core model.
One would argue that it is not super DRY though.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)


class OrderLine(Base):
    __tablename__ = "orderlines"
    id = Column(Integer, primary_key=True)
    sku = Column(String(250))
    qty = Column(String(250))
    order_id = Column(Integer, ForeignKey("orders.id"))
    order = relationship(Order)
    batch_id = Column(Integer, ForeignKey("batches.id"))


class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True)
    reference = Column(String(250))
    quantity = Column(Integer)
    sku = Column(String(250))
    order_lines = relationship(OrderLine, collection_class=set)
    eta = Column(Date)
