""" Domain modeling exercise (aka Business Logic) """
import datetime as dt
from typing import Set, List, Optional

from pydantic import BaseModel, Field


class OrderLine(BaseModel):
    sku: str
    quantity: int = Field(int, ge=0)
    orderid: int = Field(int, ge=0)

    def __hash__(self) -> int:
        return hash((type(self),) + tuple(self.__dict__.values()))

    # NOTE: This is a `value` object, identified by the data it holds.


class BatchError(Exception):
    pass


class Batch(BaseModel):
    reference: str
    sku: str
    quantity: int = Field(int, ge=0)
    order_lines: Set[OrderLine] = set()
    eta: Optional[dt.date]

    class Config:
        orm_mode = True

    def allocate(self, order_line: OrderLine) -> None:
        if order_line in self.order_lines:
            return
        if order_line.sku != self.sku:
            msg = "sku should match: expected {}, got {}"
            msg = msg.format(self.sku, order_line.sku)
            raise ValueError(msg)
        if order_line.quantity > self.quantity:
            msg = "Order line quantity cannot be > than batch quantity"
            raise BatchError(msg)
        self.quantity -= order_line.quantity
        self.order_lines.add(order_line)

    def deallocate(self, order_line: OrderLine) -> None:
        if order_line not in self.order_lines:
            msg = "Order line {} has is not allocated".format(order_line)
            raise BatchError(msg)
        self.quantity += order_line.quantity
        self.order_lines.remove(order_line)

    def __gt__(self, obj: "Batch") -> bool:
        if self.eta is None:
            return False
        elif obj.eta is None:
            return True
        return self.eta > obj.eta

    def __hash__(self) -> int:
        return hash((type(self), self.reference, self.quantity, self.eta))

    # NOTE: This is an `entity` object - long-lived identity where some
    # of the data it holds can change.


class OutOfStock(Exception):
    pass


def allocate(order_line: OrderLine, batches: List[Batch]) -> str:
    """ Allocate an order line to a list of batches

    NOTE: Would like to see this in another module (services?)
    """
    sorted_batches = sorted(batches)
    valid_batches = [b for b in sorted_batches if order_line.quantity <= b.quantity]
    if valid_batches:
        valid_batches[0].allocate(order_line)
        return valid_batches[0].reference
    raise OutOfStock(f"Out of stock for sku {order_line.sku}")
