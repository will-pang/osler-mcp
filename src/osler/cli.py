import subprocess

import typer

app = typer.Typer(
    name="osler",
    help="osler CLI: Initialize Tuva Health Demo in DuckDB",
    add_completion=False,
    rich_markup_mode="markdown",
)


def run_dbt_command(cmd: list[str], cwd: str = "tuva-health-demo") -> None:
    """Run a dbt command and handle errors."""
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, text=True)
        typer.echo(result.stdout)
        typer.echo(f"✅ dbt {cmd[1:]} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ {' '.join(cmd)} failed with exit code {e.returncode}")
        if e.stderr:
            typer.echo(e.stderr)
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("❌ dbt command not found. Please ensure dbt is installed.")
        raise typer.Exit(1)


@app.command()
def init(project_name):
    """Run dbt build and store in DuckDB"""
    typer.echo("Initializing DBT Build of Tuva-Health in DuckDB")

    run_dbt_command(["dbt", "deps"])
    run_dbt_command(["dbt", "build"])
    run_dbt_command(["dbt", "docs", "generate"])


if __name__ == "__main__":
    app()
