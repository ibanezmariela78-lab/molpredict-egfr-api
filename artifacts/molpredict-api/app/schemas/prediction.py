"""
Esquemas Pydantic para endpoints de predicción EGFR.
"""
from typing import Any
from pydantic import BaseModel, Field, field_validator
from app.core.config import settings


class PredictionInput(BaseModel):
    smiles: str = Field(
        ...,
        description="Cadena SMILES de la molécula a evaluar.",
        examples=["COc1ccc2ncnc(Nc3ccc(F)c(Cl)c3)c2c1"],
    )

    @field_validator("smiles")
    @classmethod
    def validate_smiles_length(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El SMILES no puede estar vacío.")
        if len(v) > settings.MAX_SMILES_LENGTH:
            raise ValueError(
                f"El SMILES tiene {len(v)} caracteres; el límite es {settings.MAX_SMILES_LENGTH}."
            )
        return v


class ApplicabilityDomain(BaseModel):
    inside_domain: bool
    maximum_similarity: float
    confidence: str
    method: str = "demo"


class PredictionResponse(BaseModel):
    canonical_smiles: str
    pic50_prediction: float
    ic50_nm_prediction: float
    activity_label: str
    confidence: str
    prediction_mode: str = "demo"
    scientifically_validated: bool = False
    model_version: str
    descriptors: dict[str, Any]
    applicability_domain: ApplicabilityDomain
    favorable_factors: list[str]
    unfavorable_factors: list[str]
    disclaimer: str = (
        "Predicción demostrativa no validada científicamente. "
        "No reemplaza ensayos químicos, biológicos, toxicológicos, preclínicos ni clínicos."
    )
