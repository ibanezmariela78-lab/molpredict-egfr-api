"""
Esquemas Pydantic para endpoints de similitud molecular.
"""
from pydantic import BaseModel, Field, field_validator
from app.core.config import settings


class SimilarityInput(BaseModel):
    smiles: str = Field(
        ...,
        description="SMILES de la molécula de consulta.",
        examples=["CCO"],
    )
    limit: int = Field(
        5,
        ge=1,
        le=20,
        description="Número máximo de compuestos similares a devolver.",
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


class SimilarCompound(BaseModel):
    name: str
    canonical_smiles: str
    similarity: float
    experimental_pic50_demo: float
    data_mode: str
    molecular_formula: str


class SimilarityResponse(BaseModel):
    query_smiles: str
    results: list[SimilarCompound]
    method: str = "Morgan Fingerprint (radio=2, 2048 bits) + Tanimoto"
    disclaimer: str = (
        "Los valores de pIC50 son ilustrativos y no provienen de una fuente experimental verificada."
    )
