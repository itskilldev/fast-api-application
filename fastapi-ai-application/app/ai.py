"""AI integration.

Uses the Anthropic Messages API when ANTHROPIC_API_KEY is set. Otherwise it falls back to a
simple local extractive summarizer so the app (and tests) work without any API key.
"""
import re

import httpx

from .config import settings

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


def _local_summary(text: str, max_sentences: int = 2) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(sentences[:max_sentences])


def summarize(text: str) -> tuple[str, str]:
    """Return (summary, provider)."""
    if not settings.anthropic_api_key:
        return _local_summary(text), "local-fallback"

    try:
        response = httpx.post(
            ANTHROPIC_URL,
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.ai_model,
                "max_tokens": 300,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Summarize the following note in 2-3 concise sentences:\n\n{text}",
                    }
                ],
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"].strip(), "anthropic"
    except (httpx.HTTPError, KeyError, IndexError):
        # Never fail the request because the AI provider is down.
        return _local_summary(text), "local-fallback"
