import logging
import os
import shutil
from pathlib import Path

APP_NAME = "osler"

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(), logging.FileHandler("osler.log")],
)
logger = logging.getLogger(APP_NAME)


# -------------------------------------------------------------------
# Data directory rooted at project root (two levels up from this file)
# -------------------------------------------------------------------
def get_project_root() -> Path:
    """
    Determine project root:
    - If cloned repo: use repository root (two levels up from this file)
    - If pip installed: ALWAYS use home directory
    """
    package_root = Path(__file__).resolve().parents[2]

    # Check if we're in a cloned repository (has pyproject.toml at root)
    if (package_root / "pyproject.toml").exists():
        return package_root

    # Pip installed: ALWAYS use home directory (simple and consistent)
    return Path.home()


_PROJECT_ROOT = get_project_root()
_PROJECT_DATA_DIR = _PROJECT_ROOT / "osler_data"

DEFAULT_DATABASES_DIR = _PROJECT_DATA_DIR / "databases"
print(f"DEFAULT_DATABASES_DIR: {DEFAULT_DATABASES_DIR}")

SUPPORTED_DATASETS = {  # Contains a collection of dataset configs
    "tuva-project-demo": {
        "db_filename": "tuva_project_demo.duckdb",
        "dbt_project_name": "tuva-project-demo",
        "github_repo": "https://github.com/tuva-health/demo",
    }
}


# --------------------------------------------------
# Helper functions
# --------------------------------------------------
def get_dataset_config(dataset_name: str) -> dict | None:
    """Retrieve the configuration for a given dataset (case-insensitive)."""
    return SUPPORTED_DATASETS.get(dataset_name.lower())


def create_default_database_path(dataset_name: str) -> bool:
    """
    Return the default DuckDB path for a given dataset,
    under <project_root>/osler_data/databases/.
    """
    cfg = get_dataset_config(dataset_name)
    if cfg:
        DEFAULT_DATABASES_DIR.mkdir(parents=True, exist_ok=True)
    else:
        logger.error(f"Unsupported dataset: {dataset_name}")

    return True


def delete_default_database_path() -> None:
    """Deletes default database path"""
    if os.path.exists(DEFAULT_DATABASES_DIR):
        shutil.rmtree(DEFAULT_DATABASES_DIR)

    return None
