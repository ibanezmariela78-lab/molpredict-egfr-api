"""
Servicio de búsqueda por similitud molecular usando Morgan Fingerprints y Tanimoto.
"""
import json
import logging
from pathlib import Path
from app.services.chemistry_service import parse_molecule, get_molecular_formula
from app.core.exceptions import InvalidSMILESError

logger = logging.getLogger(__name__)

from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs, rdMolDescriptors

# Ruta al dataset demostrativo
_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "demo_compounds.json"

# Cache del dataset con fingerprints precalculados
_COMPOUND_CACHE: list[dict] | None = None


def _load_compounds() -> list[dict]:
    """Carga y cachea los compuestos del dataset demostrativo."""
    global _COMPOUND_CACHE
    if _COMPOUND_CACHE is not None:
        return _COMPOUND_CACHE

    if not _DATA_PATH.exists():
        logger.error("Dataset no encontrado en %s", _DATA_PATH)
        return []

    with open(_DATA_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    compounds = []
    for entry in raw:
        smiles = entry.get("smiles", "")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            logger.warning("SMILES inválido en dataset para '%s', omitido.", entry.get("name"))
            continue
        canonical = Chem.MolToSmiles(mol)
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)
        formula = rdMolDescriptors.CalcMolFormula(mol)
        compounds.append({
            **entry,
            "canonical_smiles": canonical,
            "fingerprint": fp,
            "molecular_formula": formula,
        })

    _COMPOUND_CACHE = compounds
    logger.info("Dataset cargado: %d compuestos", len(compounds))
    return compounds


def search_similar(smiles: str, limit: int = 5) -> dict:
    """
    Busca los compuestos más similares al SMILES dado usando similitud de Tanimoto.

    Args:
        smiles: SMILES de consulta
        limit: número máximo de resultados

    Returns:
        dict con query_smiles, results, method, disclaimer
    """
    mol = parse_molecule(smiles)
    canonical_query = Chem.MolToSmiles(mol)
    query_fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)

    compounds = _load_compounds()
    if not compounds:
        return {
            "query_smiles": canonical_query,
            "results": [],
            "method": "Morgan Fingerprint (radio=2, 2048 bits) + Tanimoto",
            "disclaimer": (
                "Los valores de pIC50 son ilustrativos y no provienen "
                "de una fuente experimental verificada."
            ),
        }

    scored = []
    for c in compounds:
        sim = DataStructs.TanimotoSimilarity(query_fp, c["fingerprint"])
        scored.append({
            "name": c["name"],
            "canonical_smiles": c["canonical_smiles"],
            "similarity": round(float(sim), 4),
            "experimental_pic50_demo": c.get("experimental_pic50_demo", 0.0),
            "data_mode": c.get("data_mode", "demo"),
            "molecular_formula": c["molecular_formula"],
        })

    # Ordenar de mayor a menor similitud
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    results = scored[:limit]

    logger.debug(
        "Búsqueda de similitud: %s → %d resultados (top sim: %.4f)",
        canonical_query[:40],
        len(results),
        results[0]["similarity"] if results else 0.0,
    )

    return {
        "query_smiles": canonical_query,
        "results": results,
        "method": "Morgan Fingerprint (radio=2, 2048 bits) + Tanimoto",
        "disclaimer": (
            "Los valores de pIC50 son ilustrativos y no provienen "
            "de una fuente experimental verificada."
        ),
    }
