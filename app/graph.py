from __future__ import annotations

import sqlite3
from pathlib import Path

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from .nodes import (
    analyze_structure,
    audit_security_metrics,
    export_markdown,
    generate_documentation,
    load_source_file,
    merge_analyses,
    start_parallel_analysis,
    validate_analysis,
    finish_with_error,
)
from .routers import (
    should_continue_after_file_validation,
    should_continue_after_analysis,
)
from .state import AgentState


def build_graph(checkpoint_path: str | Path = "checkpoints.db") -> StateGraph:
    """Build the initial workflow for the documentation agent."""
    workflow = StateGraph(AgentState)

    workflow.add_node("load_source_file", load_source_file)
    workflow.add_node("start_parallel_analysis", start_parallel_analysis)
    workflow.add_node("analyze_structure", analyze_structure)
    workflow.add_node("audit_security_metrics", audit_security_metrics)
    workflow.add_node("merge_analyses", merge_analyses)
    workflow.add_node("validate_analysis", validate_analysis)
    workflow.add_node("generate_documentation", generate_documentation)
    workflow.add_node("export_markdown", export_markdown)
    workflow.add_node("finish_with_error", finish_with_error)

    workflow.set_entry_point("load_source_file")
    # After loading, decide whether to continue based on lightweight router
    workflow.add_conditional_edges(
        "load_source_file",
        should_continue_after_file_validation,
        {
            "valid": "start_parallel_analysis",
            "invalid": "finish_with_error",
        },
    )
    # Run independent analysis nodes in parallel, then join their results.
    workflow.add_edge("start_parallel_analysis", "analyze_structure")
    workflow.add_edge("start_parallel_analysis", "audit_security_metrics")
    workflow.add_edge(["analyze_structure", "audit_security_metrics"], "merge_analyses")
    workflow.add_edge("merge_analyses", "validate_analysis")
    workflow.add_conditional_edges(
        "validate_analysis",
        should_continue_after_analysis,
        {"success": "generate_documentation", "failure": "finish_with_error"},
    )
    workflow.add_edge("generate_documentation", "export_markdown")
    workflow.add_edge("export_markdown", END)

    checkpoint_connection = sqlite3.connect(checkpoint_path, check_same_thread=False)
    sqlite_saver = SqliteSaver(checkpoint_connection)
    return workflow.compile(
        checkpointer=sqlite_saver,
        interrupt_before=["export_markdown"],
    )
