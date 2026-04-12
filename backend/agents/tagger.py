import anthropic
import json
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

TOPICS = [
    "locomotion", "manipulation", "dexterous hands", "whole-body control",
    "sim-to-real", "world models", "vision-language-action", "reinforcement learning",
    "imitation learning", "humanoid", "legged robots", "autonomous navigation",
    "tactile sensing", "hardware", "investment/funding", "policy/regulation",
]

SYSTEM_PROMPT = f"""You are a technology analyst specialising in embodied AI.
Given an article title and abstract, return JSON with:
- "topics": list of 1-3 relevant topics from this list: {TOPICS}
- "significance": one of "high", "medium", "low"
  (high = breakthrough, major funding, new product launch;
   medium = incremental research, company update;
   low = minor news, opinion piece)

Respond with JSON only."""


def tag(title: str, abstract: str) -> tuple[list[str], str]:
    """Returns (topics, significance)."""
    text = f"Title: {title}\n\nAbstract: {abstract[:1500]}"
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
    )
    try:
        import re
        text = message.content[0].text
        text = re.sub(r"^```[a-z]*\n?", "", text.strip(), flags=re.MULTILINE)
        text = text.rstrip("`").strip()
        data = json.loads(text)
        topics = data.get("topics", [])
        significance = data.get("significance", "medium")
        return topics, significance
    except Exception:
        return [], "medium"
