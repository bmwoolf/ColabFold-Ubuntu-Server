from pathlib import Path
from Bio.PDB import PDBParser, PDBIO
import subprocess

def load_and_rename(pdb_path: Path, chain_id: str):
    """Load PDB and rename chain"""
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("pdb", str(pdb_path))
    for model in structure:
        for chain in model:
            chain.id = chain_id
    return structure

def merge_pdbs(protein_pdb: Path, binder_pdb: Path, output_path: Path) -> Path:
    """
    Merge protein and binder PDB files for Rosetta analysis.
    
    Args:
        protein_pdb: Path to protein PDB file (ScNtx)
        binder_pdb: Path to binder PDB file (SHRT)
        output_path: Path to save merged PDB
        
    Returns:
        Path to merged PDB file
    """
    # Load structures and rename chains
    protein = load_and_rename(protein_pdb, "A")  # ScNtx as chain A
    binder = load_and_rename(binder_pdb, "B")    # SHRT as chain B
    
    # Create output directory if needed
    output_path.parent.mkdir(exist_ok=True)
    
    # Merge structures
    io = PDBIO()
    with open(output_path, "w") as out:
        io.set_structure(protein)
        io.save(out)
        out.write("TER\n")  # Terminal record
        io.set_structure(binder)
        io.save(out)
        out.write("TER\nEND\n")
    
    return output_path

def run_interface_analyzer(pdb_path: Path) -> dict:
    """
    Run Rosetta InterfaceAnalyzer on merged PDB.
    
    Args:
        pdb_path: Path to merged PDB file
        
    Returns:
        Dict containing analysis results
    """
    cmd = [
        "InterfaceAnalyzer",
        f"-s {pdb_path}",
        "-pack_input true",
        "-pack_separated true",
        "-out:file:score_only score.sc"
    ]
    
    result = subprocess.run(" ".join(cmd), shell=True, check=True,
                          capture_output=True, text=True)
    
    # TODO: Parse score.sc file and return results
    return {"stdout": result.stdout}

if __name__ == "__main__":
    outputs = Path("outputs")
    
    # Find latest ScNtx and SHRT predictions
    scntx_dir = sorted(outputs.glob("7Z14_5_*"))[-1]
    shrt_dir = sorted(outputs.glob("9BK7_1_*"))[-1]
    
    protein_pdb = scntx_dir / "prediction.pdb"
    binder_pdb = shrt_dir / "prediction.pdb"
    merged_pdb = outputs / "merged" / "complex.pdb"
    
    merged_path = merge_pdbs(protein_pdb, binder_pdb, merged_pdb)
    print(f"Merged PDB saved to: {merged_path}")
    
    results = run_interface_analyzer(merged_path)
    print("Interface analysis complete")