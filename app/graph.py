from __future__ import annotations

from langgraph.graph import StateGraph, END

from .nodes import (
    analyze_code,
    export_markdown,
    generate_documentation,
    load_source_file,
    validate_analysis,
    finish_with_error,
)
from .routers import (
    should_continue_after_file_validation,
    should_continue_after_analysis,
)
from .state import AgentState


def build_graph() -> StateGraph:
    """Build the initial workflow for the documentation agent."""
    workflow = StateGraph(AgentState)

    workflow.add_node("load_source_file", load_source_file)
    from .nodes import analyze_code_full
    workflow.add_node("analyze_code", analyze_code_full)
    workflow.add_node("validate_analysis", validate_analysis)
    workflow.add_node("generate_documentation", generate_documentation)
    workflow.add_node("export_markdown", export_markdown)
    workflow.add_node("finish_with_error", finish_with_error)

    workflow.set_entry_point("load_source_file")
    # After loading, decide whether to continue based on lightweight router
    workflow.add_conditional_edges(
        "load_source_file",
        should_continue_after_file_validation,
        {"valid": "analyze_code", "invalid": "finish_with_error"},
    )
    # After analysis, validate analysis results and route accordingly
    workflow.add_edge("analyze_code", "validate_analysis")
    workflow.add_conditional_edges(
        "validate_analysis",
        should_continue_after_analysis,
        {"success": "generate_documentation", "failure": "finish_with_error"},
    )
    workflow.add_edge("generate_documentation", "export_markdown")
    workflow.add_edge("export_markdown", END)

    return workflow.compile()
