from __future__ import annotations

from .state import AgentState
from .tools import read_text_file, write_text_file
from pathlib import Path


def load_source_file(state: AgentState) -> AgentState:
    """Load the source file contents into the shared state."""
    input_file = state.get("input_file")
    if not input_file:
        state["errors"] = ["No input file provided."]
        return state

    try:
        state["source_code"] = read_text_file(input_file)
    except FileNotFoundError:
        state["errors"] = [f"File not found: {input_file}"]
    return state


def analyze_code(state: AgentState) -> AgentState:
    """Placeholder analysis step for future implementation."""
    state["extracted_info"] = {"status": "stub", "summary": "Analysis not implemented yet."}
    return state


def analyze_code_full(state: AgentState) -> AgentState:
    """Best-effort analysis: extract class name and public methods from source.

    This is used in the graph flow to provide minimal structured information
    required by validation, while `analyze_code` remains a test-friendly stub.
    """
    source = state.get("source_code", "")
    info: dict[str, object] = {"status": "stub", "summary": "Analysis not implemented yet."}
    if source:
        # Best-effort extraction: class name and public methods
        import re

        class_match = re.search(r"class\s+(\w+)", source)
        methods = re.findall(r"public\s+[\w<>\[\]]+\s+(\w+)\s*\(", source)
        if class_match or methods:
            info = {
                "status": "ok",
                "class_name": class_match.group(1) if class_match else None,
                "methods": methods,
            }

    state["extracted_info"] = info
    return state


def generate_documentation(state: AgentState) -> AgentState:
    """Placeholder documentation generation step."""
    source_code = state.get("source_code", "")
    state["documentation"] = (
        "# Documentation\n\n"
        f"This document was generated from the provided source file.\n\n```csharp\n{source_code[:500]}\n```"
    )
    return state


def export_markdown(state: AgentState) -> AgentState:
    """Write the generated documentation to disk."""
    output_file = state.get("output_file")
    documentation = state.get("documentation", "")
    if output_file and documentation:
        write_text_file(output_file, documentation)
        state["output_file"] = output_file
    return state


def validate_analysis(state: AgentState) -> AgentState:
    """Check that analysis extracted minimal information required for docs.

    Requirements (best-effort):
    - `extracted_info` present
    - contains either a `class_name` or at least one `methods` entry

    On failure, populate `errors`.
    """
    extracted = state.get("extracted_info")
    errors: list[str] = []
    if not extracted:
        errors.append("No analysis information available.")
    else:
        # Best-effort checks for minimal structure
        has_class = bool(extracted.get("class_name") if isinstance(extracted, dict) else False)
        has_methods = bool(extracted.get("methods") if isinstance(extracted, dict) else False)
        if not has_class and not has_methods:
            errors.append("Insufficient analysis: missing class name and methods.")

    if errors:
        state["errors"] = errors

    return state


def finish_with_error(state: AgentState) -> AgentState:
    """Finalize a failed run without raising exceptions.

    Ensures `success` is False and provides a friendly message in `errors`.
    """
    state["success"] = False
    if "errors" not in state:
        state["errors"] = ["An unknown error occurred."]
    # Keep the state intact and return
    return state
