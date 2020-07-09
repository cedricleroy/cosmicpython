from cosmic import models, repository


def test_repository_can_save_a_batch(session) -> None:
    batch = models.Batch(reference="mybatchreference", sku="BLUE-VASE", quantity=20)
    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)
    session.commit()
    rows = list(session.execute('SELECT reference, sku, quantity, eta FROM "batches"'))
    assert rows == [("mybatchreference", "BLUE-VASE", 20, None)]


def test_repository_can_retrieve_a_batch(session) -> None:
    session.execute(
        "INSERT INTO batches (reference, sku, quantity, eta)"
        ' VALUES ("batch1", "GENERIC-SOFA", 100, null)'
    )
    repo = repository.SqlAlchemyRepository(session)
    batch = repo.get("batch1")
    assert batch == models.Batch(reference="batch1", sku="GENERIC-SOFA", quantity=100)
