"""
Tests para el endpoint GET /health
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_health_ok(client: AsyncClient):
    """El endpoint /health debe devolver status ok."""
    response = await client.get("/health")
    assert response.status_code == 200


async def test_health_fields(client: AsyncClient):
    """El endpoint /health debe incluir todos los campos requeridos."""
    response = await client.get("/health")
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data
    assert "environment" in data
    assert "demo_mode" in data
    assert "rdkit_available" in data
    assert "version" in data


async def test_health_rdkit_available(client: AsyncClient):
    """RDKit debe estar disponible en el entorno."""
    response = await client.get("/health")
    data = response.json()
    assert data["rdkit_available"] is True, "RDKit no está disponible — instalar rdkit."


async def test_health_service_name(client: AsyncClient):
    """El nombre del servicio debe ser el correcto."""
    response = await client.get("/health")
    data = response.json()
    assert data["service"] == "molpredict-egfr-api"
