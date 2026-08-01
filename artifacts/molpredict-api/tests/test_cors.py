"""
Tests de configuración CORS para MolPredict EGFR API.

Verifica la lógica de:
  - Wildcard origin → allow_credentials=False
  - Orígenes explícitos → allow_credentials según CORS_ALLOW_CREDENTIALS
  - Preflight OPTIONS desde un origen de Lovable
  - Ausencia de Access-Control-Allow-Credentials en respuesta wildcard
"""
import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport

pytestmark = pytest.mark.anyio


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_app(cors_origins: str, cors_allow_credentials: str = "false"):
    """Crea una nueva instancia de la app con variables de entorno sobreescritas."""
    import importlib
    import app.core.config as cfg_module
    import app.main as main_module

    with patch.dict("os.environ", {
        "CORS_ORIGINS": cors_origins,
        "CORS_ALLOW_CREDENTIALS": cors_allow_credentials,
    }):
        # Re-instanciar Settings con los nuevos valores de entorno
        new_settings = cfg_module.Settings()
        with patch.object(cfg_module, "settings", new_settings):
            with patch.object(main_module, "settings", new_settings):
                # Reimportar main para que CORS se aplique con los nuevos valores
                importlib.reload(main_module)
                return main_module.app


# ── Tests de la lógica de Settings ───────────────────────────────────────────

async def test_cors_wildcard_produces_star_list():
    """CORS_ORIGINS=* debe producir cors_origins_list=['*']."""
    from app.core.config import Settings
    s = Settings()
    with patch.object(s, "CORS_ORIGINS", "*"):
        assert s.cors_origins_list == ["*"]


async def test_cors_wildcard_forces_credentials_false():
    """CORS_ALLOW_CREDENTIALS=true no debe activar credenciales cuando el origen es '*'."""
    from app.core.config import Settings
    with patch.dict("os.environ", {
        "CORS_ORIGINS": "*",
        "CORS_ALLOW_CREDENTIALS": "true",
    }):
        s = Settings()
        assert s.cors_is_wildcard is True
        assert s.cors_allow_credentials is False


async def test_cors_explicit_origins_parsed_correctly():
    """Una lista separada por comas se convierte en la lista correcta de orígenes."""
    from app.core.config import Settings
    s = Settings()
    # Patch instance attributes directamente (los atributos de clase se leen en
    # tiempo de definición; parchear os.environ en ese punto ya no tiene efecto).
    s.CORS_ORIGINS = "https://app.example.com,https://staging.example.com"
    s.CORS_ALLOW_CREDENTIALS = False
    assert s.cors_origins_list == [
        "https://app.example.com",
        "https://staging.example.com",
    ]
    assert s.cors_is_wildcard is False


async def test_cors_explicit_origins_with_credentials_true():
    """Con orígenes explícitos y CORS_ALLOW_CREDENTIALS=true → allow_credentials=True."""
    from app.core.config import Settings
    s = Settings()
    s.CORS_ORIGINS = "https://app.example.com,https://staging.example.com"
    s.CORS_ALLOW_CREDENTIALS = True
    assert s.cors_allow_credentials is True


async def test_cors_preflight_lovable_with_wildcard(client: AsyncClient):
    """Preflight OPTIONS desde Lovable debe tener éxito cuando CORS_ORIGINS=*."""
    response = await client.options(
        "/api/v1/molecules/validate",
        headers={
            "Origin": "https://example.lovable.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    # FastAPI responde 200 o 204 a preflights válidos
    assert response.status_code in (200, 204)
    allow_origin = response.headers.get("access-control-allow-origin", "")
    assert allow_origin in ("*", "https://example.lovable.app")


async def test_cors_wildcard_no_credentials_header(client: AsyncClient):
    """Con wildcard la respuesta NO debe incluir access-control-allow-credentials: true."""
    response = await client.options(
        "/api/v1/molecules/validate",
        headers={
            "Origin": "https://example.lovable.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    credentials_header = response.headers.get("access-control-allow-credentials", "")
    assert credentials_header.lower() != "true"


async def test_app_starts_after_cors_change(client: AsyncClient):
    """La aplicación debe arrancar y responder /health correctamente."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
