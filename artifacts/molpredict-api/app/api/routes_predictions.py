"""
Endpoint de predicción EGFR:
  POST /api/v1/predictions/egfr

ADVERTENCIA: Predicción demostrativa. No está basada en un modelo QSAR real.
"""
import logging
from fastapi import APIRouter
from app.schemas.prediction import PredictionInput, PredictionResponse
from app.services.prediction_service import predict_egfr

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post(
    "/egfr",
    response_model=PredictionResponse,
    summary="Predicción demostrativa de actividad frente a EGFR [DEMO]",
    description=(
        "**⚠️ DEMO:** Esta predicción NO está basada en un modelo QSAR entrenado. "
        "Los valores de pIC50 e IC50 son demostrativos. "
        "`scientifically_validated = false` siempre. "
        "No reemplaza ensayos experimentales."
    ),
)
async def predict_egfr_activity(body: PredictionInput) -> PredictionResponse:
    """
    Flujo:
    1. Valida y canonicaliza el SMILES
    2. Calcula descriptores fisicoquímicos (real, RDKit)
    3. Calcula Morgan Fingerprint (real, RDKit)
    4. Devuelve predicción demostrativa determinista

    prediction_mode = "demo" | scientifically_validated = False
    """
    result = predict_egfr(body.smiles)
    return PredictionResponse(**result)
