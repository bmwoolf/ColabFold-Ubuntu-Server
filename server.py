import os
import json
import subprocess
from uuid import uuid4
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

app = FastAPI()

# ColabFold requires FASTA files as inputs, so we temproraily store them 
INPUT_DIR = "/tmp/colabfold_inputs"
OUTPUT_DIR = "/tmp/colabfold_outputs"
COLABFOLD_BIN = "colabfold_batch"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUTS_DIR = Path("/outputs")

# Format input- FASTA header and sequence 
class PredictionRequest(BaseModel):
    header: str
    sequence: str

# Route
@app.post("/predict")
def predict(req: PredictionRequest, outputs_dir: Path = OUTPUTS_DIR):
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
    
    # Dynamically find the best-ranked model
    for file in os.listdir(output_path):
        if "rank_001" in file and file.endswith(".pdb"):
            pdb_path = os.path.join(output_path, file)
            break
    else:
        raise HTTPException(status_code=404, detail="PDB file not found (rank_001)")
        print("Files in output:", os.listdir(output_path))

    # Check if PDB file exists 
    if not os.path.exists(pdb_path):
        raise HTTPException(status_code=404, detail="PDB file not found")

    # Read PDB file and return its contents
    with open(pdb_path, "r") as f:
        pdb_content = f.read()
    # print("pdb_content", pdb_content)

    # store each molecules pdb_content in a folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = req.header.split("|")[0] # use the first part of the header as the name of the folder
    run_dir = outputs_dir / f"{name}_{timestamp}"
    run_dir.mkdir(exists_ok=True)

    # get header and sequence from the payload
    payload = {
        "header": req.header,
        "sequence": req.sequence
    }

    # write inputs to file 
    with open(run_dir / "input.json", "w") as f:
        json.dump(payload, f, indent=2)

    # write pdb content to file 
    pdb_path = run_dir / "prediction.pdb"
    with open(pdb_path, "w") as f:
        f.write(res.json()["pdb"])

    # save metadata to file 
    with open(run_dir / "metadata.json", "w") as f:
        json.dump({
            "timestamp": timestamp,
            "header": req.header,
            "sequence": req.sequence,
            "sequence_length": len(req.sequence),
            "files": {
                "input": "input.json",
                "prediction": "prediction.pdb"
            }
        }, f, indent=2)

    return {"pdb": pdb_content}
