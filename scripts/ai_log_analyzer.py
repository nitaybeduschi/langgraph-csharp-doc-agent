from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.config import get_llm  # noqa: E402
from app.nodes import _invoke_llm_with_retry  # noqa: E402

ERROR_PATTERNS = (
    re.compile(r"\bFAILED\b", re.IGNORECASE),
    re.compile(r"\bERROR\b", re.IGNORECASE),
    re.compile(r"\bTraceback\b"),
    re.compile(r"\bModuleNotFoundError\b"),
    re.compile(r"\bAssertionError\b"),
)


def read_logs(log_dir: Path) -> dict[str, str]:
    logs: dict[str, str] = {}
    if not log_dir.exists():
        return logs
    for path in sorted(log_dir.glob("*.log")):
        logs[path.name] = path.read_text(encoding="utf-8", errors="replace")
    return logs


def calculate_risk_score(logs: dict[str, str]) -> int:
    combined = "\n".join(logs.values())
    score = 0
    score += min(40, sum(len(pattern.findall(combined)) for pattern in ERROR_PATTERNS) * 5)
    score += 20 if "mypy" in combined.lower() else 0
    score += 15 if "ruff" in combined.lower() else 0
    score += 15 if "pytest" in combined.lower() or "failed" in combined.lower() else 0
    score += 10 if "security" in combined.lower() or "injection" in combined.lower() else 0
    return min(score, 100)


def risk_level(score: int) -> str:
    if score >= 75:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def fallback_diagnosis(logs: dict[str, str]) -> str:
    if not logs:
        return "No CI log files were found for analysis."

    sections: list[str] = []
    for name, content in logs.items():
        relevant_lines = [
            line for line in content.splitlines() if any(pattern.search(line) for pattern in ERROR_PATTERNS)
        ][:10]
        if relevant_lines:
            sections.append(f"### {name}\n" + "\n".join(f"- `{line[:180]}`" for line in relevant_lines))
    return "\n\n".join(sections) or "The checks failed, but no common error pattern was detected in the captured logs."


def llm_diagnosis(logs: dict[str, str]) -> str:
    combined = "\n\n".join(f"## {name}\n{content[-6000:]}" for name, content in logs.items())
    if not combined.strip():
        return fallback_diagnosis(logs)

    prompt = (
        "Analyze these GitHub Actions logs. Explain the likely root cause, impacted checks, "
        "and recommended next steps in concise Markdown.\n\n"
        f"{combined[-12000:]}"
    )
    try:
        llm: Any = get_llm()
        if llm is None:
            return fallback_diagnosis(logs)
        return _invoke_llm_with_retry(llm, "You are a CI failure analysis assistant.", prompt)
    except Exception as exc:
        return f"{fallback_diagnosis(logs)}\n\nLLM diagnosis unavailable: `{exc}`"


def write_summary(markdown: str) -> None:
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with Path(summary_path).open("a", encoding="utf-8") as summary:
        summary.write(markdown)
        summary.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze CI failure logs and produce a risk summary.")
    parser.add_argument("--log-dir", default=".ci-logs", help="Directory containing captured CI log files.")
    parser.add_argument("--json-output", default="", help="Optional path for machine-readable analysis output.")
    args = parser.parse_args()

    logs = read_logs(Path(args.log_dir))
    score = calculate_risk_score(logs)
    level = risk_level(score)
    diagnosis = llm_diagnosis(logs)
    markdown = (
        "## AI CI Log Analysis\n\n"
        f"- Risk score: **{score}/100**\n"
        f"- Risk level: **{level}**\n\n"
        "### Diagnosis\n"
        f"{diagnosis}\n"
    )

    print(markdown)
    write_summary(markdown)

    if args.json_output:
        payload = {"risk_score": score, "risk_level": level, "diagnosis": diagnosis}
        Path(args.json_output).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
