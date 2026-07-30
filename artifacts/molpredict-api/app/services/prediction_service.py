"""
Servicio de predicción demostrativa de actividad frente a EGFR.

ADVERTENCIA: Este servicio produce predicciones DEMOSTRATIVAS.
- prediction_mode = "demo"
- scientifically_validated = False
- No representa un modelo QSAR real entrenado.
"""
import hashlib
import json
import logging
import math
from pathlib import Path

logger = logging.getLogger(__name__)

from rdkit import Chem
from rdkit.Chem import AllChem, rdMolDescriptors

from app.services.chemistry_service import parse_molecule, get_canonical_smiles
from app.services.descriptor_service import calculate_descriptors
from app.core.config import settings

_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "demo_compounds.json"
_DEMO_CACHE: dict | None = None

DISCLAIMER = (
    "Predicción demostrativa no validada científicamente. "
    "No reemplaza ensayos químicos, biológicos, toxicológicos, preclínicos ni clínicos."
)


def _load_demo_compounds() -> dict:
    """Carga el dataset demostrativo indexado por SMILES canónico."""
    global _DEMO_CACHE
    if _DEMO_CACHE is not None:
        return _DEMO_CACHE

    if not _DATA_PATH.exists():
        _DEMO_CACHE = {}
        return _DEMO_CACHE

    with open(_DATA_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    cache = {}
    for entry in raw:
        smiles = entry.get("smiles", "")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            continue
        canonical = Chem.MolToSmiles(mol)
        cache[canonical] = entry

    _DEMO_CACHE = cache
    logger.info("Predicciones demo: %d compuestos cargados.", len(cache))
    return cache


def _deterministic_pic50(canonical_smiles: str) -> float:
    """
    Genera un pIC50 demostrativo determinista basado en el hash del SMILES canónico.
    El resultado es siempre el mismo para el mismo SMILES.
    Rango: 5.5 – 9.0 (rango típico de inhibidores EGFR conocidos).
    """
    digest = hashlib.sha256(canonical_smiles.encode("utf-8")).digest()
    # Usar los primeros 4 bytes como entero sin signo
    seed_int = int.from_bytes(digest[:4], byteorder="big")
    normalized = seed_int / (2**32 - 1)  # [0.0, 1.0]
    pic50 = 5.5 + normalized * 3.5       # [5.5, 9.0]
    return round(pic50, 2)


def _pic50_to_ic50_nm(pic50: float) -> float:
    """
    Conversión matemática consistente: pIC50 = -log10(IC50_molar)
    IC50 (nM) = 10^(9 - pIC50)
    """
    return round(10 ** (9.0 - pic50), 2)


def _activity_label(pic50: float) -> str:
    if pic50 >= 8.0:
        return "Actividad potencial muy alta"
    elif pic50 >= 7.0:
        return "Actividad potencial alta"
    elif pic50 >= 6.0:
        return "Actividad potencial moderada"
    else:
        return "Actividad potencial baja"


def _confidence_label(pic50: float) -> str:
    return "medium"  # siempre medium en modo demo


def _favorable_factors(desc: dict) -> list[str]:
    factors = []
    mw = desc.get("molecular_weight", 0)
    logp = desc.get("logp", 0)
    hba = desc.get("h_bond_acceptors", 0)
    arom = desc.get("aromatic_rings", 0)

    if mw <= 500:
        factors.append("Peso molecular dentro del rango favorable (<= 500 Da)")
    if 1 <= logp <= 4:
        factors.append("LogP en rango lipofílico óptimo (1–4)")
    if arom >= 2:
        factors.append("Presencia de anillos aromáticos (posible interacción con el sitio ATP)")
    if hba >= 3:
        factors.append("Número adecuado de aceptores de H para interacciones con el receptor")
    return factors


def _unfavorable_factors(desc: dict) -> list[str]:
    factors = []
    mw = desc.get("molecular_weight", 0)
    logp = desc.get("logp", 0)
    tpsa = desc.get("tpsa", 0)
    rot = desc.get("rotatable_bonds", 0)
    violations = desc.get("lipinski_violations", 0)

    if mw > 500:
        factors.append("Peso molecular elevado (> 500 Da): puede reducir biodisponibilidad oral")
    if logp > 5:
        factors.append("LogP elevado (> 5): posible acumulación lipofílica")
    if tpsa > 140:
        factors.append("TPSA elevada (> 140 Å²): puede limitar la absorción oral")
    if rot > 10:
        factors.append("Alta flexibilidad conformacional (> 10 enlaces rotables)")
    if violations > 2:
        factors.append(f"Viola {violations} criterios de Lipinski: perfil ADME subóptimo")
    return factors


def predict_egfr(smiles: str) -> dict:
    """
    Genera una predicción demostrativa de actividad frente a EGFR.

    IMPORTANTE: Esta predicción es demostrativa.
    - No está basada en un modelo entrenado real.
    - No representa evidencia científica.
    - prediction_mode = "demo"
    - scientifically_validated = False
    """
    mol = parse_molecule(smiles)
    canonical = Chem.MolToSmiles(mol)

    # Calcular Morgan fingerprint (informativo)
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)

    # Calcular descriptores reales
    desc = calculate_descriptors(smiles)

    # Obtener pIC50 demostrativo
    demo_compounds = _load_demo_compounds()

    if canonical in demo_compounds:
        # Compuesto conocido del dataset: usar valor predefinido
        entry = demo_compounds[canonical]
        pic50 = float(entry.get("experimental_pic50_demo", 7.0))
        logger.debug("Compuesto encontrado en dataset demo: %s → pIC50=%.2f", entry.get("name"), pic50)
    else:
        # Compuesto desconocido: predicción determinista basada en hash
        pic50 = _deterministic_pic50(canonical)
        logger.debug("Predicción determinista para SMILES desconocido: pIC50=%.2f", pic50)

    ic50_nm = _pic50_to_ic50_nm(pic50)

    # Calcular similitud máxima con el dataset (para dominio de aplicabilidad demo)
    from app.services.similarity_service import _load_compounds
    compounds = _load_compounds()
    max_sim = 0.0
    if compounds:
        from rdkit.Chem import DataStructs
        for c in compounds:
            sim = DataStructs.TanimotoSimilarity(fp, c["fingerprint"])
            if sim > max_sim:
                max_sim = sim
    max_sim = round(max_sim, 4)
    inside_domain = max_sim >= 0.3

    return {
        "canonical_smiles": canonical,
        "pic50_prediction": pic50,
        "ic50_nm_prediction": ic50_nm,
        "activity_label": _activity_label(pic50),
        "confidence": _confidence_label(pic50),
        "prediction_mode": "demo",
        "scientifically_validated": False,
        "model_version": settings.MODEL_VERSION,
        "descriptors": {
            "molecular_weight": desc["molecular_weight"],
            "logp": desc["logp"],
            "tpsa": desc["tpsa"],
            "h_bond_donors": desc["h_bond_donors"],
            "h_bond_acceptors": desc["h_bond_acceptors"],
            "rotatable_bonds": desc["rotatable_bonds"],
            "aromatic_rings": desc["aromatic_rings"],
            "heavy_atom_count": desc["heavy_atom_count"],
        },
        "applicability_domain": {
            "inside_domain": inside_domain,
            "maximum_similarity": max_sim,
            "confidence": "medium",
            "method": "demo",
        },
        "favorable_factors": _favorable_factors(desc),
        "unfavorable_factors": _unfavorable_factors(desc),
        "disclaimer": DISCLAIMER,
    }
