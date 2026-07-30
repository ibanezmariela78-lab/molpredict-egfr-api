"""
Esquemas Pydantic para endpoints de moléculas.
"""
from pydantic import BaseModel, Field, field_validator
from app.core.config import settings


class SMILESInput(BaseModel):
    smiles: str = Field(
        ...,
        description="Cadena SMILES que representa la estructura molecular.",
        examples=["CCO", "COc1ccc2ncnc(Nc3ccc(F)c(Cl)c3)c2c1"],
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


class ValidateResponse(BaseModel):
    valid: bool
    input_smiles: str
    canonical_smiles: str
    molecular_formula: str
    atom_count: int
    heavy_atom_count: int
    message: str


class LipinskiCriterion(BaseModel):
    name: str
    value: float
    threshold: str
    passes: bool


class LipinskiEvaluation(BaseModel):
    criteria: list[LipinskiCriterion]
    passed_count: int
    total_count: int
    summary: str


class DescriptorsResponse(BaseModel):
    canonical_smiles: str
    molecular_formula: str
    molecular_weight: float
    logp: float
    tpsa: float
    h_bond_donors: int
    h_bond_acceptors: int
    rotatable_bonds: int
    aromatic_rings: int
    fraction_csp3: float
    formal_charge: int
    atom_count: int
    heavy_atom_count: int
    ring_count: int
    lipinski_violations: int
    lipinski: LipinskiEvaluation
    disclaimer: str = (
        "Los criterios de Lipinski son orientativos para la permeabilidad oral; "
        "no son un predictor absoluto de biodisponibilidad."
    )


class RenderInput(BaseModel):
    smiles: str = Field(
        ...,
        description="Cadena SMILES de la molécula a renderizar.",
    )
    width: int = Field(500, ge=50, le=2000, description="Ancho en píxeles.")
    height: int = Field(350, ge=50, le=2000, description="Alto en píxeles.")

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


class RenderResponse(BaseModel):
    canonical_smiles: str
    format: str = "svg"
    width: int
    height: int
    svg: str
