import datetime as dt

import pytest

from cosmic.models import Batch, OrderLine, BatchError, allocate


@pytest.fixture()
def batch():
    batch_data = {
        'reference': 'mybatchreference',
        'sku': 'BLUE-VASE',
        'quantity': 20
    }
    return Batch(**batch_data)


def test_allocate_order_line_to_batch_reduce_qty(batch):
    order_line = OrderLine(sku='BLUE-VASE', quantity=2, orderid=1)
    # make sure we remove the order quantity from the batch
    batch.allocate(order_line)
    assert batch.quantity == 18


def test_allocate_order_line_to_batch_max_qty(batch):
    # make sure we cannot allocate if order line quantity
    # is > than batch quantity
    order_line = OrderLine(sku='BLUE-VASE', quantity=21, orderid=1)
    with pytest.raises(BatchError) as err:
        batch.allocate(order_line)
    msg = 'Order line quantity cannot be > than batch quantity'
    assert str(err.value) == msg
    # same quantity is ok though
    order_line = OrderLine(sku='BLUE-VASE', quantity=20, orderid=1)
    batch.allocate(order_line)
    assert batch.quantity == 0


def test_allocate_order_line_to_batch(batch):
    # cannot allocate the same order line multiple times
    # to the same batch
    order_line = OrderLine(sku='BLUE-VASE', quantity=2, orderid=1)
    batch.allocate(order_line)
    batch.allocate(order_line)
    assert batch.quantity == 18


def test_allocate_order_line_wrong_sku(batch):
    order_line = OrderLine(sku='WHITE-VASE', quantity=20, orderid=1)
    with pytest.raises(ValueError) as err:
        batch.allocate(order_line)
    msg = 'sku should match: expected BLUE-VASE, got WHITE-VASE'
    assert str(err.value) == msg


def test_deallocate_order_line(batch):
    order_line = OrderLine(sku='BLUE-VASE', quantity=2, orderid=1)
    batch.allocate(order_line)
    batch.deallocate(order_line)
    assert batch.quantity == 20


def test_deallocate_order_line_does_not_exist(batch):
    order_line = OrderLine(sku='BLUE-VASE', quantity=2, orderid=1)
    order_line2 = OrderLine(sku='WHITE-VASE', quantity=3, orderid=1)
    batch.allocate(order_line)
    with pytest.raises(BatchError) as err:
        batch.deallocate(order_line2)
    msg = 'Order line {} has is not allocated'.format(order_line2)
    assert str(err.value) == msg


def test_get_from_stock_when_possible():
    # if we have a batch in stock, and another being shipped, let's
    # prioritize the one in stock
    tomorrow = dt.date.today() + dt.timedelta(days=1)
    batch_in_stock = Batch(
        reference='batch-in-stock-reference',
        sku='BLUE-VASE',
        quantity=20
    )
    batch_being_shipped = Batch(
        reference='batch-being-shipped-reference',
        sku='BLUE-VASE',
        quantity=10,
        eta=tomorrow
    )
    order_line = OrderLine(sku='BLUE-VASE', quantity=2, orderid=1)
    allocate(order_line, [batch_being_shipped, batch_in_stock])
    assert order_line in batch_in_stock.order_lines
    assert batch_in_stock.quantity == 18


def test_get_from_stock_with_smallest_eta():
    tomorrow = dt.date.today() + dt.timedelta(days=1)
    batch1 = Batch(
        reference='batch1',
        sku='BLUE-VASE',
        quantity=10,
        eta=tomorrow
    )
    batch2 = Batch(
        reference='batch2',
        sku='BLUE-VASE',
        quantity=10,
        eta=tomorrow + dt.timedelta(days=1)
    )
    order_line = OrderLine(sku='BLUE-VASE', quantity=2, orderid=1)
    allocate(order_line, [batch2, batch1])
    assert batch1.quantity == 8
    assert batch2.quantity == 10


def test_get_from_stock_ignore_batch_with_bad_qty():
    # when the batch are sorted by eta, we should also
    # ignore those where the quantity does not match the
    # order line
    tomorrow = dt.date.today() + dt.timedelta(days=1)
    batch1 = Batch(
        reference='batch1',
        sku='BLUE-VASE',
        quantity=10,
        eta=tomorrow
    )
    batch2 = Batch(
        reference='batch2',
        sku='BLUE-VASE',
        quantity=20,
        eta=tomorrow + dt.timedelta(days=1)
    )
    order_line = OrderLine(sku='BLUE-VASE', quantity=12, orderid=1)
    allocate(order_line, [batch1, batch2])
    assert batch1.quantity == 10
    assert batch2.quantity == 8


def test_get_from_stock_return_allocated_reference():
    batch = Batch(
        reference='batch1',
        sku='BLUE-VASE',
        quantity=10
    )
    order_line = OrderLine(sku='BLUE-VASE', quantity=2, orderid=1)
    res = allocate(order_line, [batch])
    assert res == batch.reference


def test_get_from_stock_no_allocation():
    batch = Batch(
        reference='batch1',
        sku='BLUE-VASE',
        quantity=10
    )
    order_line = OrderLine(sku='BLUE-VASE', quantity=12, orderid=1)
    res = allocate(order_line, [batch])
    assert batch.quantity == 10
    assert res is None

