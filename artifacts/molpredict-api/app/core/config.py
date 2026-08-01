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
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    MODEL_VERSION: str = os.getenv("MODEL_VERSION", "demo-v0.1")
    VERSION: str = "0.1.0"
    SERVICE_NAME: str = "molpredict-egfr-api"

    # Seguridad: límites de validación
    MAX_SMILES_LENGTH: int = 1000
    MIN_RENDER_DIM: int = 50
    MAX_RENDER_DIM: int = 2000

    @property
    def cors_origins_list(self) -> list[str]:
        """Lista limpia de orígenes CORS. Devuelve ['*'] si el valor es '*' o está vacío."""
        raw = self.CORS_ORIGINS.strip()
        if not raw or raw == "*":
            return ["*"]
        origins = [o.strip() for o in raw.split(",") if o.strip()]
        return origins if origins else ["*"]

    @property
    def cors_is_wildcard(self) -> bool:
        """True cuando la lista de orígenes es ['*']."""
        return self.cors_origins_list == ["*"]

    @property
    def cors_allow_credentials(self) -> bool:
        """
        Credenciales permitidas sólo cuando:
        - Los orígenes son explícitos (no wildcard), Y
        - CORS_ALLOW_CREDENTIALS=true.
        Con wildcard las credenciales se fuerzan a False (exigencia del navegador).
        """
        if self.cors_is_wildcard:
            return False
        return self.CORS_ALLOW_CREDENTIALS


settings = Settings()
