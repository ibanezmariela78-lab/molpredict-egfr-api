"""
Configuración de logging estándar para MolPredict EGFR API.
"""
import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """Configura el logging de la aplicación."""
    log_level = logging.DEBUG if settings.APP_ENV == "development" else logging.INFO

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
    )

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Silenciar logs muy verbosos de terceros
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Devuelve un logger con el nombre dado."""
    return logging.getLogger(name)
