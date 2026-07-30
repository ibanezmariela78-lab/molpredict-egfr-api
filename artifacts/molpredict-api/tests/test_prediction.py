"""
Tests para la predicción demostrativa de actividad frente a EGFR.
"""
import math
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio

ETHANOL = "CCO"
GEFITINIB = "COc1cc2c(Nc3ccc(F)c(Cl)c3)ncnc2cc1OCCCN1CCOCC1"


async def test_prediction_ok(client: AsyncClient):
    """El endpoint de predicción debe responder 200."""
    response = await client.post(
        "/api/v1/predictions/egfr", json={"smiles": ETHANOL}
    )
    assert response.status_code == 200


async def test_prediction_required_fields(client: AsyncClient):
    """La respuesta debe contener todos los campos requeridos."""
    response = await client.post(
        "/api/v1/predictions/egfr", json={"smiles": ETHANOL}
    )
    data = response.json()
    required = [
        "canonical_smiles",
        "pic50_prediction",
        "ic50_nm_prediction",
        "activity_label",
        "confidence",
        "prediction_mode",
        "scientifically_validated",
        "model_version",
        "descriptors",
        "applicability_domain",
        "favorable_factors",
        "unfavorable_factors",
        "disclaimer",
    ]
    for field in required:
        assert field in data, f"Campo faltante: {field}"


async def test_prediction_mode_demo(client: AsyncClient):
    """La predicción siempre debe indicar prediction_mode='demo'."""
    response = await client.post(
        "/api/v1/predictions/egfr", json={"smiles": ETHANOL}
    )
    data = response.json()
    assert data["prediction_mode"] == "demo"
    assert data["scientifically_validated"] is False


async def test_prediction_reproducible(client: AsyncClient):
    """La predicción debe ser determinista (mismo resultado en dos llamadas)."""
    r1 = await client.post("/api/v1/predictions/egfr", json={"smiles": ETHANOL})
    r2 = await client.post("/api/v1/predictions/egfr", json={"smiles": ETHANOL})
    d1 = r1.json()
    d2 = r2.json()
    assert d1["pic50_prediction"] == d2["pic50_prediction"]
    assert d1["ic50_nm_prediction"] == d2["ic50_nm_prediction"]


async def test_prediction_pic50_ic50_consistency(client: AsyncClient):
    """La relación pIC50 ↔ IC50(nM) debe ser matemáticamente consistente.

    IC50 (nM) = 10^(9 - pIC50)
    """
    response = await client.post(
        "/api/v1/predictions/egfr", json={"smiles": ETHANOL}
    )
    data = response.json()
    pic50 = data["pic50_prediction"]
    ic50_nm = data["ic50_nm_prediction"]
    expected_ic50 = 10 ** (9.0 - pic50)
    # Tolerancia del 1% para el redondeo
    assert abs(ic50_nm - expected_ic50) / expected_ic50 < 0.01, (
        f"Inconsistencia: pIC50={pic50} → IC50 esperado={expected_ic50:.2f} nM, "
        f"obtenido={ic50_nm} nM"
    )


async def test_prediction_invalid_smiles(client: AsyncClient):
    """Una predicción con SMILES inválido debe devolver error."""
    response = await client.post(
        "/api/v1/predictions/egfr", json={"smiles": "esto-no-es-un-smiles"}
    )
    assert response.status_code == 422


async def test_prediction_demo_compound(client: AsyncClient):
    """Los compuestos del dataset demo deben usar sus valores predefinidos."""
    response = await client.post(
        "/api/v1/predictions/egfr", json={"smiles": GEFITINIB}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["prediction_mode"] == "demo"
    assert data["scientifically_validated"] is False
    # Gefitinib tiene pIC50 demo = 7.9 en el dataset
    assert abs(data["pic50_prediction"] - 7.9) < 0.01
