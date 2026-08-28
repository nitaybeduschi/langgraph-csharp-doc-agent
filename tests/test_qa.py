from __future__ import annotations

from app.qa import review_code_quality
from app.state import AgentState


def test_review_code_quality_returns_static_suggestions(monkeypatch) -> None:
    monkeypatch.setattr("app.qa.get_llm", lambda: None)
    state: AgentState = {
        "source_code": (
            "public class SampleService { "
            'public void Run() { System.Diagnostics.Process.Start("cmd"); } }'
        ),
        "sanitized_source_code": "public class SampleService { }",
    }

    result = review_code_quality(state)

    suggestions = result["qa_review"]["static_suggestions"]
    assert any("interface" in suggestion for suggestion in suggestions)
    assert any("process execution" in suggestion.lower() for suggestion in suggestions)
