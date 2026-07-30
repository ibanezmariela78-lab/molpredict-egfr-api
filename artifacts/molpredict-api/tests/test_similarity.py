"""
Tests para la búsqueda por similitud molecular.
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio

GEFITINIB = "COc1cc2c(Nc3ccc(F)c(Cl)c3)ncnc2cc1OCCCN1CCOCC1"
ETHANOL = "CCO"


async def test_similarity_ok(client: AsyncClient):
    """El endpoint de similitud debe responder 200."""
    response = await client.post(
        "/api/v1/similarity/search", json={"smiles": GEFITINIB, "limit": 3}
    )
    assert response.status_code == 200


async def test_similarity_returns_results(client: AsyncClient):
    """Debe devolver resultados para un compuesto EGFR conocido."""
    response = await client.post(
        "/api/v1/similarity/search", json={"smiles": GEFITINIB, "limit": 5}
    )
    data = response.json()
    assert len(data["results"]) > 0


async def test_similarity_sorted_desc(client: AsyncClient):
    """Los resultados deben estar ordenados de mayor a menor similitud."""
    response = await client.post(
        "/api/v1/similarity/search", json={"smiles": GEFITINIB, "limit": 5}
    )
    data = response.json()
    similarities = [r["similarity"] for r in data["results"]]
    assert similarities == sorted(similarities, reverse=True), (
        "Los resultados no están ordenados de mayor a menor similitud."
    )


async def test_similarity_result_fields(client: AsyncClient):
    """Cada resultado debe incluir los campos requeridos."""
    response = await client.post(
        "/api/v1/similarity/search", json={"smiles": GEFITINIB, "limit": 3}
    )
    data = response.json()
    for result in data["results"]:
        assert "name" in result
        assert "canonical_smiles" in result
        assert "similarity" in result
        assert "experimental_pic50_demo" in result
        assert "data_mode" in result
        assert "molecular_formula" in result
        assert 0.0 <= result["similarity"] <= 1.0


async def test_similarity_limit(client: AsyncClient):
    """El parámetro limit debe respetarse."""
    response = await client.post(
        "/api/v1/similarity/search", json={"smiles": GEFITINIB, "limit": 2}
    )
    data = response.json()
    assert len(data["results"]) <= 2


async def test_similarity_model_metrics_unavailable(client: AsyncClient):
    """Las métricas del modelo deben indicar que no están disponibles."""
    response = await client.get("/api/v1/models/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is False
    assert data["metrics"] is None


async def test_similarity_dataset_summary(client: AsyncClient):
    """El resumen del dataset debe incluir los 5 compuestos demo."""
    response = await client.get("/api/v1/dataset/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_compounds"] == 5
    names = [c["name"] for c in data["compounds"]]
    assert "Gefitinib" in names
    assert "Erlotinib" in names
    assert "Lapatinib" in names
    assert "Osimertinib" in names
    assert "Afatinib" in names
