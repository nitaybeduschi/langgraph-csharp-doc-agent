from __future__ import annotations

from langgraph.graph import StateGraph, END

from .nodes import analyze_code, export_markdown, generate_documentation, load_source_file
from .state import AgentState


def build_graph() -> StateGraph:
    """Build the initial workflow for the documentation agent."""
    workflow = StateGraph(AgentState)

    workflow.add_node("load_source_file", load_source_file)
    workflow.add_node("analyze_code", analyze_code)
    workflow.add_node("generate_documentation", generate_documentation)
    workflow.add_node("export_markdown", export_markdown)

    workflow.set_entry_point("load_source_file")
    workflow.add_edge("load_source_file", "analyze_code")
    workflow.add_edge("analyze_code", "generate_documentation")
    workflow.add_edge("generate_documentation", "export_markdown")
    workflow.add_edge("export_markdown", END)

    return workflow.compile()
