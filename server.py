import os
import json
import shutil
import subprocess
from uuid import uuid4
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from scripts.merge_pdbs import merge_pdbs


app = FastAPI()

# ColabFold requires FASTA files as inputs, so we temproraily store them 
INPUT_DIR = "/tmp/colabfold_inputs"
OUTPUT_DIR = "/tmp/colabfold_outputs"
COLABFOLD_BIN = "colabfold_batch"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Ubuntu requires specified relative path
OUTPUTS_DIR = Path("./outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# load dataset log
dataset_file = OUTPUTS_DIR / "dataset.jsonl"

# format input- FASTA header and sequence 
class PredictionRequest(BaseModel):
    header: str
    sequence: str

# route
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
    # fasta_id = f"{req.header.split()[0]}_{uuid4().hex[:8]}"
    # sanitize 
    fasta_id = req.header.split()[0].replace("|", "_") + "_" + uuid4().hex[:8]
    fasta_path = os.path.join(INPUT_DIR, f"{fasta_id}.fasta")
    output_path = os.path.join(OUTPUT_DIR, fasta_id)

    # write FASTA file with header and sequence 
    with open(fasta_path, "w") as f:
        f.write(f">{req.header}\n{req.sequence}\n")

    # run ColabFold, one sequence at a time 
    try:
        subprocess.run([
            COLABFOLD_BIN,
            fasta_path,
            output_path
        ], check=True) # Crashes if error
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="ColabFold prediction failed")

    # find result
    base_name = req.header.split()[0]
    
    # dynamically find the best-ranked model
    for file in os.listdir(output_path):
        if "rank_001" in file and file.endswith(".pdb"):
            pdb_path = os.path.join(output_path, file)
            break
    else:
        raise HTTPException(status_code=404, detail="PDB file not found (rank_001)")

    # check if PDB file exists 
    if not os.path.exists(pdb_path):
        raise HTTPException(status_code=404, detail="PDB file not found")

    # read PDB file and return its contents
    with open(pdb_path, "r") as f:
        pdb_content = f.read()

    # store each molecules pdb_content in a folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    protein_id = req.header.split("|")[0].strip()
    run_dir = outputs_dir / protein_id / timestamp
    
    run_dir.mkdir(parents=True, exist_ok=True)
    
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
        f.write(pdb_content)

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
    
    # append to dataset log
    dataset_log = {
        "protein_id": protein_id,
        "timestamp": timestamp,
        "sequence": req.sequence,
        "pdb_path": str(run_dir / "prediction.pdb"),
        "input_path": str(run_dir / "input.json"),
        "metadata_path": str(run_dir / "metadata.json")
    }

    with open(dataset_file, "a") as f:
        f.write(json.dumps(dataset_log) + "\n")
    
    # cleanup temp files
    shutil.rmtree(output_path, ignore_errors=True)
    os.remove(fasta_path)

    return {"pdb": pdb_content}
