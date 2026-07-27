"""RAIP schemas package."""
from pathlib import Path

SCHEMAS_DIR = Path(__file__).parent

def get_schema_path(name: str) -> Path:
    return SCHEMAS_DIR / name
