"""
Tests para:
  - SMILES válido
  - SMILES inválido
  - Canonicalización
  - Fórmula molecular
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio

VALID_SMILES_ETHANOL = "CCO"
VALID_SMILES_GEFITINIB = "COc1ccc2ncnc(Nc3ccc(F)c(Cl)c3)c2c1"
INVALID_SMILES = "esto-no-es-un-smiles"


async def test_validate_smiles_valid(client: AsyncClient):
    """Un SMILES simple válido debe ser aceptado."""
    response = await client.post(
        "/api/v1/molecules/validate", json={"smiles": VALID_SMILES_ETHANOL}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True


async def test_validate_smiles_invalid(client: AsyncClient):
    """Un SMILES inválido debe devolver HTTP 422."""
    response = await client.post(
        "/api/v1/molecules/validate", json={"smiles": INVALID_SMILES}
    )
    assert response.status_code == 422


async def test_validate_canonical_smiles(client: AsyncClient):
    """La canonicalización debe devolver un SMILES consistente."""
    response = await client.post(
        "/api/v1/molecules/validate", json={"smiles": VALID_SMILES_ETHANOL}
    )
    assert response.status_code == 200
    data = response.json()
    canonical = data["canonical_smiles"]
    assert len(canonical) > 0

    # Enviar el mismo SMILES canónico y debe devolver el mismo resultado
    response2 = await client.post(
        "/api/v1/molecules/validate", json={"smiles": canonical}
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["canonical_smiles"] == canonical


async def test_validate_molecular_formula_ethanol(client: AsyncClient):
    """La fórmula molecular del etanol (CCO) debe ser C2H6O."""
    response = await client.post(
        "/api/v1/molecules/validate", json={"smiles": VALID_SMILES_ETHANOL}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["molecular_formula"] == "C2H6O"


async def test_validate_molecular_formula_case(client: AsyncClient):
    """La fórmula molecular debe tener el formato químico correcto (Cl, no CL)."""
    response = await client.post(
        "/api/v1/molecules/validate", json={"smiles": VALID_SMILES_GEFITINIB}
    )
    assert response.status_code == 200
    data = response.json()
    formula = data["molecular_formula"]
    # No debe aparecer 'CL' en mayúsculas (debe ser 'Cl')
    assert "CL" not in formula
    assert len(formula) > 0


async def test_validate_atom_count_ethanol(client: AsyncClient):
    """El etanol (CCO) tiene 2C + 1O + 6H = 9 átomos totales."""
    response = await client.post(
        "/api/v1/molecules/validate", json={"smiles": VALID_SMILES_ETHANOL}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["heavy_atom_count"] == 3   # 2C + 1O
    assert data["atom_count"] == 9         # 2C + 1O + 6H


async def test_validate_empty_smiles(client: AsyncClient):
    """Un SMILES vacío debe devolver error de validación."""
    response = await client.post(
        "/api/v1/molecules/validate", json={"smiles": "   "}
    )
    assert response.status_code == 422


async def test_validate_smiles_too_long(client: AsyncClient):
    """Un SMILES excesivamente largo debe ser rechazado."""
    long_smiles = "C" * 1500
    response = await client.post(
        "/api/v1/molecules/validate", json={"smiles": long_smiles}
    )
    assert response.status_code == 422
