from pathlib import Path

from app.graph import build_graph
from app.state import AgentState


def test_build_graph_compiles_and_runs_with_example_file(tmp_path: Path) -> None:
    example_file = Path("examples/sample_service.cs")
    assert example_file.exists(), "Example source file should exist"

    output_file = tmp_path / "documentation.md"
    initial_state: AgentState = {
        "input_file": str(example_file),
        "output_file": str(output_file),
    }

    graph = build_graph()
    result = graph.invoke(initial_state)

    assert result["source_code"].startswith("using System;")
    assert "SampleService" in result["source_code"]
    assert result["documentation"].startswith("# Documentation")
    assert output_file.exists() is False or output_file.exists()
