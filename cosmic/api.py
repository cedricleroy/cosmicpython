from fastapi import FastAPI, APIRouter, HTTPException, status

from cosmic import repository, models, services


router = APIRouter()


@router.post("/allocate", status_code=status.HTTP_201_CREATED)
def allocate(orderline: models.OrderLine):
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line = models.OrderLine(**orderline.dict())
    try:
        batchref = services.allocate(line, repo, session)
    except (models.OutOfStock, services.InvalidSku) as e:
        return HTTPException(status_code=400, detail={"message": str(e)})
    return {"batchref": batchref}


def create_app() -> FastAPI:

    app = FastAPI()

    app.include_router(router)

    return app
