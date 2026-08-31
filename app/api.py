from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import PROJECT_ROOT
from .graph import build_graph
from .logging_config import configure_logging, set_trace_id
from .state import AgentState

app = FastAPI(title="LangGraph C# Documentation Agent")


class WebhookTriggerRequest(BaseModel):
    """Payload accepted by low-code tools and GitHub Actions."""

    input_file: str = Field(..., description="Workspace-relative path to the C# source file.")
    output_file: str = Field(default="output/documentation.md", description="Workspace-relative Markdown output path.")
    thread_id: str | None = Field(default=None, description="Optional LangGraph checkpoint thread id.")
    include_qa_review: bool = Field(default=False, description="Enable optional C# QA review node.")
    notify_discord: bool = Field(default=True, description="Send a Discord webhook notification after completion.")
    discord_webhook_url: str | None = Field(default=None, description="Discord webhook URL. Defaults to env var.")


class WebhookTriggerResponse(BaseModel):
    trace_id: str
    thread_id: str
    status: str
    output_file: str
    documentation_summary: str
    metrics: dict[str, Any]
    notification_sent: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def _documentation_summary(markdown: str, limit: int = 500) -> str:
    cleaned = " ".join(markdown.split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 3]}..."


def _extract_metrics(result: AgentState) -> dict[str, Any]:
    extracted = result.get("extracted_info") or {}
    security_metrics = extracted.get("security_metrics", {}) if isinstance(extracted, dict) else {}
    methods = extracted.get("methods", []) if isinstance(extracted, dict) else []
    dependencies = extracted.get("dependencies", []) if isinstance(extracted, dict) else []
    return {
        "class_name": extracted.get("class_name") if isinstance(extracted, dict) else None,
        "method_count": len(methods) if isinstance(methods, list) else 0,
        "dependency_count": len(dependencies) if isinstance(dependencies, list) else 0,
        "line_count": security_metrics.get("line_count", 0) if isinstance(security_metrics, dict) else 0,
        "risk_count": security_metrics.get("risk_count", 0) if isinstance(security_metrics, dict) else 0,
    }


def build_discord_payload(response: WebhookTriggerResponse) -> dict[str, Any]:
    color = 0x2ECC71 if response.status == "success" else 0xE74C3C
    return {
        "username": "C# Doc Agent",
        "embeds": [
            {
                "title": f"Documentation generation {response.status}",
                "description": response.documentation_summary or "No documentation summary available.",
                "color": color,
                "fields": [
                    {"name": "Trace ID", "value": response.trace_id, "inline": False},
                    {"name": "Output", "value": response.output_file, "inline": False},
                    {"name": "Methods", "value": str(response.metrics.get("method_count", 0)), "inline": True},
                    {"name": "Risks", "value": str(response.metrics.get("risk_count", 0)), "inline": True},
                ],
            }
        ],
    }


def send_discord_notification(webhook_url: str, response: WebhookTriggerResponse) -> bool:
    payload = build_discord_payload(response)
    request = Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "langgraph-csharp-doc-agent/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as discord_response:
            return 200 <= discord_response.status < 300
    except (HTTPError, URLError, TimeoutError):
        return False


def run_documentation_trigger(payload: WebhookTriggerRequest) -> WebhookTriggerResponse:
    configure_logging()
    trace_id = set_trace_id()
    thread_id = payload.thread_id or f"webhook-{uuid4()}"
    checkpoint_path = PROJECT_ROOT / ".tmp" / f"{thread_id}.db"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    initial_state: AgentState = {
        "input_file": payload.input_file,
        "output_file": payload.output_file,
        "trace_id": trace_id,
        "workspace_root": str(PROJECT_ROOT),
    }
    config = {"configurable": {"thread_id": thread_id}}
    graph = build_graph(checkpoint_path=checkpoint_path, include_qa_review=payload.include_qa_review)

    result = graph.invoke(initial_state, config=config)
    if graph.get_state(config).next:
        result = graph.invoke(None, config=config)

    errors = result.get("errors", [])
    documentation = result.get("documentation", "")
    status = "success" if documentation and not errors else "failure"
    response = WebhookTriggerResponse(
        trace_id=trace_id,
        thread_id=thread_id,
        status=status,
        output_file=str(Path(payload.output_file)),
        documentation_summary=_documentation_summary(documentation),
        metrics=_extract_metrics(result),
        notification_sent=False,
        errors=errors,
        warnings=result.get("warnings", []),
    )

    webhook_url = payload.discord_webhook_url or os.getenv("DISCORD_WEBHOOK_URL", "")
    if payload.notify_discord and webhook_url:
        response.notification_sent = send_discord_notification(webhook_url, response)

    return response


@app.post("/webhooks/documentation", response_model=WebhookTriggerResponse)
def trigger_documentation(payload: WebhookTriggerRequest) -> WebhookTriggerResponse:
    try:
        return run_documentation_trigger(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
