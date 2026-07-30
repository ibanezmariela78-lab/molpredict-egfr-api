"""
Endpoints de información del modelo y dataset:
  GET /api/v1/models/current
  GET /api/v1/models/metrics
  GET /api/v1/dataset/summary
"""
import json
import logging
from datetime import date
from pathlib import Path
from fastapi import APIRouter
from app.schemas.model import (
    ModelInfoResponse,
    ModelMetricsResponse,
    DatasetSummaryResponse,
    DatasetCompoundSummary,
)
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Models & Dataset"])

_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "demo_compounds.json"


@router.get(
    "/models/current",
    response_model=ModelInfoResponse,
    summary="Información del modelo QSAR actual",
)
async def get_current_model() -> ModelInfoResponse:
    """
    Devuelve el estado actual del modelo QSAR para EGFR.
    El modelo real todavía no fue entrenado ni validado.
    """
    return ModelInfoResponse(
        name="QSAR Ensemble EGFR",
        version=settings.MODEL_VERSION,
        status="demo",
        task="regression",
        target="EGFR",
        endpoint="pIC50",
        trained=False,
        validated=False,
        message="El modelo QSAR real todavía no fue entrenado.",
    )


@router.get(
    "/models/metrics",
    response_model=ModelMetricsResponse,
    summary="Métricas del modelo QSAR",
)
async def get_model_metrics() -> ModelMetricsResponse:
    """
    Las métricas de rendimiento no están disponibles hasta que el modelo sea entrenado
    y validado. No se inventan métricas.
    """
    return ModelMetricsResponse(
        available=False,
        metrics=None,
        message=(
            "Las métricas estarán disponibles después del entrenamiento "
            "y validación del modelo."
        ),
    )


@router.get(
    "/dataset/summary",
    response_model=DatasetSummaryResponse,
    summary="Resumen del dataset demostrativo local",
)
async def get_dataset_summary() -> DatasetSummaryResponse:
    """
    Información del dataset demostrativo local.
    No se afirma que los datos provienen de ChEMBL ni de otra fuente experimental verificada.
    """
    compounds = []
    if _DATA_PATH.exists():
        with open(_DATA_PATH, encoding="utf-8") as f:
            raw = json.load(f)
        for entry in raw:
            compounds.append(
                DatasetCompoundSummary(
                    id=entry.get("id", ""),
                    name=entry.get("name", ""),
                    data_mode=entry.get("data_mode", "demo"),
                )
            )

    return DatasetSummaryResponse(
        total_compounds=len(compounds),
        compounds=compounds,
        data_mode="demo",
        source="Dataset demostrativo local — valores ilustrativos, no verificados experimentalmente",
        generation_date="2025-01-01",
        disclaimer=(
            "Este dataset es demostrativo. Los valores de pIC50 son ilustrativos "
            "y no provienen de una fuente experimental verificada como ChEMBL."
        ),
    )
