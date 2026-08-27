from __future__ import annotations

import argparse
import uuid

from .graph import build_graph
from .state import AgentState


def main() -> None:
    """Run the initial LangGraph workflow for a C# source file."""
    parser = argparse.ArgumentParser(description="Generate Markdown docs for a C# source file")
    parser.add_argument("input_file", help="Path to the C# source file")
    parser.add_argument("--output", default="output/documentation.md", help="Path for the generated Markdown file")
    parser.add_argument("--thread-id", default=None, help="Thread ID used to persist and resume graph state")
    parser.add_argument("--approve-export", action="store_true", help="Resume a paused run and write Markdown to disk")
    args = parser.parse_args()

    thread_id = args.thread_id or f"doc-agent-{uuid.uuid4()}"
    initial_state: AgentState = {
        "input_file": args.input_file,
        "output_file": args.output,
    }

    graph = build_graph()
    config = {"configurable": {"thread_id": thread_id}}
    graph_input = None if args.approve_export else initial_state
    result = graph.invoke(graph_input, config=config)
    if graph.get_state(config).next:
        print(f"Execution paused before export_markdown. Review output, then resume with --thread-id {thread_id} --approve-export.")
    print(result)


if __name__ == "__main__":
    main()
