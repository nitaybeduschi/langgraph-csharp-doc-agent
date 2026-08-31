from __future__ import annotations

from typing import Any, cast

from .config import get_llm
from .prompts import build_documentation_prompt
from .schemas import CodeAnalysisResult, DocumentationOutput
from .security import SecurityError, sanitize_csharp_source
from .state import AgentState
from .tools import read_text_file, write_text_file

try:
    from tenacity import retry as tenacity_retry
    from tenacity import retry_if_exception_type, stop_after_attempt, wait_exponential
except Exception:
    tenacity_retry = None  # type: ignore[assignment]


def _model_dump(model: Any) -> dict[str, Any]:
    """Return a plain dict for Pydantic v1 or v2 models."""
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def load_source_file(state: AgentState) -> AgentState:
    """Load the source file contents into the shared state."""
    input_file = state.get("input_file")
    if not input_file:
        state["errors"] = ["No input file provided."]
        return state

    try:
        source_code = read_text_file(input_file, workspace_root=state.get("workspace_root"))
        state["source_code"] = source_code
        state["sanitized_source_code"] = sanitize_csharp_source(source_code)
    except FileNotFoundError:
        state["errors"] = [f"File not found: {input_file}"]
    except SecurityError as e:
        state["errors"] = [str(e)]
    return state


def analyze_code(state: AgentState) -> AgentState:
    """Placeholder analysis step for future implementation."""
    state["extracted_info"] = {"status": "stub", "summary": "Analysis not implemented yet."}
    return state


def analyze_code_full(state: AgentState) -> AgentState:
    """Best-effort analysis: extract class name and public methods from source.

    This is used in the graph flow to provide minimal structured information
    required by validation, while `analyze_code` remains a test-friendly stub.
    """
    source = state.get("source_code", "")
    info: dict[str, object] = {"status": "stub", "summary": "Analysis not implemented yet."}
    if source:
        # Best-effort extraction: class name and public methods
        import re

        class_match = re.search(r"class\s+(\w+)", source)
        methods = re.findall(r"public\s+[\w<>\[\]]+\s+(\w+)\s*\(", source)
        if class_match or methods:
            info = {
                "status": "ok",
                "class_name": class_match.group(1) if class_match else None,
                "methods": methods,
            }

    state["extracted_info"] = info
    return state


def start_parallel_analysis(state: AgentState) -> AgentState:
    """Pass-through node used to fan out parallel analysis branches."""
    return {}


def analyze_structure(state: AgentState) -> AgentState:
    """Extract structural code information in a parallel-safe state update."""
    source = state.get("source_code", "")
    class_name: str | None = None
    methods: list[str] = []
    dependencies: list[str] = []

    if source:
        import re

        class_match = re.search(r"class\s+(\w+)", source)
        class_name = class_match.group(1) if class_match else None
        methods = re.findall(r"public\s+[\w<>\[\]]+\s+(\w+)\s*\(", source)
        dependencies = re.findall(r"^\s*using\s+([\w.]+);", source, flags=re.MULTILINE)

    summary = "Extracted structural information from source code."
    if not class_name and not methods:
        summary = "No class name or public methods found in source code."

    result = CodeAnalysisResult(
        status="ok" if class_name or methods else "partial",
        summary=summary,
        class_name=class_name,
        methods=methods,
        dependencies=dependencies,
    )
    return {"structure_analysis": _model_dump(result)}


def audit_security_metrics(state: AgentState) -> AgentState:
    """Collect lightweight security and maintainability metrics in parallel."""
    source = state.get("source_code", "")
    lines = source.splitlines()
    lower_source = source.lower()
    risk_patterns = {
        "sql_execution": ["SqlCommand", "ExecuteSqlRaw", "FromSqlRaw"],
        "process_execution": ["Process.Start"],
        "file_deletion": ["File.Delete", "Directory.Delete"],
        "secret_literal": ["password", "secret", "token", "apikey", "api_key"],
    }

    detected_risks: list[str] = []
    for risk_name, patterns in risk_patterns.items():
        if any(pattern.lower() in lower_source for pattern in patterns):
            detected_risks.append(risk_name)

    metrics = {
        "line_count": len(lines),
        "non_empty_line_count": sum(1 for line in lines if line.strip()),
        "detected_risks": detected_risks,
        "risk_count": len(detected_risks),
    }

    result = CodeAnalysisResult(
        status="ok",
        summary="Collected lightweight security and maintainability metrics.",
        security_metrics=metrics,
    )
    return {"security_metrics": _model_dump(result)}


