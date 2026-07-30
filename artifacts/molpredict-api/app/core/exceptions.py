"""
Excepciones personalizadas y manejadores globales de errores.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class InvalidSMILESError(ValueError):
    """Se lanza cuando el SMILES proporcionado no es válido según RDKit."""

    def __init__(self, smiles: str, detail: str = "SMILES inválido"):
        self.smiles = smiles
        self.detail = detail
        super().__init__(detail)


class SMILESTooLongError(ValueError):
    """Se lanza cuando el SMILES supera la longitud máxima permitida."""

    def __init__(self, length: int, max_length: int):
        self.detail = (
            f"El SMILES tiene {length} caracteres, el límite es {max_length}."
        )
        super().__init__(self.detail)


class RenderingError(RuntimeError):
    """Se lanza cuando falla la generación de la estructura 2D."""

    def __init__(self, detail: str = "Error al generar la estructura 2D"):
        self.detail = detail
        super().__init__(detail)


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los manejadores globales de excepciones en la app FastAPI."""

    @app.exception_handler(InvalidSMILESError)
    async def invalid_smiles_handler(
        request: Request, exc: InvalidSMILESError
    ) -> JSONResponse:
        logger.warning("SMILES inválido recibido en %s", request.url.path)
        return JSONResponse(
            status_code=422,
            content={
                "error": "smiles_invalido",
                "message": exc.detail,
                "detail": "La cadena SMILES proporcionada no pudo ser interpretada por RDKit.",
            },
        )

    @app.exception_handler(SMILESTooLongError)
    async def smiles_too_long_handler(
        request: Request, exc: SMILESTooLongError
    ) -> JSONResponse:
        logger.warning("SMILES demasiado largo en %s", request.url.path)
        return JSONResponse(
            status_code=422,
            content={
                "error": "smiles_demasiado_largo",
                "message": exc.detail,
            },
        )

    @app.exception_handler(RenderingError)
    async def rendering_error_handler(
        request: Request, exc: RenderingError
    ) -> JSONResponse:
        logger.error("Error de renderizado en %s: %s", request.url.path, exc.detail)
        return JSONResponse(
            status_code=500,
            content={
                "error": "error_renderizado",
                "message": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "Error inesperado en %s: %s",
            request.url.path,
            type(exc).__name__,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "error_interno",
                "message": "Se produjo un error interno en el servidor.",
            },
        )
