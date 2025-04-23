#!/bin/bash
# Run ColabFold server

source ~/miniconda3/etc/profile.d/conda.sh
conda activate colabfold

colabfold_batch --help  # or whatever command you're testing
