# ColabFold-Ubuntu-Server

Set up a local ColabFold prediction server on an NVIDIA 4090 GPU via Ubuntu 24. Super specific, but needed for running [BinderLoop](https://github.com/bmwoolf/BinderLoop) (the other repo that allows end to end de novo binder generation).

## Software used 
```bash
Ubuntu 24.04 LTS
NVIDIA GPU + CUDA 11.8
Miniconda (Python 3.10)
ColabFold
JAX with CUDA
FFMPEG (for some visualization utils)
```

## Environment setup for running 
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

# Set up env
git clone https://github.com/bmwoolf/ColabFold-Ubuntu-Server.git
cd ColabFold-Ubuntu-Server

# Create the environment 
conda env create -f environment.yml

# Activate ColabFold 
conda activate colabfold-server 

# Verify install
colabfold_batch --help
```

If you get JAX mismatch errors 
```bash
pip install --upgrade jax==0.4.27 jaxlib==0.4.27
```