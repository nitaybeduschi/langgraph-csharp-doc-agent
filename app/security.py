from __future__ import annotations

import re
from pathlib import Path

from .config import PROJECT_ROOT


class SecurityError(ValueError):
    """Raised when an input fails a security boundary check."""


PROMPT_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+instructions?\b"),
    re.compile(r"(?i)\b(disregard|forget)\s+(all\s+)?(previous|prior|above)\s+instructions?\b"),
    re.compile(r"(?i)\b(system|developer|assistant|user)\s*:\s*"),
    re.compile(r"<\|/?(?:system|user|assistant|developer|end)[^>]*\|>", re.IGNORECASE),
)

FENCE_PATTERN = re.compile(r"```+")


def workspace_root(root: str | Path | None = None) -> Path:
    """Return the resolved workspace root used for path validation."""
    return Path(root or PROJECT_ROOT).resolve()


def validate_workspace_path(
    file_path: str | Path,
    *,
    root: str | Path | None = None,
    must_exist: bool = False,
) -> Path:
    """Resolve a path and ensure it stays inside the configured workspace."""
    base = workspace_root(root)
    resolved = Path(file_path).expanduser().resolve()

    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise SecurityError(f"Path escapes workspace: {file_path}") from exc

    if must_exist and not resolved.exists():
        raise FileNotFoundError(str(file_path))

    return resolved


def sanitize_csharp_source(source_code: str) -> str:
    """Neutralize prompt-control text embedded in untrusted C# source."""
    sanitized = FENCE_PATTERN.sub("` ` `", source_code)
    for pattern in PROMPT_INJECTION_PATTERNS:
        sanitized = pattern.sub("[neutralized prompt directive]", sanitized)
    return sanitized
