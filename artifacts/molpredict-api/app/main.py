"""
MolPredict EGFR API — Punto de entrada de la aplicación FastAPI.

ESTADO ACTUAL:
  - Validación molecular: REAL (RDKit)
  - Descriptores fisicoquímicos: REAL (RDKit)
  - Estructura 2D: REAL (RDKit)
  - Similitud Tanimoto: REAL (RDKit Morgan FP)
  - Predicción pIC50/IC50: DEMOSTRATIVA (no validada científicamente)
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.core.exceptions import register_exception_handlers
from app.api import routes_health, routes_molecules, routes_predictions, routes_similarity, routes_model

# Configurar logging antes de todo
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Iniciando %s v%s en modo '%s' (demo_mode=%s)",
        settings.APP_NAME,
        settings.VERSION,
        settings.APP_ENV,
        settings.DEMO_MODE,
    )
    yield
    logger.info("Cerrando %s.", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API pública para validación molecular, cálculo de descriptores fisicoquímicos "
        "y predicción demostrativa de actividad frente a EGFR.\n\n"
        "**⚠️ AVISO:** Las predicciones de pIC50/IC50 son **demostrativas** y no están "
        "basadas en un modelo QSAR entrenado. `scientifically_validated = false` siempre."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────────────────────
cors_origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Manejadores globales de excepciones ─────────────────────────────────────
register_exception_handlers(app)

# ── Routers ─────────────────────────────────────────────────────────────────
app.include_router(routes_health.router)

api_v1_prefix = "/api/v1"
app.include_router(routes_molecules.router, prefix=api_v1_prefix)
app.include_router(routes_predictions.router, prefix=api_v1_prefix)
app.include_router(routes_similarity.router, prefix=api_v1_prefix)
app.include_router(routes_model.router, prefix=api_v1_prefix)

logger.info("Routers registrados bajo prefijo '%s'.", api_v1_prefix)
