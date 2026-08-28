from __future__ import annotations

from fastapi.testclient import TestClient

from app.api import WebhookTriggerRequest, WebhookTriggerResponse, app, build_discord_payload


def test_build_discord_payload_contains_status_and_metrics() -> None:
    response = WebhookTriggerResponse(
        trace_id="trace-123",
        thread_id="thread-123",
        status="success",
        output_file="output/documentation.md",
        documentation_summary="# Documentation Sample",
        metrics={"method_count": 2, "risk_count": 0},
        notification_sent=True,
    )

    payload = build_discord_payload(response)

    embed = payload["embeds"][0]
    assert embed["title"] == "Documentation generation success"
    assert embed["description"] == "# Documentation Sample"
    assert {"name": "Methods", "value": "2", "inline": True} in embed["fields"]
    assert {"name": "Risks", "value": "0", "inline": True} in embed["fields"]


def test_trigger_documentation_endpoint_accepts_webhook_payload(monkeypatch) -> None:
    def fake_run_documentation_trigger(payload: WebhookTriggerRequest) -> WebhookTriggerResponse:
        return WebhookTriggerResponse(
            trace_id="trace-123",
            thread_id=payload.thread_id or "thread-123",
            status="success",
            output_file=payload.output_file,
            documentation_summary="Generated docs for SampleService.",
            metrics={"method_count": 2, "risk_count": 0},
            notification_sent=False,
        )

    monkeypatch.setattr("app.api.run_documentation_trigger", fake_run_documentation_trigger)
    client = TestClient(app)

    response = client.post(
        "/webhooks/documentation",
        json={
            "input_file": "examples/sample_service.cs",
            "output_file": "output/webhook-doc.md",
            "notify_discord": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["documentation_summary"] == "Generated docs for SampleService."
