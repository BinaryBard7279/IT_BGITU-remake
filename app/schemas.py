from pydantic import BaseModel

class HealthCheck(BaseModel):
    db_status: bool
    math_result: int | None = None
    error: str | None = None
