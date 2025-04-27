# scripts/merge_pdbs.py

from pathlib import Path
from Bio.PDB import PDBParser, PDBIO
import subprocess

def load_and_rename(pdb_path: Path, chain_id: str):
    """Load a PDB file and rename all chains to the given chain ID."""
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("pdb", str(pdb_path))
    for model in structure:
        for chain in model:
            chain.id = chain_id
    return structure

def merge_pdbs(protein_pdb: Path, binder_pdb: Path, output_path: Path) -> Path:
    """
    Merge protein and binder PDBs into one complex for Rosetta analysis.

    Args:
        protein_pdb: Path to the protein PDB (chain A).
        binder_pdb: Path to the binder PDB (chain B).
        output_path: Path to save the merged complex PDB.

    Returns:
        Path to merged output PDB.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    protein = load_and_rename(protein_pdb, "A")
    binder = load_and_rename(binder_pdb, "B")

    io = PDBIO()
    with open(output_path, "w") as out:
        io.set_structure(protein)
        io.save(out)
        out.write("TER\n")
        io.set_structure(binder)
        io.save(out)
        out.write("TER\nEND\n")

    return output_path

def run_interface_analyzer(pdb_path: Path) -> dict:
    """
    Run Rosetta's InterfaceAnalyzer on the merged PDB file.

    Args:
        pdb_path: Path to the merged complex PDB.

    Returns:
        Dictionary containing Rosetta output.
    """
    cmd = [
        "InterfaceAnalyzer.default.linuxgccrelease",
        f"-s {pdb_path}",
        "-pack_input true",
        "-pack_separated true",
        "-out:file:score_only",
        str(pdb_path.with_suffix('.sc'))
    ]

    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "score_file": str(pdb_path.with_suffix('.sc'))
    }
