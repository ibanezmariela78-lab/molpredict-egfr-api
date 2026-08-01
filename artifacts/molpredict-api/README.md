# MolPredict EGFR API

API pública de demostración para validación molecular y predicción de actividad inhibidora frente a EGFR.

---

## ⚠️ Aviso científico

Este proyecto contiene dos capas claramente separadas:

| Capa | Tipo | Descripción |
|---|---|---|
| Validación, descriptores, estructura 2D, similitud Tanimoto | **REAL** | Calculados con RDKit sobre el SMILES ingresado |
| Predicción pIC50 / IC50 frente a EGFR | **DEMOSTRATIVA** | No hay modelo QSAR entrenado; los valores se derivan de un hash determinista del SMILES canónico |

Toda respuesta de predicción incluye `prediction_mode: "demo"` y `scientifically_validated: false`. No reemplaza ensayos químicos, biológicos, toxicológicos, preclínicos ni clínicos.

---

## Estructura del proyecto

```
artifacts/molpredict-api/
├── app/
│   ├── main.py                  # FastAPI app, CORS, lifespan, routers
│   ├── core/
│   │   ├── config.py            # Settings desde variables de entorno
│   │   ├── logging_config.py   # Logging stdlib
│   │   └── exceptions.py       # Manejadores globales de errores
│   ├── api/
│   │   ├── routes_health.py     # GET /health
│   │   ├── routes_molecules.py  # POST /api/v1/molecules/*
│   │   ├── routes_predictions.py# POST /api/v1/predictions/egfr
│   │   ├── routes_similarity.py # POST /api/v1/similarity/search
│   │   └── routes_model.py      # GET /api/v1/models/* y /dataset/summary
│   ├── schemas/                 # Modelos Pydantic v2
│   └── services/
│       ├── chemistry_service.py # Validación y canonicalización RDKit
│       ├── descriptor_service.py# Descriptores fisicoquímicos RDKit
│       ├── rendering_service.py # SVG 2D RDKit MolDraw2D
│       ├── similarity_service.py# Tanimoto Morgan FP RDKit
│       └── prediction_service.py# Predicción demo determinista
├── data/
│   └── demo_compounds.json      # 5 inhibidores EGFR con valores ilustrativos
├── models/
│   └── README.md                # Placeholder — modelo QSAR no entrenado
├── tests/                       # 40 tests pytest (todos pasan)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Ejecución local

```bash
cd artifacts/molpredict-api
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Documentación Swagger disponible en: `http://localhost:8000/docs`

---

## Variables de entorno

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `APP_ENV` | `development` | Entorno de ejecución |
| `PORT` | `8000` | Puerto del servidor |
| `DEMO_MODE` | `true` | Activa el modo demostrativo |
| `CORS_ORIGINS` | `*` | Orígenes CORS (lista separada por comas o `*`) |
| `CORS_ALLOW_CREDENTIALS` | `false` | Credenciales CORS (se fuerza `false` cuando el origen es `*`) |
| `MODEL_VERSION` | `demo-v0.1` | Versión del modelo reportada en los metadatos |

---

## Endpoints

### Servicio

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Estado del servicio |
| `GET` | `/health` | Health check con disponibilidad de RDKit |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc |

### Moléculas (RDKit real)

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/v1/molecules/validate` | Valida SMILES y retorna fórmula molecular |
| `POST` | `/api/v1/molecules/descriptors` | Calcula descriptores fisicoquímicos (MW, LogP, TPSA, Lipinski…) |
| `POST` | `/api/v1/molecules/render` | Genera estructura 2D en SVG |

### Predicción (demostrativa)

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/v1/predictions/egfr` | Predicción demo de pIC50/IC50 frente a EGFR |

### Similitud (RDKit real)

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/v1/similarity/search` | Búsqueda por similitud Tanimoto sobre los 5 compuestos demo |

### Modelo y dataset

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/models/current` | Metadatos del modelo (indica que no está entrenado) |
| `GET` | `/api/v1/models/metrics` | Métricas del modelo (no disponibles — modelo no entrenado) |
| `GET` | `/api/v1/dataset/summary` | Resumen del dataset demo |

---

## Tests

```bash
cd artifacts/molpredict-api
python -m pytest tests -v --tb=short
```

Suite actual: **40 tests, 0 fallos**.

Cubre: health, validación de SMILES, descriptores, renderizado SVG, predicción EGFR, similitud Tanimoto, y configuración CORS.

---

## CORS

La configuración CORS está diseñada para uso público sin credenciales:

```
CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=false
```

Para restringir a un frontend específico de Lovable en producción, cambiar a:

```
CORS_ORIGINS=https://tu-app.lovable.app
CORS_ALLOW_CREDENTIALS=false
```

---

## Conectar con Lovable

El frontend de Lovable puede consumir esta API directamente usando las URLs de los endpoints listados arriba. No se requiere autenticación en esta versión de demostración. CORS está configurado con `*` para aceptar solicitudes desde cualquier origen.

Ejemplo de fetch desde JavaScript:

```javascript
const response = await fetch('https://TU_URL/api/v1/molecules/validate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ smiles: 'CCO' }),
});
const data = await response.json();
```

---

## Publicar en Replit

El artefacto `api-server` está configurado con:
- Comando de producción: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
- Health check: `GET /health`
- Puerto: dinámico (variable `PORT` de Replit)

Para publicar, presioná el botón **Publish** en el panel superior de Replit (sin configuración adicional).
