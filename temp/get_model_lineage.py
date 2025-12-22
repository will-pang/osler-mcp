import subprocess
from pathlib import Path

# Set working directory to your dbt project
script_dir = Path(__file__).parent
tuva_dir = script_dir.parent / "dbt_projects/tuva-project-demo"

cmd = [
    "dbt",
    "ls",
    "-s",
    "3+core__eligibility",
    "--profiles-dir",
    "../",
    "--profile",
    "tuva-project-demo",
    "--output",
    "name",
]

result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=tuva_dir)

lines = result.stdout.strip().split("\n")
models = [
    line
    for line in lines
    if not line.startswith("0")
    and "Running with dbt" not in line
    and "target not specified" not in line
    and "Registered adapter" not in line
    and "Found" not in line
]
store = "\n".join(models)

print(store)
