from __future__ import annotations

from pathlib import Path


def read_text_file(file_path: str | Path) -> str:
    """Read the contents of a text file."""
    path = Path(file_path)
    return path.read_text(encoding="utf-8")


def write_text_file(file_path: str | Path, content: str) -> str:
    """Write content to a text file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)
