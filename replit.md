# MolPredict EGFR API

Backend Python/FastAPI para validación molecular, cálculo de descriptores fisicoquímicos y predicción demostrativa de actividad frente a EGFR. El frontend externo (Lovable) consumirá esta API.

## Run & Operate

- **Python API (principal):** Workflow `MolPredict EGFR API` — `uvicorn app.main:app --host 0.0.0.0 --port 8000` (desde `artifacts/molpredict-api/`)
- **Tests:** `cd artifacts/molpredict-api && python3 -m pytest tests/ -v`
- **Prueba manual:** `python3 artifacts/molpredict-api/scripts/test_api.py http://localhost:8000`
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## Stack

- Python 3.13 + FastAPI + Uvicorn
- RDKit (validación SMILES, descriptores, SVG 2D, Morgan FP + Tanimoto)
- Pydantic v2 para validación de entradas/salidas
- pytest + httpx + pytest-asyncio para tests
- Sin base de datos (stateless por diseño en esta fase)

## Where things live

```
artifacts/molpredict-api/
  app/
    main.py              ← punto de entrada FastAPI
    core/config.py       ← Settings desde .env
    core/exceptions.py   ← manejadores globales de errores
    api/routes_*.py      ← endpoints por dominio
    services/            ← lógica RDKit real + predicción demo
    schemas/             ← modelos Pydantic
  data/demo_compounds.json  ← 5 inhibidores EGFR demo
  models/README.md          ← placeholder para modelo QSAR futuro
  tests/                    ← 33 tests (todos pasan)
```

## Architecture decisions

- **Predicción demostrativa determinista:** hash SHA-256 del SMILES canónico → pIC50 en [5.5–9.0]; sin aleatoriedad, reproducible.
- **pIC50 ↔ IC50(nM):** fórmula exacta `IC50_nM = 10^(9 - pIC50)`; validada en tests de consistencia.
- **Node.js API Server movido a `/api-nodejs`:** el template Node.js original ocupaba `/api`; se movió para que las rutas `/api/v1/...` de Python funcionen sin conflicto.
- **Sin autenticación en esta fase:** por diseño; CORS permisivo (`*`) en development.

## Product

API pública para: validar/canonicalizar SMILES, calcular descriptores RDKit (peso molecular, LogP, TPSA, Lipinski), renderizar estructuras 2D SVG, buscar similitud Tanimoto (Morgan FP), y predecir actividad demostrativa frente a EGFR.

## User preferences

- Solo backend Python en esta etapa; no crear frontend, auth, ni DB.
- Predicciones siempre marcadas como demostrativas (`scientifically_validated=false`).

## Gotchas

- RDKit requiere `expat` como dependencia de sistema (Nix). Si se reinstala el entorno, correr: `installSystemDependencies({ packages: ["expat"] })`.
- `Chem` se importa desde `rdkit`, NO desde `rdkit.Chem`: `from rdkit import Chem`.
- El workflow usa `cd artifacts/molpredict-api &&` antes de uvicorn; Python carga los módulos con `app.*` relativo a ese directorio.

## Pointers

- Ver `artifacts/molpredict-api/README.md` para documentación completa en español
- Ver `artifacts/molpredict-api/models/README.md` para el roadmap hacia el modelo QSAR real
