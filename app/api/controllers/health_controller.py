from fastapi import APIRouter
from app.api.services.health_service import HealthService

router = APIRouter()
health_service = HealthService()

@router.get("/health")
def get_health():
    return health_service.get_health_info()
