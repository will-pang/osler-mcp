import subprocess
import typer
import os
from osler.config import get_project_root, get_dataset_config, get_default_database_path, logger
import shutil

_PROJECT_ROOT = get_project_root()

def _download_dataset(dataset_config: dict) -> str:

    if dataset_config["dbt_project_name"]:
        dbt_project_path = _clone_dbt_project(dataset_config["github_repo"], dataset_config["dbt_project_name"])
        return dbt_project_path
    
    return False

### Start: DBT Utils
_DBT_PROJECT_ROOT = _PROJECT_ROOT/"dbt_projects"

def _clone_dbt_project(github_repo: str, dbt_project_name: str) -> str:
    """Clones DBT project into _DBT_PROJECT_ROOT"""

    dbt_project_path = _DBT_PROJECT_ROOT / dbt_project_name 
    
    if dbt_project_path.exists():
        shutil.rmtree(dbt_project_path)      

    try:
        subprocess.run([
        "git", "clone",
        github_repo,
        dbt_project_name
        ], cwd=_DBT_PROJECT_ROOT, check=True)
    except subprocess.CalledProcessError as e:
      typer.echo(f"❌ git clone failed with exit code {e.returncode}")
      raise typer.Exit(1)

    return dbt_project_path

def run_dbt_command(cmd: list[str], cwd: str) -> None:
    """Run a dbt command and handle errors."""
    try:
        cmd_plus_profiles = cmd + ['--profiles-dir', '../']
        result = subprocess.run(cmd_plus_profiles, cwd=cwd, check=True, text=True)
        logger.info(f"✅ dbt {cmd[1:]} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ {' '.join(cmd)} failed with exit code {e.returncode}")
        if e.stderr:
            typer.echo(e.stderr)
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("❌ dbt command not found. Please ensure dbt is installed.")
        raise typer.Exit(1)

### End: DBT Utils

def initialize_dataset(dataset_name: str) -> bool:
    database_path = get_default_database_path(dataset_name)
    dataset_config = get_dataset_config(dataset_name)
    if not dataset_config:
        logger.error(f"Configuration for dataset '{dataset_name}' not found.")
        return False
    dbt_project_path = _download_dataset(dataset_config)

    if not dbt_project_path:
        typer.secho(
            (
                f"Dataset '{dataset_name}' initialization FAILED. "
                "Please check logs for details."
            ),
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
    
    logger.info(f"Starting initialization for dataset: {dataset_name}")
    run_dbt_command(["dbt", "deps"], dbt_project_path)
    run_dbt_command(["dbt", "build"], dbt_project_path)
    run_dbt_command(["dbt", "docs", "generate"], dbt_project_path)

    return True