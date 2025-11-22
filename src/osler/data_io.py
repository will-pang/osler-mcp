from osler.config import get_dataset_config, logger
from osler.dbt.utils import clone_dbt_project, run_dbt_command


def initialize_dataset(dataset_name: str) -> bool:
    """Initializes a dataset: downloads files and loads them into a database."""
    # database_path = get_default_database_path(dataset_name)
    dataset_config = get_dataset_config(dataset_name)

    if not dataset_config:
        logger.error(f"Configuration for dataset '{dataset_name}' not found.")
        return False

    # For DBT Projects
    if dataset_config["dbt_project_name"]:
        dbt_project_path = clone_dbt_project(
            dataset_config["github_repo"], dataset_config["dbt_project_name"]
        )
        run_dbt_command(["dbt", "deps"], dbt_project_path, dataset_name)
        run_dbt_command(["dbt", "build"], dbt_project_path, dataset_name)
        run_dbt_command(["dbt", "docs", "generate"], dbt_project_path, dataset_name)

    return True
