"""Ollama client. Runs entirely on the local machine - no API key, no data leaves the laptop."""

import httpx

from ..config import settings


def is_available() -> bool:
    try:
        r = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def installed_models() -> list[str]:
    try:
        r = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=5)
        return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []


def chat(system: str, user: str, temperature: float = 0.1, timeout: int = 180) -> str:
    """Single-turn chat completion. Raises on transport errors - callers decide the fallback."""
    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 320},
    }
    r = httpx.post(f"{settings.ollama_base_url}/api/chat", json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()["message"]["content"].strip()
