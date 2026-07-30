"""
Tests para el cálculo de descriptores fisicoquímicos.
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio

ETHANOL = "CCO"


async def test_descriptors_ethanol_ok(client: AsyncClient):
    """El endpoint de descriptores debe responder 200 para un SMILES válido."""
    response = await client.post(
        "/api/v1/molecules/descriptors", json={"smiles": ETHANOL}
    )
    assert response.status_code == 200


async def test_descriptors_required_fields(client: AsyncClient):
    """La respuesta debe incluir todos los campos de descriptores."""
    response = await client.post(
        "/api/v1/molecules/descriptors", json={"smiles": ETHANOL}
    )
    data = response.json()
    required = [
        "molecular_weight",
        "logp",
        "tpsa",
        "h_bond_donors",
        "h_bond_acceptors",
        "rotatable_bonds",
        "aromatic_rings",
        "fraction_csp3",
        "formal_charge",
        "atom_count",
        "heavy_atom_count",
        "ring_count",
        "lipinski_violations",
        "lipinski",
    ]
    for field in required:
        assert field in data, f"Campo faltante: {field}"


async def test_descriptors_ethanol_molecular_weight(client: AsyncClient):
    """El peso molecular del etanol debe ser ~46.04 Da."""
    response = await client.post(
        "/api/v1/molecules/descriptors", json={"smiles": ETHANOL}
    )
    data = response.json()
    mw = data["molecular_weight"]
    assert 46.0 <= mw <= 46.1, f"Peso molecular inesperado: {mw}"


async def test_descriptors_ethanol_lipinski(client: AsyncClient):
    """El etanol debe cumplir todos los criterios de Lipinski."""
    response = await client.post(
        "/api/v1/molecules/descriptors", json={"smiles": ETHANOL}
    )
    data = response.json()
    lipinski = data["lipinski"]
    assert lipinski["total_count"] == 5
    assert lipinski["passed_count"] == 5
    assert data["lipinski_violations"] == 0


async def test_descriptors_lipinski_structure(client: AsyncClient):
    """La evaluación de Lipinski debe tener la estructura correcta."""
    response = await client.post(
        "/api/v1/molecules/descriptors", json={"smiles": ETHANOL}
    )
    data = response.json()
    lipinski = data["lipinski"]
    assert "criteria" in lipinski
    assert "passed_count" in lipinski
    assert "total_count" in lipinski
    assert "summary" in lipinski
    assert len(lipinski["criteria"]) == 5
    for criterion in lipinski["criteria"]:
        assert "name" in criterion
        assert "value" in criterion
        assert "threshold" in criterion
        assert "passes" in criterion


async def test_descriptors_svg_render(client: AsyncClient):
    """El endpoint de renderizado debe devolver un SVG válido."""
    response = await client.post(
        "/api/v1/molecules/render",
        json={"smiles": ETHANOL, "width": 300, "height": 200},
    )
    assert response.status_code == 200
    data = response.json()
    assert "svg" in data
    assert data["svg"].strip().startswith("<")
    assert "svg" in data["svg"].lower()
    assert data["format"] == "svg"


async def test_descriptors_render_invalid_smiles(client: AsyncClient):
    """El renderizado de un SMILES inválido debe devolver error."""
    response = await client.post(
        "/api/v1/molecules/render",
        json={"smiles": "esto-no-es-un-smiles", "width": 300, "height": 200},
    )
    assert response.status_code == 422
