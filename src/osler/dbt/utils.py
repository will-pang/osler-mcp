import shutil
import subprocess

import typer

from osler.config import get_project_root, logger

_PROJECT_ROOT = get_project_root()
_DBT_PROJECT_ROOT = _PROJECT_ROOT / "dbt_projects"


def clone_dbt_project(github_repo: str, dbt_project_name: str) -> str:
    """Clones DBT project into _DBT_PROJECT_ROOT"""

    dbt_project_path = _DBT_PROJECT_ROOT / dbt_project_name

    if dbt_project_path.exists():
        shutil.rmtree(dbt_project_path)

    try:
        subprocess.run(
            ["git", "clone", github_repo, dbt_project_name], cwd=_DBT_PROJECT_ROOT, check=True
        )
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ git clone failed with exit code {e.returncode}")
        raise typer.Exit(1)

    return dbt_project_path


def run_dbt_command(cmd: list[str], cwd: str, dataset_name: str) -> None:
    """Run a dbt command and handle errors."""
    try:
        add_profiles_specification_to_cmd = cmd + [
            "--profiles-dir",
            "../",
            "--profile",
            dataset_name,
        ]
        result = subprocess.run(
            add_profiles_specification_to_cmd, capture_output=True, cwd=cwd, check=True, text=True
        )
        logger.info(f"✅ dbt {cmd[1:]} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        logger.info(f"❌ {' '.join(cmd)} failed with exit code {e.returncode}")
        if e.stderr:
            logger.error(e.stderr)
        raise typer.Exit(1)
    except FileNotFoundError:
        logger.info("❌ dbt command not found. Please ensure dbt is installed.")
        raise typer.Exit(1)


def get_dbt_model_lineage(table_name, direction, depth):
    dataset_name = "tuva-project-demo"
    cwd = _DBT_PROJECT_ROOT / dataset_name

    if direction == "parent":
        lineage_arg = f"{depth}+{table_name}"
    elif direction == "children":
        lineage_arg = f"{table_name}+{depth}"

    cmd = ["dbt", "ls", "-s", lineage_arg]

    result = run_dbt_command(cmd, cwd, dataset_name)

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
    models_lst = "\n".join(models)

    return models_lst
