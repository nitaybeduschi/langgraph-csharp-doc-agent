from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGSMITH_TRACING", "true")


def _extract_prompt_text(prompt_input: Any) -> str:
    if isinstance(prompt_input, str):
        return prompt_input
    if isinstance(prompt_input, dict) and "content" in prompt_input:
        return str(prompt_input["content"])
    if isinstance(prompt_input, (list, tuple)):
        parts: list[str] = []
        for item in prompt_input:
            if hasattr(item, "content"):
                parts.append(str(item.content))
            elif isinstance(item, dict) and "content" in item:
                parts.append(str(item["content"]))
            else:
                parts.append(str(item))
        return "\n\n".join(parts)
    return str(prompt_input)


def _extract_gemini_text(response: Any) -> str:
    if not isinstance(response, dict):
        return "" if response is None else str(response)

    texts: list[str] = []
    for candidate in response.get("candidates", []):
        parts = candidate.get("content", {}).get("parts", [])
        texts.extend(str(part["text"]) for part in parts if isinstance(part, dict) and "text" in part)

    return "\n\n".join(texts)


class GeminiApiLLM:
    """Small Gemini adapter compatible with the app's LangChain-like call style."""

    def __init__(self, model: str, api_key: str) -> None:
        self.model = model
        self.api_key = api_key

    def __call__(self, prompt_input: Any, **kwargs: Any) -> Any:
        prompt_text = _extract_prompt_text(prompt_input)
        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{quote(self.model, safe='')}:generateContent?key={quote(self.api_key, safe='')}"
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt_text}]}],
            "generationConfig": {
                "temperature": float(os.getenv("LLM_TEMPERATURE", "0.2")),
            },
        }
        request = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=60) as response:
                body = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Gemini API request failed ({exc.code}): {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"Gemini API request failed: {exc.reason}") from exc

        return SimpleNamespace(content=_extract_gemini_text(json.loads(body)))


GeminiVertexLLM = GeminiApiLLM


def _get_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _default_model() -> str:
    return _get_env("GEMINI_MODEL", "OPENAI_MODEL") or "gemini-3.5-flash"

# Attempt to load environment variables from a local .env file if python-dotenv
# is available. This keeps the behavior optional so the project doesn't require
# an extra dependency at runtime.
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None  # type: ignore

if load_dotenv is not None:
    env_path = PROJECT_ROOT / ".env"
    try:
        # Prefer an explicit .env at the project root when present
        if env_path.exists():
            load_dotenv(dotenv_path=str(env_path))
        else:
            load_dotenv()
    except Exception:
        # If loading fails, continue without raising
        pass

DEFAULT_MODEL = _default_model()
OPENAI_API_KEY = _get_env("OPENAI_API_KEY")
GOOGLE_API_KEY = _get_env("GOOGLE_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY")


def get_api_key() -> str:
    """Return the configured API key."""
    return GOOGLE_API_KEY if "gemini" in DEFAULT_MODEL.lower() else OPENAI_API_KEY


def get_llm() -> Any:
    """Factory to return a LangChain LLM/chat model instance.

    The application must only call this function and never instantiate
    provider-specific models directly. If no provider is available this
    returns None so callers can fallback gracefully.
    """
    api_key = get_api_key()

    # Allow explicit provider selection or infer from the model name
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()
    if not provider and "gemini" in (DEFAULT_MODEL or "").lower():
        provider = "gemini"

    # --- Gemini / Google ---
    if provider == "gemini":
        if not api_key:
            raise ValueError("Missing Gemini API key. Set GOOGLE_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY in .env.")
        return GeminiApiLLM(model=DEFAULT_MODEL, api_key=api_key)

    # Import inside function to avoid hard dependency at module import time
    try:
        from langchain.chat_models import ChatOpenAI  # type: ignore[attr-defined]
    except Exception:
        ChatOpenAI = None

    if ChatOpenAI is not None:
        try:
            kwargs = {}
            if api_key:
                kwargs["openai_api_key"] = api_key
            return ChatOpenAI(model=DEFAULT_MODEL, **kwargs)
        except Exception:
            # Fall through to other options
            pass

    # Try older/OpenAI LLM wrapper as a fallback
    try:
        from langchain.llms import OpenAI

        kwargs = {}
        if api_key:
            kwargs["openai_api_key"] = api_key
        return OpenAI(model_name=DEFAULT_MODEL, **kwargs)
    except Exception:
        return None
