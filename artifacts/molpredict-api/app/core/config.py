"""
Configuración general de la aplicación MolPredict EGFR API.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "MolPredict EGFR API")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    MODEL_VERSION: str = os.getenv("MODEL_VERSION", "qsar-demo-v0.1")
    VERSION: str = "0.1.0"
    SERVICE_NAME: str = "molpredict-egfr-api"

    # Seguridad: límites de validación
    MAX_SMILES_LENGTH: int = 1000
    MIN_RENDER_DIM: int = 50
    MAX_RENDER_DIM: int = 2000

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
