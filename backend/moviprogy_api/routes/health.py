from fastapi import APIRouter
from fastapi import HTTPException, status

from moviprogy_api.database import check_database


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def readiness_check() -> dict[str, str]:
    database = check_database()
    if not database.configured:
        return {"status": "ok", "database": "not_configured"}

    if not database.available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "database": "unavailable"},
        )

    return {"status": "ok", "database": "available"}
