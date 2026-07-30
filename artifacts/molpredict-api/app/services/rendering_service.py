"""
Servicio de renderizado de estructuras moleculares 2D usando RDKit.
Genera SVG con enlaces químicos, etiquetas de heteroátomos y fondo transparente.
"""
import logging
from app.services.chemistry_service import parse_molecule, get_canonical_smiles
from app.core.exceptions import RenderingError

logger = logging.getLogger(__name__)

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D


def render_molecule_svg(smiles: str, width: int = 500, height: int = 350) -> dict:
    """
    Genera una representación 2D en formato SVG de la molécula.

    Args:
        smiles: Cadena SMILES
        width:  Ancho del SVG en píxeles (50–2000)
        height: Alto del SVG en píxeles (50–2000)

    Returns:
        dict con canonical_smiles, format, width, height, svg
    """
    mol = parse_molecule(smiles)
    canonical = Chem.MolToSmiles(mol)

    # Calcular coordenadas 2D
    try:
        AllChem.Compute2DCoords(mol)
    except Exception as exc:
        logger.error("Error al calcular coordenadas 2D: %s", exc)
        raise RenderingError("No se pudieron calcular las coordenadas 2D de la molécula.") from exc

    # Configurar el renderizador SVG
    try:
        drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
        draw_opts = drawer.drawOptions()
        draw_opts.addStereoAnnotation = True
        draw_opts.addAtomIndices = False
        draw_opts.clearBackground = True  # fondo blanco/transparente

        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg_text = drawer.GetDrawingText()
    except Exception as exc:
        logger.error("Error al renderizar SVG: %s", exc)
        raise RenderingError("Fallo durante el renderizado SVG de la molécula.") from exc

    logger.debug("SVG generado para %s (%dx%d)", canonical[:40], width, height)

    return {
        "canonical_smiles": canonical,
        "format": "svg",
        "width": width,
        "height": height,
        "svg": svg_text,
    }
