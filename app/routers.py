from __future__ import annotations

from typing import Any

from .state import AgentState
from .tools import read_text_file
from pathlib import Path


def should_continue_after_file_validation(state: AgentState) -> str:
    """Router returning the next branch after file validation.

    Returns 'valid' when there are no errors and source_code exists, otherwise 'invalid'.
    """
    # If errors are already present, short-circuit
    if state.get("errors"):
        return "invalid"

    input_file = state.get("input_file")
    if not input_file:
        return "invalid"

    path = Path(input_file)
    if not path.exists():
        state["errors"] = [f"File not found: {input_file}"]
        return "invalid"
    if path.suffix.lower() != ".cs":
        state.setdefault("errors", []).append("Invalid file extension: expected .cs")
        return "invalid"

    # Ensure source_code is present for downstream nodes; read it here if needed
    if not state.get("source_code"):
        try:
            content = read_text_file(input_file)
        except FileNotFoundError:
            state["errors"] = [f"File not found: {input_file}"]
            return "invalid"
        if not content.strip():
            state["errors"] = ["Source file is empty."]
            return "invalid"
        state["source_code"] = content

    return "valid"


def should_continue_after_analysis(state: AgentState) -> str:
    """Router returning the next branch after analysis validation.

    Returns 'success' when analysis appears sufficient, otherwise 'failure'.
    """
    extracted = state.get("extracted_info")
    if not extracted or not isinstance(extracted, dict):
        return "failure"
    has_class = bool(extracted.get("class_name"))
    has_methods = bool(extracted.get("methods"))
    if has_class or has_methods:
        return "success"
    return "failure"
