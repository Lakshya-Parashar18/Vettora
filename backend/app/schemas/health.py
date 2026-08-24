from typing import Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    database: Optional[str] = "connected"