def merge_analyses(state: AgentState) -> AgentState:
    """Merge parallel analysis outputs into the canonical extracted_info key."""
    structure = CodeAnalysisResult(**cast(dict[str, Any], state.get("structure_analysis", {})))
    security = CodeAnalysisResult(**cast(dict[str, Any], state.get("security_metrics", {})))

    merged = CodeAnalysisResult(
        status="ok" if structure.class_name or structure.methods else "partial",
        summary=structure.summary,
        class_name=structure.class_name,
        methods=structure.methods,
        dependencies=structure.dependencies,
        security_metrics=security.security_metrics,
    )
    return {"extracted_info": _model_dump(merged)}


def _invoke_llm_once(llm: Any, system_msg: str, human_msg: str) -> str:
    """Invoke a LangChain-style LLM and return response content."""
    try:
        from langchain.schema import HumanMessage, SystemMessage

        messages = [SystemMessage(content=system_msg), HumanMessage(content=human_msg)]
        response = llm(messages)
        return getattr(response, "content", None) or str(response)
    except Exception:
        resp = llm(f"{system_msg}\n\n{human_msg}")
        return getattr(resp, "content", None) or str(resp)


if tenacity_retry is not None:
    _invoke_llm_with_retry = tenacity_retry(
        retry=retry_if_exception_type(Exception),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )(_invoke_llm_once)
else:
    _invoke_llm_with_retry = _invoke_llm_once


def generate_documentation(state: AgentState) -> AgentState:
    """Placeholder documentation generation step."""
    source_code = state.get("source_code", "")
    sanitized_source_code = state.get("sanitized_source_code") or sanitize_csharp_source(source_code)
    extracted = state.get("extracted_info")

    system_msg, human_msg = build_documentation_prompt(extracted, sanitized_source_code)

    # Try to obtain a LangChain LLM/chat model
    llm: Any = None
    try:
        llm = get_llm()
    except Exception as e:
        state.setdefault("errors", []).append(f"LLM factory failed: {e}")

    markdown: str | None = None

    if llm is not None:
        try:
            markdown = _invoke_llm_with_retry(llm, system_msg, human_msg)
        except Exception as e:
            state.setdefault("errors", []).append(f"LLM call failed: {e}")

    if not markdown:
        # Fallback: produce a simple markdown similar to previous behavior
        src_preview = source_code[:500]
        parts = [
            "# Documentation\n\n",
            "This document was generated from the provided source file.\n\n",
            "```csharp\n",
            src_preview,
            "\n```\n",
        ]

        if extracted and isinstance(extracted, dict):
            import json

            parts.extend(["\n## Extracted Info\n```", json.dumps(extracted, indent=2, ensure_ascii=False), "\n```\n"]) 

        parts.append("\n_Note: LLM unavailable or errored; this is a fallback._")
        markdown = "".join(parts)

    output = DocumentationOutput(markdown=markdown)
    dumped_output = _model_dump(output)
    state["documentation_output"] = dumped_output
    state["documentation"] = output.markdown
    return state


def export_markdown(state: AgentState) -> AgentState:
    """Write the generated documentation to disk."""
    output_file = state.get("output_file")
    documentation = state.get("documentation", "")
    if output_file and documentation:
        write_text_file(output_file, documentation, workspace_root=state.get("workspace_root"))
        state["output_file"] = output_file
    return state


def validate_analysis(state: AgentState) -> AgentState:
    """Check that analysis extracted minimal information required for docs.

    Requirements (best-effort):
    - `extracted_info` present
    - contains either a `class_name` or at least one `methods` entry

    On failure, populate `errors`.
    """
    extracted = state.get("extracted_info")
    errors: list[str] = []
    if not extracted:
        errors.append("No analysis information available.")
    else:
        # Best-effort checks for minimal structure
        has_class = bool(extracted.get("class_name") if isinstance(extracted, dict) else False)
        has_methods = bool(extracted.get("methods") if isinstance(extracted, dict) else False)
        if not has_class and not has_methods:
            errors.append("Insufficient analysis: missing class name and methods.")

    if errors:
        state["errors"] = errors

    return state


def finish_with_error(state: AgentState) -> AgentState:
    """Finalize a failed run without raising exceptions.

    Ensures `success` is False and provides a friendly message in `errors`.
    """
    state["success"] = False
    if "errors" not in state:
        state["errors"] = ["An unknown error occurred."]
    # Keep the state intact and return
    return state
