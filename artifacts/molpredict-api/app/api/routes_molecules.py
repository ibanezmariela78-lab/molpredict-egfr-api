"""
Endpoints de moléculas:
  POST /api/v1/molecules/validate
  POST /api/v1/molecules/descriptors
  POST /api/v1/molecules/render
"""
import logging
from fastapi import APIRouter
from app.schemas.molecule import (
    SMILESInput,
    ValidateResponse,
    DescriptorsResponse,
    RenderInput,
    RenderResponse,
)
from app.services.chemistry_service import validate_smiles
from app.services.descriptor_service import calculate_descriptors
from app.services.rendering_service import render_molecule_svg

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/molecules", tags=["Molecules"])


@router.post(
    "/validate",
    response_model=ValidateResponse,
    summary="Validar y canonicalizar un SMILES",
)
async def validate_molecule(body: SMILESInput) -> ValidateResponse:
    """
    Valida la estructura química mediante RDKit.
    Devuelve SMILES canónico, fórmula molecular y conteo de átomos.
    """
    result = validate_smiles(body.smiles)
    return ValidateResponse(**result)


@router.post(
    "/descriptors",
    response_model=DescriptorsResponse,
    summary="Calcular descriptores fisicoquímicos (RDKit real)",
)
async def get_descriptors(body: SMILESInput) -> DescriptorsResponse:
    """
    Calcula descriptores fisicoquímicos reales con RDKit:
    peso molecular, LogP, TPSA, donantes/aceptores de H, enlaces rotables,
    anillos aromáticos, fracción CSP3, carga formal y evaluación de Lipinski.
    """
    result = calculate_descriptors(body.smiles)
    return DescriptorsResponse(**result)


@router.post(
    "/render",
    response_model=RenderResponse,
    summary="Generar estructura molecular 2D en SVG",
)
async def render_molecule(body: RenderInput) -> RenderResponse:
    """
    Genera una representación 2D en formato SVG usando RDKit.
    La imagen incluye enlaces químicos, etiquetas de heteroátomos y fondo blanco.
    """
    result = render_molecule_svg(body.smiles, width=body.width, height=body.height)
    return RenderResponse(**result)
