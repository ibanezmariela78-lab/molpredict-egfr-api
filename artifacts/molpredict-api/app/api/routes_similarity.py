"""
Endpoint de similitud molecular:
  POST /api/v1/similarity/search
"""
import logging
from fastapi import APIRouter
from app.schemas.similarity import SimilarityInput, SimilarityResponse
from app.services.similarity_service import search_similar

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/similarity", tags=["Similarity"])


@router.post(
    "/search",
    response_model=SimilarityResponse,
    summary="Buscar moléculas similares usando Tanimoto (Morgan FP)",
)
async def similarity_search(body: SimilarityInput) -> SimilarityResponse:
    """
    Calcula la similitud de Tanimoto entre el SMILES dado y el dataset demostrativo.
    Usa Morgan Fingerprints (radio=2, 2048 bits).
    Los resultados se ordenan de mayor a menor similitud.
    """
    result = search_similar(body.smiles, limit=body.limit)
    return SimilarityResponse(**result)
