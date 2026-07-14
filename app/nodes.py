from __future__ import annotations

from .state import AgentState
from .tools import read_text_file, write_text_file


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
