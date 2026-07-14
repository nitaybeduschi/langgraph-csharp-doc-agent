from pathlib import Path

import pytest

from app.nodes import (
    analyze_code,
    export_markdown,
    generate_documentation,
    load_source_file,
)
from app.state import AgentState


@pytest.fixture
def sample_state() -> AgentState:
    return {"input_file": "examples/sample_service.cs"}


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


def test_generate_documentation_creates_markdown_content(sample_state: AgentState) -> None:
    state = load_source_file(sample_state)
    state = analyze_code(state)
    result = generate_documentation(state)

    assert result["documentation"].startswith("# Documentation")
    assert "provided source file" in result["documentation"]
    assert "SampleService" in result["documentation"]


def test_export_markdown_writes_output_file(tmp_path: Path, sample_state: AgentState) -> None:
    state = load_source_file(sample_state)
    state = analyze_code(state)
    state = generate_documentation(state)
    output_file = tmp_path / "generated.md"
    state["output_file"] = str(output_file)

    result = export_markdown(state)

    assert result["output_file"] == str(output_file)
    assert output_file.exists()
    assert "# Documentation" in output_file.read_text(encoding="utf-8")
