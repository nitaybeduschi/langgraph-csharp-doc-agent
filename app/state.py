from __future__ import annotations

from typing import TypedDict


class AgentState(TypedDict, total=False):
    """Shared state for the documentation agent workflow."""

    input_file: str
    source_code: str
    extracted_info: dict[str, object]
    documentation: str
    output_file: str
    errors: list[str]
