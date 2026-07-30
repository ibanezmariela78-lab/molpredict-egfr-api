#!/usr/bin/env python3
"""
Script de prueba manual de la API MolPredict EGFR.
Uso: python scripts/test_api.py [base_url]

Ejemplo:
  python scripts/test_api.py http://localhost:8000
"""
import sys
import json
import httpx

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

SMILES_GEFITINIB = "COc1cc2c(Nc3ccc(F)c(Cl)c3)ncnc2cc1OCCCN1CCOCC1"
SMILES_ETHANOL = "CCO"
SMILES_INVALID = "esto-no-es-un-smiles"


def print_section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def print_result(response: httpx.Response, label: str = "") -> None:
    status_emoji = "✅" if response.status_code < 400 else "❌"
    print(f"{status_emoji} [{response.status_code}] {label}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False)[:600])
        if len(response.text) > 600:
            print("  ... [respuesta truncada]")
    except Exception:
        print(response.text[:400])


def main():
    print(f"🧪 Probando API en: {BASE_URL}")

    with httpx.Client(base_url=BASE_URL, timeout=30) as client:

        print_section("1. GET /health")
        r = client.get("/health")
        print_result(r, "Health check")

        print_section("2. POST /api/v1/molecules/validate — SMILES válido (Gefitinib)")
        r = client.post("/api/v1/molecules/validate", json={"smiles": SMILES_GEFITINIB})
        print_result(r, "Validar Gefitinib")

        print_section("3. POST /api/v1/molecules/validate — SMILES inválido")
        r = client.post("/api/v1/molecules/validate", json={"smiles": SMILES_INVALID})
        print_result(r, "SMILES inválido (esperado 422)")

        print_section("4. POST /api/v1/molecules/descriptors — Etanol")
        r = client.post("/api/v1/molecules/descriptors", json={"smiles": SMILES_ETHANOL})
        print_result(r, "Descriptores etanol")

        print_section("5. POST /api/v1/molecules/descriptors — Gefitinib")
        r = client.post("/api/v1/molecules/descriptors", json={"smiles": SMILES_GEFITINIB})
        print_result(r, "Descriptores Gefitinib")

        print_section("6. POST /api/v1/molecules/render — SVG Gefitinib")
        r = client.post(
            "/api/v1/molecules/render",
            json={"smiles": SMILES_GEFITINIB, "width": 500, "height": 350},
        )
        data = r.json()
        svg_preview = data.get("svg", "")[:100] if r.status_code == 200 else ""
        print(f"{'✅' if r.status_code == 200 else '❌'} [{r.status_code}] SVG generado: {svg_preview}...")

        print_section("7. POST /api/v1/predictions/egfr — Gefitinib [DEMO]")
        r = client.post("/api/v1/predictions/egfr", json={"smiles": SMILES_GEFITINIB})
        print_result(r, "Predicción EGFR Gefitinib")

        print_section("8. POST /api/v1/similarity/search — Gefitinib")
        r = client.post(
            "/api/v1/similarity/search",
            json={"smiles": SMILES_GEFITINIB, "limit": 3},
        )
        print_result(r, "Similitud Gefitinib")

        print_section("9. GET /api/v1/models/current")
        r = client.get("/api/v1/models/current")
        print_result(r, "Modelo actual")

        print_section("10. GET /api/v1/models/metrics")
        r = client.get("/api/v1/models/metrics")
        print_result(r, "Métricas del modelo")

        print_section("11. GET /api/v1/dataset/summary")
        r = client.get("/api/v1/dataset/summary")
        print_result(r, "Resumen del dataset")

    print("\n✅ Script de prueba completado.\n")


if __name__ == "__main__":
    main()
