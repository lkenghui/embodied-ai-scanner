import json
import re
from typing import Any

import anthropic

from config import ANTHROPIC_API_KEY, ANTHROPIC_FAST_MODEL, ANTHROPIC_REPORT_MODEL

_client = None


def get_client() -> anthropic.Anthropic:
    global _client
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured. Add it to .env to run AI analysis.")
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def _safe_str(text: str) -> str:
    """Strip non-ASCII characters to avoid encoding issues on servers with ASCII locale."""
    return text.encode("ascii", errors="ignore").decode("ascii")


def generate_text(system_prompt: str, user_prompt: str, *, report: bool = False, max_output_tokens: int = 600) -> str:
    model = ANTHROPIC_REPORT_MODEL if report else ANTHROPIC_FAST_MODEL
    message = get_client().messages.create(
        model=model,
        max_tokens=max_output_tokens,
        system=_safe_str(system_prompt),
        messages=[{"role": "user", "content": _safe_str(user_prompt)}],
    )
    return message.content[0].text.strip()


def generate_json(
    system_prompt: str,
    user_prompt: str,
    schema: dict[str, Any],
    *,
    name: str,
    max_output_tokens: int = 300,
) -> dict[str, Any]:
    enhanced_system = system_prompt + "\n\nYou MUST respond with valid JSON only. No explanation, no markdown fences, just raw JSON."
    response = generate_text(enhanced_system, user_prompt, max_output_tokens=max_output_tokens)
    response = response.strip()

    # Try direct parse first
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Strip markdown fences and retry
    response = re.sub(r"^```(?:json)?\s*", "", response)
    response = re.sub(r"\s*```$", "", response).strip()
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Extract first {...} block and retry
    match = re.search(r"\{.*\}", response, re.DOTALL)
    if match:
        return json.loads(match.group())

    print(f"[anthropic_client] generate_json failed to parse response for '{name}': {response[:200]}")
    raise ValueError(f"Could not parse JSON from response: {response[:200]}")
