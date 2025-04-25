# ColabFold-Ubuntu-Server

Set up a local ColabFold prediction server on an NVIDIA 4090 GPU via Ubuntu 24. Super specific, but needed for running [BinderLoop](https://github.com/bmwoolf/BinderLoop) (the other repo that allows end to end de novo binder generation).

## Software used 
```bash
Ubuntu 24.04 LTS
NVIDIA GPU + CUDA 11.8
Miniconda (Python 3.10)
ColabFold (v1.5.3)
JAX with CUDA
FFMPEG (visualization utils)
Rosetta (structure scoring and docking)
BioPython (PDB/FASTA handling)
FastAPI (ColabFold API server)
Pydantic (request validation)
```

## System setup for running on Ubuntu 
```bash
# System setup
sudo apt update && sudo apt install -y \
    wget git build-essential ffmpeg \
    libgl1 libglib2.0-0 libssl-dev

# Install miniconda
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
eval "$($HOME/miniconda3/bin/conda shell.bash hook)"
```

## Environment setup in Conda for running app
```bash
# Set up env
git clone https://github.com/bmwoolf/ColabFold-Ubuntu-Server.git
cd ColabFold-Ubuntu-Server

# Create the environment 
conda env create -f environment.yml

# Activate ColabFold 
conda activate colabfold-server 

# Start server
uvicorn server:app --host 0.0.0.0 --port 8000
```

### Errors when starting
If you get JAX mismatch errors 
```bash
pip install --upgrade jax==0.4.27 jaxlib==0.4.27
```

## Notes
- de novo binder generation
    - [masif](https://github.com/LPDI-EPFL/masif)  
        - geometric deep learning on protein surfaces for predicting a binding site on a single protein
        - used for finding where to bind 
    - [p2rank](https://github.com/rdk/p2rank)
        - ML-based ligand binding site predictor (designed for small molecules)
        - predicts pockets likely to bind to molecules 
        - used for designing around pockets
    - [RFDiffusion2](https://www.biorxiv.org/content/10.1101/2025.04.09.648075v2)
        - structure based de novo binder generation
        - put in a target + optional constraints, and it generates the binder 
        - doesn't need binding site if scaffolded correctly 