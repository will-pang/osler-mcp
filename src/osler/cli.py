import subprocess

from typing import Annotated

import typer

from osler.data_io import initialize_dataset
from osler.config import SUPPORTED_DATASETS, delete_default_database_path
from osler import __version__

app = typer.Typer(
    name="osler",
    help="osler CLI: Initialize Project",
    add_completion=False,
    rich_markup_mode="markdown",
)

def version_callback(value: bool):
    if value:
        typer.echo(f"Osler CLI Version: {__version__}")
        raise typer.Exit()


@app.command("init")
def dataset_init_cmd(
    dataset_name: Annotated[
        str,
        typer.Argument(
            help=(
                "Dataset to initialize. Default: 'tuva-project-demo'. "
                f"Supported: {', '.join(SUPPORTED_DATASETS.keys())}"
            ),
            metavar="DATASET_NAME",
        ),
    ] = "tuva-project-demo"
):
    dataset_key = dataset_name.lower()
    delete_default_database_path()
    initialization_successful = initialize_dataset(dataset_key)

    if not initialization_successful:
        typer.secho(
            (
                f"Dataset '{dataset_name}' initialization FAILED. "
                "Please check logs for details."
            ),
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
    
@app.command("config")
def config_cmd():
    pass

if __name__ == "__main__":
    app()
