import subprocess
from config import _get_project_root

_PROJECT_ROOT = _get_project_root()
_DBT_PROJECT_ROOT = _PROJECT_ROOT/"dbt_projects"

def _clone_dbt_project(gitUrl: str) -> None:
    """Clones DBT project into _DBT_PROJECT_ROOT"""
    _DBT_PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    
    subprocess.run([
      "git", "clone",
      gitUrl
      ], cwd=_DBT_PROJECT_ROOT, check=True)


_clone_dbt_project("https://github.com/tuva-health/demo")