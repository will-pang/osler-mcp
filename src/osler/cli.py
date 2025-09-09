import subprocess
from osler.download_data import initialize_dataset

import typer

app = typer.Typer(
    name="osler",
    help="osler CLI: Initialize Tuva Health Demo in DuckDB",
    add_completion=False,
    rich_markup_mode="markdown",
)

@app.command()
def init(project_name: str):
    initialize_dataset(project_name)


if __name__ == "__main__":
    app()
