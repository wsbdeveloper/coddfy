"""
Helpers para armazenamento local dos arquivos enviados.
"""
import os
import shutil
from pathlib import Path
from typing import Optional
from uuid import uuid4

STORAGE_DIR = Path(os.getenv('TIMESHEET_STORAGE_PATH', 'storage/timesheets'))


def ensure_storage_dir() -> Path:
    """Garante que o diretório de armazenamento exista."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"STORAGE_DIR: {STORAGE_DIR}")
    return STORAGE_DIR


def _sanitize_suffix(filename: Optional[str]) -> str:
    if not filename:
        return ''
    name = Path(filename).name
    return Path(name).suffix


def save_timesheet_file(file_field) -> str:
    """
    Persiste o arquivo no disco e retorna o nome relativo usado no registro.
    """
    storage = ensure_storage_dir()
    suffix = _sanitize_suffix(file_field.filename if hasattr(file_field, 'filename') else None)
    target = storage / f"{uuid4().hex}{suffix}"
    file_field.file.seek(0)
    with open(target, 'wb') as dest:
        shutil.copyfileobj(file_field.file, dest)
    return target.name


def get_timesheet_file_path(filename: str) -> Path:
    """
    Constrói o caminho absoluto para um arquivo salvo.
    """
    storage = ensure_storage_dir()
    return storage / filename

