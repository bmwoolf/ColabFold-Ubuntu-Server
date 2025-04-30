# ColabFold-Ubuntu-Server

Set up a local ColabFold prediction server on an NVIDIA 4070 GPU via Ubuntu 24. Super specific, but needed for running [BinderLoop](https://github.com/bmwoolf/BinderLoop) (the other repo that allows end to end de novo binder generation).

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
sudo apt install bzip2 build-essential python3-dev zlib1g-dev libxml2-dev libbz2-dev scons python-is-python3

# navigate to Downloads after you have downloaded the 5GB Rosetta package
cd ~/Downloads

# extract the Rosetta archive (the versioning may have changed since you looked at this)
# this may take a few minutes
tar -xvjf rosetta_src_3.14_bundle.tar.bz2

# enter the source folder (which may be different depending on download version)
cd rosetta.source.release-371/main/source

# compile Rosetta- i chose 24 because i have 24 threads, you will have to choose for your computer
python3 ./scons.py -j24 mode=release bin

# test that rosetta is working (you should get a wall of text with two big lines in the middle)
cd bin
./score_jd2.default.linuxgccrelease -help
```

### Troubleshooting
I ran into a few problems installing this. Mainly with Python versioning, since my system is running 3.12. 
If you have problems, just email me and I can help install. 

```bash
# it started with this error
ModuleNotFoundError: No module named 'imp'

# which meant that 3.12+ was too new
# install build dependencies
sudo apt update
sudo apt install -y wget build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev

# download and install Python 3.10
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz
sudo tar xzf Python-3.10.13.tgz
cd Python-3.10.13
sudo ./configure --enable-optimizations
sudo make altinstall

# confirm install
python3.10 --version

# compile Rosetta
cd ~/Downloads/rosetta.source.release-371/main/source
python3.10 ./scons.py -j24 mode=release bin
```
