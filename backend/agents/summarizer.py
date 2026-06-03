from backend.agents.anthropic_client import generate_text

SYSTEM_PROMPT = """You are a concise technology analyst specialising in embodied AI.
Summarise the given article or paper in 2-3 sentences for a non-technical executive audience.
Focus on: what was built or discovered, why it matters, and any company involved.
Be factual and avoid hype."""


def summarise(title: str, abstract: str) -> str:
    text = f"Title: {title}\n\nContent: {abstract[:2000]}"
    return generate_text(SYSTEM_PROMPT, text, max_output_tokens=250)
