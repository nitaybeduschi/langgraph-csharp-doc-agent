from __future__ import annotations

from typing import TypedDict


class AgentState(TypedDict, total=False):
    """Shared state for the documentation agent workflow."""

    input_file: str
    trace_id: str
    workspace_root: str
    source_code: str
    sanitized_source_code: str
    structure_analysis: dict[str, object]
    security_metrics: dict[str, object]
    extracted_info: dict[str, object]
    documentation_output: dict[str, object]
    documentation: str
    output_file: str
    # Whether the overall workflow succeeded. Optional to preserve compatibility.
    success: bool
    # List of error messages collected during execution.
    errors: list[str]
    # Non-fatal warnings that may be helpful to the user.
    warnings: list[str]
