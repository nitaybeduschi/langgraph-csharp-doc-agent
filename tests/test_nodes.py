from pathlib import Path
from types import SimpleNamespace

import pytest

from app.nodes import (
    analyze_code,
    analyze_structure,
    audit_security_metrics,
    export_markdown,
    generate_documentation,
    load_source_file,
    merge_analyses,
)
from app.schemas import CodeAnalysisResult, DocumentationOutput
from app.state import AgentState


@pytest.fixture
def sample_state() -> AgentState:
    return {"input_file": "examples/sample_service.cs"}


class FakeLLM:
    def __call__(self, messages: object) -> SimpleNamespace:
        return SimpleNamespace(
            content="# Documentation\n\nMocked documentation for SampleService generated without calling an external LLM."
        )


def test_load_source_file_reads_existing_file(sample_state: AgentState) -> None:
    state = load_source_file(sample_state)

    assert state["source_code"].startswith("using System;")
    assert "class SampleService" in state["source_code"]
    assert "errors" not in state


def test_load_source_file_returns_error_for_missing_file() -> None:
    state: AgentState = {"input_file": "examples/does_not_exist.cs"}

    result = load_source_file(state)

    assert result["errors"] == ["File not found: examples/does_not_exist.cs"]


def test_analyze_code_sets_stub_information(sample_state: AgentState) -> None:
    state = load_source_file(sample_state)
    result = analyze_code(state)

    assert result["extracted_info"] == {
        "status": "stub",
        "summary": "Analysis not implemented yet.",
    }


def test_parallel_analysis_nodes_return_validated_partial_updates(sample_state: AgentState) -> None:
    state = load_source_file(sample_state)

    structure = analyze_structure(state)
    security = audit_security_metrics(state)

    structure_result = CodeAnalysisResult(**structure["structure_analysis"])
    security_result = CodeAnalysisResult(**security["security_metrics"])

    assert structure_result.class_name == "SampleService"
    assert structure_result.methods == ["GetGreeting", "Add"]
    assert security_result.security_metrics["line_count"] > 0
    assert "source_code" not in structure
    assert "source_code" not in security


def test_merge_analyses_creates_code_analysis_result(sample_state: AgentState) -> None:
    state = load_source_file(sample_state)
    state.update(analyze_structure(state))
    state.update(audit_security_metrics(state))

    result = merge_analyses(state)
    analysis = CodeAnalysisResult(**result["extracted_info"])

    assert analysis.class_name == "SampleService"
    assert analysis.methods == ["GetGreeting", "Add"]
    assert analysis.security_metrics["risk_count"] == 0


def test_generate_documentation_creates_markdown_content(
    monkeypatch: pytest.MonkeyPatch, sample_state: AgentState
) -> None:
    monkeypatch.setattr("app.nodes.get_llm", lambda: FakeLLM())

    state = load_source_file(sample_state)
    state = analyze_code(state)
    result = generate_documentation(state)
    documentation_output = DocumentationOutput(**result["documentation_output"])

    assert result["documentation"].startswith("# Documentation")
    assert documentation_output.markdown == result["documentation"]
    assert "Mocked documentation" in result["documentation"]
    assert "SampleService" in result["documentation"]


def test_export_markdown_writes_output_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, sample_state: AgentState
) -> None:
    monkeypatch.setattr("app.nodes.get_llm", lambda: FakeLLM())

    state = load_source_file(sample_state)
    state = analyze_code(state)
    state = generate_documentation(state)
    output_file = tmp_path / "generated.md"
    state["output_file"] = str(output_file)

    result = export_markdown(state)

    assert result["output_file"] == str(output_file)
    assert output_file.exists()
    assert "# Documentation" in output_file.read_text(encoding="utf-8")
