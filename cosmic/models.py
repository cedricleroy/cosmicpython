from typing import Set

from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class OrderLine(BaseModel):
    sku: str
    quantity: int = Field(int, ge=0)
    orderid: int = Field(int, ge=0)

    # NOTE: Using a dataclass here to get a hash automatically
    # https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass


class BatchError(Exception):
    pass


class Batch(BaseModel):
    reference: str
    sku: str
    quantity: int = Field(int, ge=0)
    order_lines: Set[OrderLine] = set()

    def allocate(self, order_line: OrderLine):
        if order_line in self.order_lines:
            return
        if order_line.sku != self.sku:
            msg = 'sku should match: expected {}, got {}'
            msg = msg.format(self.sku, order_line.sku)
            raise ValueError(msg)
        if order_line.quantity > self.quantity:
            msg = 'Order line quantity cannot be > than batch quantity'
            raise BatchError(msg)
        self.quantity -= order_line.quantity  # type: ignore
        self.order_lines.add(order_line)

