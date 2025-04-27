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
# system setup
sudo apt update && sudo apt install -y \
    wget git build-essential ffmpeg \
    libgl1 libglib2.0-0 libssl-dev

# install miniconda
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
eval "$($HOME/miniconda3/bin/conda shell.bash hook)"
```

## Environment setup in Conda for running app
```bash
# set up env
git clone https://github.com/bmwoolf/ColabFold-Ubuntu-Server.git
cd ColabFold-Ubuntu-Server

# create the environment 
conda env create -f environment.yml

# activate ColabFold 
conda activate colabfold-server 

# start server
uvicorn server:app --host 0.0.0.0 --port 8000
```

### Errors when starting
If you get JAX mismatch errors 
```bash
pip install --upgrade jax==0.4.27 jaxlib==0.4.27
```

## Installing Rosetta for protein + binder scoring 
First, download the actual binaries from their website. 
Just do the main 5GB one, not the 20GB Ubuntu one: https://downloads.rosettacommons.org/downloads/academic/3.14/
```bash
# install required packages 
sudo apt update
sudo apt install bzip2 build-essential python3-dev zlib1g-dev libxml2-dev libbz2-dev scons

# navigate to Downloads after you have downloaded the 5GB Rosetta package
cd ~/Downloads

# extract the Rosetta archive (the versioning may have changed since you looked at this)
# this may take a few minutes
tar -xvjf rosetta_src_3.14_bundle.tar.bz2

# enter the source folder
cd rosetta.source.release-371/main/source

# compile Rosetta
python3 ./scons.py -j4 mode=release bin
```
** I ran into a lot of problems installing this. If you have problems, just email me and I can help install. 


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
- tar -xvjs: "unpack this .tar.bz2 file and show me the progress"
- scons: python based build system, like Make files but for Python
    - allows the user to specify the number of jobs they can do
    - a job = one CPU thread
- hyperthreaded: one physical CPU core runs two instruction streams (threads) at once by sharing core resources
    - boosts performance 10-30%