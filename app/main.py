from __future__ import annotations

import argparse

from .graph import build_graph
from .state import AgentState


def main() -> None:
    """Run the initial LangGraph workflow for a C# source file."""
    parser = argparse.ArgumentParser(description="Generate Markdown docs for a C# source file")
    parser.add_argument("input_file", help="Path to the C# source file")
    parser.add_argument("--output", default="output/documentation.md", help="Path for the generated Markdown file")
    args = parser.parse_args()

    initial_state: AgentState = {
        "input_file": args.input_file,
        "output_file": args.output,
    }

    graph = build_graph()
    config = {"configurable": {"thread_id": "demo-session"}}
    result = graph.invoke(initial_state, config=config)
    print(result)


if __name__ == "__main__":
    main()
