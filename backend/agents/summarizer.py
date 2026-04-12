import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a concise technology analyst specialising in embodied AI.
Summarise the given article or paper in 2-3 sentences for a non-technical executive audience.
Focus on: what was built or discovered, why it matters, and any company involved.
Be factual and avoid hype."""


def summarise(title: str, abstract: str) -> str:
    text = f"Title: {title}\n\nContent: {abstract[:2000]}"
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
    )
    return message.content[0].text.strip()
