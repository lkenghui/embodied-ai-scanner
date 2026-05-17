import json
from typing import Any

from openai import OpenAI

from config import OPENAI_FAST_MODEL, OPENAI_REPORT_MODEL

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def generate_text(system_prompt: str, user_prompt: str, *, report: bool = False, max_output_tokens: int = 600) -> str:
    response = get_client().responses.create(
        model=OPENAI_REPORT_MODEL if report else OPENAI_FAST_MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_output_tokens=max_output_tokens,
    )
    return response.output_text.strip()


def generate_json(
    system_prompt: str,
    user_prompt: str,
    schema: dict[str, Any],
    *,
    name: str,
    max_output_tokens: int = 300,
) -> dict[str, Any]:
    response = get_client().responses.create(
        model=OPENAI_FAST_MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_output_tokens=max_output_tokens,
        text={
            "format": {
                "type": "json_schema",
                "name": name,
                "strict": True,
                "schema": schema,
            }
        },
    )
    return json.loads(response.output_text)
