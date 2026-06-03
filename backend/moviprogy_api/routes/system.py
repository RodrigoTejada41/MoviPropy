from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class SystemInfo(BaseModel):
    name: str
    mode: str
    offline_first: bool


@router.get("/info", response_model=SystemInfo)
def system_info() -> SystemInfo:
    return SystemInfo(name="MoviProgy", mode="api", offline_first=True)
