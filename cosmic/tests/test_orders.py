import pytest

from cosmic.models import Batch, OrderLine, BatchError


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

