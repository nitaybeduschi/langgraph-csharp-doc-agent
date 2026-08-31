from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.graph import build_graph
from app.state import AgentState


class FakeLLM:
    def __call__(self, messages: object) -> SimpleNamespace:
        return SimpleNamespace(
            content=(
                "# Documentation\n\n"
                "Mocked documentation for SampleService generated without calling an external LLM."
            )
        )


def test_build_graph_compiles_and_runs_with_example_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.nodes.get_llm", lambda: FakeLLM())

    example_file = Path("examples/sample_service.cs")
    assert example_file.exists(), "Example source file should exist"

    output_file = Path(".tmp") / f"{uuid4().hex}-documentation.md"
    initial_state: AgentState = {
        "input_file": str(example_file),
        "output_file": str(output_file),
    }

    checkpoint_path = tmp_path / "checkpoints.db"
    graph = build_graph(checkpoint_path=checkpoint_path)
    config = {"configurable": {"thread_id": "demo-session"}}
    result = graph.invoke(
        initial_state,
        config=config,
    )

    assert result["source_code"].startswith("using System;")
    assert "SampleService" in result["source_code"]
    assert result["structure_analysis"]["class_name"] == "SampleService"
    assert result["security_metrics"]["security_metrics"]["risk_count"] == 0
    assert result["extracted_info"]["class_name"] == "SampleService"
    assert result["documentation"].startswith("# Documentation")
    assert output_file.exists() is False
    assert graph.get_state(config).next == ("export_markdown",)
    assert checkpoint_path.exists()

    resumed = graph.invoke(None, config=config)

    assert resumed["output_file"] == str(output_file)
    assert output_file.exists()


def test_build_graph_uses_checkpointer_for_threaded_runs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.nodes.get_llm", lambda: FakeLLM())

    example_file = Path("examples/sample_service.cs")
    output_file = tmp_path / "documentation.md"
    initial_state: AgentState = {
        "input_file": str(example_file),
        "output_file": str(output_file),
    }

    checkpoint_path = tmp_path / "checkpoints.db"
    graph = build_graph(checkpoint_path=checkpoint_path)
    assert graph.checkpointer is not None

    config = {"configurable": {"thread_id": "demo-session"}}
    result = graph.invoke(
        initial_state,
        config=config,
    )

    assert result["documentation"].startswith("# Documentation")
    assert checkpoint_path.exists()
    assert graph.get_state(config).values["documentation"].startswith("# Documentation")


def test_build_graph_can_include_optional_qa_review(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.nodes.get_llm", lambda: FakeLLM())
    monkeypatch.setattr("app.qa.get_llm", lambda: None)

    output_file = Path(".tmp") / f"{uuid4().hex}-documentation.md"
    initial_state: AgentState = {
        "input_file": "examples/sample_service.cs",
        "output_file": str(output_file),
    }

    graph = build_graph(checkpoint_path=tmp_path / "checkpoints.db", include_qa_review=True)
    result = graph.invoke(initial_state, config={"configurable": {"thread_id": "qa-session"}})

    assert "qa_review" in result
    assert result["qa_review"]["static_suggestions"]
    assert result["documentation"].startswith("# Documentation")
