"""
Servicio de cálculo de descriptores fisicoquímicos usando RDKit.
Todos los descriptores son calculados con RDKit real.
"""
import logging
from app.services.chemistry_service import parse_molecule, get_canonical_smiles, get_molecular_formula
from app.core.config import settings

logger = logging.getLogger(__name__)

from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors


def calculate_descriptors(smiles: str) -> dict:
    """
    Calcula descriptores fisicoquímicos reales con RDKit.

    Returns:
        dict con todos los descriptores y evaluación de Lipinski
    """
    mol = parse_molecule(smiles)
    canonical = Chem.MolToSmiles(mol)
    formula = get_molecular_formula(mol)

    # Descriptores básicos
    mw = round(Descriptors.ExactMolWt(mol), 4)
    logp = round(Descriptors.MolLogP(mol), 4)
    tpsa = round(Descriptors.TPSA(mol), 4)
    hbd = rdMolDescriptors.CalcNumHBD(mol)
    hba = rdMolDescriptors.CalcNumHBA(mol)
    rot_bonds = rdMolDescriptors.CalcNumRotatableBonds(mol)
    arom_rings = rdMolDescriptors.CalcNumAromaticRings(mol)
    frac_csp3 = round(Descriptors.FractionCSP3(mol), 4)
    formal_charge = Chem.GetFormalCharge(mol)
    atom_count = Chem.AddHs(mol).GetNumAtoms()
    heavy_atom_count = mol.GetNumHeavyAtoms()
    ring_count = rdMolDescriptors.CalcNumRings(mol)

    # Evaluación de Lipinski (5 criterios orientativos)
    lipinski_criteria = [
        {
            "name": "Peso molecular",
            "value": mw,
            "threshold": "<= 500",
            "passes": mw <= 500,
        },
        {
            "name": "LogP",
            "value": logp,
            "threshold": "<= 5",
            "passes": logp <= 5,
        },
        {
            "name": "Donantes de puentes de hidrógeno",
            "value": float(hbd),
            "threshold": "<= 5",
            "passes": hbd <= 5,
        },
        {
            "name": "Aceptores de puentes de hidrógeno",
            "value": float(hba),
            "threshold": "<= 10",
            "passes": hba <= 10,
        },
        {
            "name": "Enlaces rotables",
            "value": float(rot_bonds),
            "threshold": "<= 5",
            "passes": rot_bonds <= 5,
        },
    ]

    passed = sum(1 for c in lipinski_criteria if c["passes"])
    total = len(lipinski_criteria)
    violations = total - passed

    if violations == 0:
        lipinski_summary = "Cumple todos los criterios orientativos de Lipinski."
    elif violations == 1:
        lipinski_summary = f"Viola 1 de {total} criterios orientativos de Lipinski."
    else:
        lipinski_summary = f"Viola {violations} de {total} criterios orientativos de Lipinski."

    return {
        "canonical_smiles": canonical,
        "molecular_formula": formula,
        "molecular_weight": mw,
        "logp": logp,
        "tpsa": tpsa,
        "h_bond_donors": hbd,
        "h_bond_acceptors": hba,
        "rotatable_bonds": rot_bonds,
        "aromatic_rings": arom_rings,
        "fraction_csp3": frac_csp3,
        "formal_charge": formal_charge,
        "atom_count": atom_count,
        "heavy_atom_count": heavy_atom_count,
        "ring_count": ring_count,
        "lipinski_violations": violations,
        "lipinski": {
            "criteria": lipinski_criteria,
            "passed_count": passed,
            "total_count": total,
            "summary": lipinski_summary,
        },
    }
