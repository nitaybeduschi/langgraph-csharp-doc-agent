"""Initial package for the C# documentation agent."""

from .config import DEFAULT_MODEL, PROJECT_ROOT
from .graph import build_graph

__all__ = ["build_graph", "DEFAULT_MODEL", "PROJECT_ROOT"]
