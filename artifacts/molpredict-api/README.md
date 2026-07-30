# MolPredict EGFR API

API pública en Python/FastAPI para validación molecular, cálculo de descriptores fisicoquímicos y predicción demostrativa de actividad frente a EGFR (Epidermal Growth Factor Receptor).

---

## Estado actual

| Función | Estado |
|---------|--------|
| Validación SMILES (RDKit) | ✅ Real |
| Canonicalización (RDKit) | ✅ Real |
| Fórmula molecular (RDKit) | ✅ Real |
| Descriptores fisicoquímicos (RDKit) | ✅ Real |
| Criterios de Lipinski | ✅ Real (orientativo) |
| Estructura 2D / SVG (RDKit) | ✅ Real |
| Similitud Tanimoto (Morgan FP) | ✅ Real |
| Predicción pIC50 EGFR | ⚠️ Demostrativa |
| Predicción IC50 (nM) | ⚠️ Demostrativa |
| Confianza de la predicción | ⚠️ Demostrativa |
| Factores explicativos | ⚠️ Demostrativa |
| Dominio de aplicabilidad | ⚠️ Demostrativa |
| Modelo QSAR real | ❌ No entrenado aún |

---

## Disclaimer científico

> **Las predicciones de pIC50 e IC50 son demostrativas y NO están basadas en un modelo QSAR entrenado ni validado.**
>
> `prediction_mode = "demo"` | `scientifically_validated = false`
>
> No reemplaza ensayos químicos, biológicos, toxicológicos, preclínicos ni clínicos.

---

## Instalación

```bash
# Clonar o acceder al directorio
cd artifacts/molpredict-api

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
cp .env.example .env
```

## Ejecución

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

O con la variable de entorno PORT:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### Documentación interactiva

- Swagger UI: `http://localhost:8000/docs`
- ReDoc:       `http://localhost:8000/redoc`

---

## Endpoints

### Salud

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servicio y disponibilidad de RDKit |

### Moléculas

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/molecules/validate` | Validar y canonicalizar SMILES |
| POST | `/api/v1/molecules/descriptors` | Descriptores fisicoquímicos (RDKit real) |
| POST | `/api/v1/molecules/render` | Estructura 2D en SVG |

### Predicción

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/predictions/egfr` | Predicción demostrativa pIC50/IC50 frente a EGFR |

### Similitud

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/similarity/search` | Búsqueda por similitud Tanimoto |

### Modelo y Dataset

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/models/current` | Información del modelo actual |
| GET | `/api/v1/models/metrics` | Métricas (no disponibles hasta entrenar) |
| GET | `/api/v1/dataset/summary` | Resumen del dataset demostrativo |

---

## Ejemplos de curl

```bash
# Health
curl http://localhost:8000/health

# Validar SMILES
curl -X POST http://localhost:8000/api/v1/molecules/validate \
  -H "Content-Type: application/json" \
  -d '{"smiles": "CCO"}'

# Descriptores
curl -X POST http://localhost:8000/api/v1/molecules/descriptors \
  -H "Content-Type: application/json" \
  -d '{"smiles": "COc1ccc2ncnc(Nc3ccc(F)c(Cl)c3)c2c1"}'

# Renderizado SVG
curl -X POST http://localhost:8000/api/v1/molecules/render \
  -H "Content-Type: application/json" \
  -d '{"smiles": "COc1cc2c(Nc3ccc(F)c(Cl)c3)ncnc2cc1OCCCN1CCOCC1", "width": 500, "height": 350}'

# Predicción EGFR (DEMO)
curl -X POST http://localhost:8000/api/v1/predictions/egfr \
  -H "Content-Type: application/json" \
  -d '{"smiles": "COc1cc2c(Nc3ccc(F)c(Cl)c3)ncnc2cc1OCCCN1CCOCC1"}'

# Similitud molecular
curl -X POST http://localhost:8000/api/v1/similarity/search \
  -H "Content-Type: application/json" \
  -d '{"smiles": "COc1cc2c(Nc3ccc(F)c(Cl)c3)ncnc2cc1OCCCN1CCOCC1", "limit": 5}'

# Métricas del modelo
curl http://localhost:8000/api/v1/models/metrics
```

---

## Tests

```bash
cd artifacts/molpredict-api
pytest tests/ -v
```

Los tests cubren:
1. GET /health
2. SMILES válido
3. SMILES inválido (422)
4. Canonicalización
5. Fórmula molecular (formato correcto: Cl, no CL)
6. Cálculo de descriptores
7. Renderizado SVG
8. Predicción en modo demo
9. Consistencia matemática pIC50 ↔ IC50
10. Similitud ordenada
11. Métricas no disponibles
12. Dataset demostrativo

---

## Variables de entorno

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `APP_NAME` | `MolPredict EGFR API` | Nombre de la aplicación |
| `APP_ENV` | `development` | Entorno (development/production) |
| `PORT` | `8000` | Puerto de escucha |
| `CORS_ORIGINS` | `*` | Orígenes CORS permitidos |
| `DEMO_MODE` | `true` | Modo demostrativo |
| `MODEL_VERSION` | `qsar-demo-v0.1` | Versión del modelo |

---

## Limitaciones actuales

- La predicción de pIC50/IC50 es **demostrativa** y no representa ciencia real.
- El dataset contiene solo 5 compuestos inhibidores EGFR conocidos (valores ilustrativos).
- No hay base de datos persistente; la API es stateless.
- No hay autenticación (será implementada en una fase posterior).

---

## Conexión futura con Lovable (frontend)

El frontend externo creado en Lovable podrá consumir esta API configurando la variable de entorno de base URL de la API. Los endpoints están diseñados con CORS permisivo en desarrollo para facilitar la integración.

Pasos de integración:
1. Obtener la URL de producción del deploy en Replit.
2. Configurar `CORS_ORIGINS` en producción con el dominio de Lovable.
3. El frontend llama a `/api/v1/molecules/validate` antes de enviar a predicción.
4. Usar `/api/v1/molecules/render` para mostrar estructuras 2D en la UI.

---

## Roadmap hacia el modelo QSAR real

1. **Datos** — Descargar ~5.000 actividades EGFR (IC50/Ki) de ChEMBL.
2. **Curaduría** — Estandarizar SMILES, eliminar duplicados y datos ambiguos.
3. **Características** — Morgan FP 2048 bits + descriptores RDKit.
4. **Entrenamiento** — Random Forest / XGBoost con validación cruzada 5-fold.
5. **Métricas** — R², RMSE en set externo, Q² de validación cruzada.
6. **AD** — Dominio de aplicabilidad basado en similitud sobre el set de entrenamiento.
7. **Producción** — Reemplazar `prediction_service.py` con carga de `joblib`.
8. **Validación externa** — Comparar contra literatura (benchmarks EGFR QSAR).
