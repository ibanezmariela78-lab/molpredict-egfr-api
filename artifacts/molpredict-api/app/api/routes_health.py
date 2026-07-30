"""
Endpoint de salud: GET /health
"""
from fastapi import APIRouter
from app.core.config import settings
from app.services.chemistry_service import check_rdkit

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Estado del servicio")
async def health_check() -> dict:
    """
    Verifica que el servicio está activo y que RDKit está disponible.
    """
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "environment": settings.APP_ENV,
        "demo_mode": settings.DEMO_MODE,
        "rdkit_available": check_rdkit(),
        "version": settings.VERSION,
    }
