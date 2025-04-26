import os
import subprocess
from pathlib import Path

def score_with_rosetta(pdb_path: Path) -> float:
    cmd = [
        f"{os.environ['ROSETTA3']}/main/source/bin/rosetta_scripts.static.linuxgccrelease",
        "-parser:protocol", "score.xml",  # you must provide this XML
        "-in:file:s", str(pdb_path),
        "-out:file:scorefile", "score.sc"
    ]
    subprocess.run(cmd, check=True)
    with open("score.sc") as f:
        for line in f:
            if not line.startswith("SCORE:") or "total_score" in line:
                continue
            score = float(line.split()[1])  # second column is usually total_score
            return score