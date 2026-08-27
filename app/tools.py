from __future__ import annotations

from pathlib import Path

from langchain_core.tools import tool

from .schemas import ReadTextFileInput, WriteTextFileInput


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


@tool("read_text_file", args_schema=ReadTextFileInput)
def read_text_file_tool(file_path: str) -> str:
    """Read a UTF-8 text file from disk and return its contents."""
    return read_text_file(file_path)


@tool("write_text_file", args_schema=WriteTextFileInput)
def write_text_file_tool(file_path: str, content: str) -> str:
    """Write UTF-8 text content to disk and return the written file path."""
    return write_text_file(file_path, content)
