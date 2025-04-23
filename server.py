from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import subprocess
import os
from colabfold.colabfold_app import ColabFoldApp

app = FastAPI()

# ColabFold requires FASTA files as inputs, so we temproraily store them 
INPUT_DIR = "tmp/colabfold_inputs"
OUTPUT_DIR = "tmp/colabfold_outputs"
COLABFOLD_BIN = "colabfold_batch"

# Format input- FASTA header and sequence 
class PredicitonRequest(BaseModel):
    header: str
    sequence: str

# Route
@app.post("/predict"):
def predict(req: Predictionrequest):
    """
    Predicts a single sequence using ColabFold. ColabFold takes in a file as input, does MSA generation, 
    predicts the structure using AlphaFold2, then relaxes the structure with energy minimization via Amber.  

    Input:
        header: str
        sequence: str

    Output:
        pdb_file: str
    
    ColabFold outputs many files, but the main output is in [protein]_relaxed_rank_1_model_1.pdb, 
    which you can then feed into PyMOL, ChimeraX or your favorite structure viewer. 
    """
    fasta_id = f"{req.header.split()[0]}_{uuid4().hex[:8]}"
    fasta_path = os.path.join(INPUT_DIR, f"{fasta_id}.fasta")
    output_path = os.path.join(OUTPUT_DIR, fasta_id)

    # Write FASTA file with header and sequence 
    with open(fasta_path, "w") as f:
        f.write(f">{req.header}\n{req.sequence}\n")

    # Run ColabFold, one sequence at a time 
    try:
        subprocess.run([
            COLABFOLD_BIN,
            fasta_path,
            output_path
        ], check=True) # Crashes if error
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="ColabFold prediction failed")

    # Find result
    base_name = req.header.split()[0]
    print("base_name", base_name)
    pdb_path = os.path.join(output_path, f"{base_name}_relaxed_rank_1_model_1.pdb")
    print("pdb_path", pdb_path)
    if not os.path.exists(pdb_path):
        raise HTTPException(status_code=404, detail="PDB file not found")

    # Read PDB file 
    return {"pdb_file": pdb_path}
