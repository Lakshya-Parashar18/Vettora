from fastapi import APIRouter
from app.db.mongodb import check_db_health
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def get_health():
    db_status = check_db_health()
    return HealthResponse(status="ok", service="vettora-api", database=db_status)

