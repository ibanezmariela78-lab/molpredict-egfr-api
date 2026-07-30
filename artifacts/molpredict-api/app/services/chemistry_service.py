"""
Servicio de química molecular usando RDKit.
Valida SMILES, canonicaliza y calcula propiedades básicas.
"""
import logging
from app.core.config import settings
from app.core.exceptions import InvalidSMILESError, SMILESTooLongError

logger = logging.getLogger(__name__)

try:
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    logger.warning("RDKit no está disponible. Los servicios de química estarán deshabilitados.")


def check_rdkit() -> bool:
    """Verifica si RDKit está disponible."""
    return RDKIT_AVAILABLE


def _check_length(smiles: str) -> None:
    """Verifica que el SMILES no exceda la longitud máxima."""
    if len(smiles) > settings.MAX_SMILES_LENGTH:
        raise SMILESTooLongError(len(smiles), settings.MAX_SMILES_LENGTH)


def parse_molecule(smiles: str):
    """
    Parsea un SMILES con RDKit.

    Returns:
        mol: objeto RDKit Mol

    Raises:
        InvalidSMILESError: si el SMILES no es válido
        SMILESTooLongError: si el SMILES es demasiado largo
    """
    if not RDKIT_AVAILABLE:
        raise RuntimeError("RDKit no está disponible en este entorno.")

    _check_length(smiles)

    mol = Chem.MolFromSmiles(smiles.strip())
    if mol is None:
        raise InvalidSMILESError(smiles, f"El SMILES '{smiles[:50]}...' no pudo ser interpretado por RDKit.")

    return mol


def get_canonical_smiles(smiles: str) -> str:
    """Devuelve el SMILES canónico de la molécula."""
    mol = parse_molecule(smiles)
    return Chem.MolToSmiles(mol)


def get_molecular_formula(mol) -> str:
    """Calcula la fórmula molecular usando RDKit."""
    return rdMolDescriptors.CalcMolFormula(mol)


def validate_smiles(smiles: str) -> dict:
    """
    Valida un SMILES y devuelve información básica de la molécula.

    Returns:
        dict con: valid, input_smiles, canonical_smiles, molecular_formula,
                  atom_count, heavy_atom_count, message
    """
    _check_length(smiles)

    mol = Chem.MolFromSmiles(smiles.strip())
    if mol is None:
        raise InvalidSMILESError(
            smiles,
            "La cadena SMILES no pudo ser interpretada. Verifique la sintaxis.",
        )

    # Añadir hidrógenos explícitos solo para contar todos los átomos
    mol_with_h = Chem.AddHs(mol)

    canonical = Chem.MolToSmiles(mol)
    formula = rdMolDescriptors.CalcMolFormula(mol)
    atom_count = mol_with_h.GetNumAtoms()
    heavy_atom_count = mol.GetNumHeavyAtoms()

    logger.debug(
        "SMILES validado: %s → %s (fórmula: %s)", smiles[:40], canonical, formula
    )

    return {
        "valid": True,
        "input_smiles": smiles.strip(),
        "canonical_smiles": canonical,
        "molecular_formula": formula,
        "atom_count": atom_count,
        "heavy_atom_count": heavy_atom_count,
        "message": "Estructura molecular válida",
    }
